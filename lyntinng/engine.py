#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: engine.py,v 1.26 2002/04/03 03:14:15 willhelm Exp $
#######################################################################
"""
This holds the Engine which both contains most of the other objects
that do work in lyntin as well as encapsulates the event
queue and the handler for it.

Most of your stuff should call functions in the engine to do things.
To get the instance of engine, look at myengine.

Engine also holds hooks to the various event types.  Events will call
all appropriate hooks allowing you to add functionality via the modules
interface without changing the Lyntin internals.

The engine module holds a variable which is a singleton: 'myengine'.
To access the engine, access it by 'engine.myengine'.

It also holds a series of helper functions for making common engine
calls easier to deal with.
"""
import Queue, traceback, copy, string, re, thread

import threadmanager, session, ui.ui, alias, lyntin, utils, event
import action, alias, gag, highlight, history, substitute, variable
import exported, hooks

"""
myengine is a singleton.  so when it gets instantiated, this
variable can be used to retrieve the engine singleton.
"""
myengine = None


class Engine:
  """
  This is the engine class.  There should be only one engine.
  """
  def __init__(self):
    """ Initializes the engine."""

    # this is the event queue that holds all the events in
    # the system.
    self._event_queue = Queue.Queue()

    # this is a lock for writing stuff to the ui--makes sure
    # we're not hosing things by having multiple things write
    # to the ui simultaneously....  ick.
    self._ui_lock = thread.allocate_lock()

    # this is the master shutdown flag for the event queue
    # handling.
    self._shutdownflag = 0

    # listeners exist at an engine level.  if you sign up for
    # an input hook, you get the input hook for ALL sessions.
    # this might change at some point....  we'll see.
    self._listeners = {}

    # the thread manager manages all the threads in the engine.
    # there is only one thread manager
    self._threadman = threadmanager.ThreadManager()

    # there is only one ui in the system.
    self._ui = None

    # current tick count
    self._tick = 0

    # counts the total number of events processed--for diagnostics
    self._num_events_processed = 0

    # our history manager
    self._historymanager = history.HistoryManager()

    # holds all the sessions
    self._sessions = {}

    # the current session.  points to a Session object.
    self._current_session = None

    # holds all the commands
    self._command_list = {}

    # we register ourselves with the shutdown hook
    hooks.shutdown_hook.register(self.shutdown)



  def initialize(self):
    """ Handles initialization that requires an engine object."""
    commonsession = session.Session()
    commonsession.setName("common")

    commonsession.setManager("action", action.ActionManager())
    commonsession.setManager("alias", alias.AliasManager())
    commonsession.setManager("gag", gag.GagManager())
    commonsession.setManager("highlight", highlight.HighlightManager())
    commonsession.setManager("substitute", substitute.SubstituteManager())
    commonsession.setManager("variable", variable.VariableManager())

    self._sessions["common"] = commonsession
    self._current_session = commonsession


  ### ------------------------------------------
  ### thread stuff
  ### ------------------------------------------

  def startthread(self, name, func):
    """ Starts a thread through the Thread Manager.

    arguments:

      'name' -- (string) name of the thread

      'func' -- (function) the function to run in the thread

    """
    self._threadman.startThread(name, func)

  def checkthreads(self):
    """
    Calls the Thread Manager checkthreads method which goes
    through and checks the status of all the threads registered
    with the Thread Manager.

    returns:

      (list of strings) of the thread status

    """
    return self._threadman.checkThreadsStatus()


  ### ------------------------------------------
  ### timer thread
  ### ------------------------------------------

  def runtimer(self):
    """
    This timer thread sleeps for a second, then calls everything
    in the queue with the current tick.

    Note: This will almost always be slightly behind and will
    get worse as there are more things that get executed each
    tick.
    """
    import time, event

    self._tick = 0
    while not self._shutdownflag:
      try:
        time.sleep(1)
        event.SpamEvent(hooks.timer_hook, (self._tick,)).enqueue()
        self._tick += 1
      except KeyboardInterrupt:
        return
      except SystemExit:
        return
      except:
        traceback.print_exc()

  def getCurrentTick(self):
    """
    Returns the current tick.  It also happens to be the total
    number of seconds since this instance of Lyntin was started.

    returns:

      (int) the current tick

    """
    return self._tick

 
  ### ------------------------------------------
  ### input/output stuff
  ### ------------------------------------------

  def handleUserData(self, input, internal=0, session=None):
    """ This handles input lines from the user in a session-less context.

    The engine.handleUserData deals with global stuff and then
    passes the modified input to the session for session-oriented
    handling.  The session can call this method again with
    expanded input--this method is considered recursive.

    internal tells whether to spam the input hook and
    things of that nature.

    arguments:

      'input' -- (string) data from the user

      'internal=0' -- (int) 1 if we should spam the input hook 
                      0 if we shouldn't

      'session=self._current_session' -- (session.Session instance)
                                         allows you to execute this
                                         and run all things in a
                                         specific session
    """ 
    inputlist = utils.split_commands(input)
    if session == None:
      session = self._current_session

    for mem in inputlist:
      # chomp it, replace \; -> ;, and strip leading/trailing whitespace
      mem = utils.chomp(mem).replace("\;", ";").strip()

      if len(mem) == 0:
        mem = lyntin.commandchar + "cr"

      # spam the hook with the raw input statement first...
      if internal:
        hooks.user_data_hook.spamhook((mem,))

      # FIXME - handle history stuff
      if mem[0] == "!":
        memhistory = self.getHistoryManager().getHistoryItem(mem)
        if memhistory != -1:
          self.handleUserData(memhistory)
          continue

      # if it starts with a # it's a loop, session or command.
      if len(mem) > 0 and mem[0] == lyntin.commandchar:
        # pull off the first token without the commandchar
        ses = mem.split(" ", 1)[0][1:]

        # is it a loop (aka repeating command)?
        if ses.isdigit():
          num = int(ses)
          if mem.find(" ") != -1:
            for i in range(num):
              self.handleUserData(mem.split(" ", 1)[1], internal)
          continue

        # is it a session?
        if self._sessions.has_key(ses):
          input = mem.split(" ", 1)
          if len(input) < 2:
            self._current_session = self._sessions[ses]
            exported.write_message(ses + " now current session.")
          else:
            self._sessions[ses].handleUserData(mem.split(" ", 1)[1], 
                                                     internal)
          continue

        # is it all sessions?
        if ses == "all":
          for mem in self._sessions.value():
            mem.handleUserData(mem.split(" ", 1)[1], internal)
          continue

      # no command char, so we pass it on to the mud
      session.handleUserData(mem, internal)


  def handleMudData(self, session, text):
    """ Handle input coming from the mud.

    We toss this to the current session to deal with.

    arguments:

      'session' -- (session) the session this mud data
                   applies to

      'text' -- (string) text coming from the mud

    """
    session.handleMudData(text)


  ### ------------------------------------------
  ### session stuff
  ### ------------------------------------------

  def createSession(self):
    """ Copies the common session and returns it.

    This does not register the session.

    returns:

      (session.Session)

    """
    ses = copy.copy(self._sessions["common"])
    return ses

  def isUniqueSessionName(self, name):
    """ Returns whether a session of that name already exists.

    arguments:

      'name' -- (string) the name to check

    returns:

      (int) 1 if it's unique, 0 if not

    """
    return not self._sessions.has_key(name)

  def registerSession(self, session, name):
    """ Registers a session with the engine.

    arguments:

      'session' -- (session.Session) the session to register

      'name' -- (string) the name of the session

    """
    if self._sessions.has_key(name):
      raise ValueError, "Session of that name already exists."
    self._sessions[name] = session

  def unregisterSession(self, name=""):
    """ Unregisters a session from the engine.

    arguments:

      'name=""' -- (string)

    """
    if not self._sessions.has_key(name):
      raise ValueError, "No session of that name."
    del self._sessions[name]
    self.changeSession()

  def currentSession(self):
    """ Returns the current session.

    returns:

      (session.Session) the current session object

    """
    return self._current_session

  def getSessions(self):
    """ Returns a list of session names.

    returns:

      (list of strings) the session names

    """
    return self._sessions.keys()

  def getSession(self, name):
    """ Returns a named session.

    arguments:

      'name' -- (string) the name of the session to retrieve

    returns:

      (session.Session) or None

    """
    if self._sessions.has_key(name):
      return self._sessions[name]
    else:
      return None

  def changeSession(self, name=''):
    """ Changes the current session to another named session.

    If they don't pass in a name, we get the next available
    non-common session if possible.

    arguments:

      'name=""' -- (string) the name of the session to switch
                   to

    """
    if name == '':
      keys = self._sessions.keys()
      keys.remove("common")
      if len(keys) == 0:
        self._current_session = self._sessions["common"]
      else:
        self._current_session = self._sessions[keys[0]]

    # if they pass in a name, we switch to that session.
    elif self._sessions.has_key(name):
      self._current_session = self._sessions[name]

    else:
      exported.write_error("No session of that name.")

  def writeSession(self, message):
    """ Writes a message to the socket.

    The message should be a string.  Otherwise, it's unhealthy.

    arguments:

      'message' -- (string) the text to write to the mud.

    """
    self._current_session.write(message)

  def closeSession(self, session=None):
    """ Closes down a session.

    arguments:

      'session=None' -- (string) the name of the session to
                        close

    returns:

      (int) 1 if successful, 0 if not

    """
    if session == None:
      session = self._current_session

    if session.getName() == "common":
      exported.write_error("Can't close the common session.")
      return 0
         
    session.shutdown(())
    return 1


  ### ------------------------------------------
  ### event-handling/engine stuff
  ### ------------------------------------------

  def dequeue(self):
    """ Pulls an event off the queue--will block!!!

    returns:

      (event.Event)

    """
    return self._event_queue.get()
         
  def enqueue(self, event):
    """ Adds an event to the queue.

    arguments:

      'event' -- (event.Event) the event to enqueue

    """
    self._event_queue.put(event)

  def runengine(self):
    """
    This gets kicked off in a thread and just keep going through
    events until it detects a shutdown.
    """
    while not self._shutdownflag:
      try:
        e = self.dequeue()
      except KeyboardInterrupt:
        return
      except SystemExit:
        return

      try:
        # print e, e.__dict__
        e.execute()
      except KeyboardInterrupt:
        self.tallyError()
        pass
      except SystemExit:
        pass
      except:
        self.tallyError()
        traceback.print_exc()
      self._num_events_processed += 1
        
  def tallyError(self):
    """ Adds one to the error count.

    If we see more than 20 errors, we shutdown.
    """
    lyntin.errorcount = lyntin.errorcount + 1
    hooks.error_occurred_hook.spamhook(lyntin.errorcount)
    if lyntin.errorcount > 20:
      hooks.too_many_errors_hook.spamhook()
      exported.write_error("Error count exceeded--shutting down.")
      event.ShutdownEvent().enqueue()


  def shutdown(self, args):
    """ Sets the shutdown status for the engine."""
    self._shutdownflag = 1

  def getDiagnostics(self):
    """
    Returns some basic diagnostic information in the form of a string.
    This allows a user to monitor how Lyntin is doing in terms
    of events and other such erata.

    returns:

      (string) the complete diagnostic data for our little happy
      mud client

    """
    data = ("   events processed: " + repr(self._num_events_processed) + "\n" +
            "   queue size: " + repr(self._event_queue.qsize()) + "\n" +
            "   ui: " + repr(self._ui) + "\n" + 
            "   thread manager: " + repr(self._threadman) + "\n" + 
            "   speedwalking: " + repr(lyntin.speedwalk) + "\n" +
            "   ansicolor: " + repr(lyntin.ansicolor) + "\n" +
            "   ticks: " + repr(self._tick) + "\n" +
            "   errors: " + repr(lyntin.errorcount) + "\n")


    # print info from each session
    data = (data + "Sessions:\n" + 
            "   total sessions: " + repr(len(self._sessions)) + "\n" +
            "   current session: " + self._current_session.getName() + "\n")

    for mem in self._sessions.values():
      # we do some fancy footwork here to make it print nicely
      data += '   ' + string.join(mem.getInfo().split('\n'), '\n   ') + "\n"


    # print info from all the hooks
    data = (data + "Hooks:\n" + 
            "   total hooks: " + 
            repr(len(self._listeners.keys())) + "\n")

    for mem in self._listeners.keys():
      data = (data + "   " + mem + ":\n")
      for mem2 in self._listeners[mem]:
        data = data + "      " + repr(mem2) + "\n"

    return data


  ### ------------------------------------------
  ### user interface stuff
  ### ------------------------------------------

  def setUI(self, thisui):
    """ Sets the ui.

    arguments:

      'thisui' -- (ui.BaseUI) the ui to set

    """
    self._ui = thisui

  def getUI(self):
    """ Returns the ui.

    returns:

      (ui.BaseUI)

    """
    return self._ui

  def writeUI(self, text):
    """ Writes a message to the ui.

    This method uses a lock so that multiple threads can write
    to the ui without intersecting and crashing the python process.

    arguments:

      'text' -- (string or ui.Message) the message to write 
                to the ui

    """
    if self._ui:
      self._ui_lock.acquire(1)
      self._ui.write(text)
      self._ui_lock.release()
    else:
      print "error: no ui\n" + repr(text)

  def writePrompt(self):
    """ Tells the ui to print a prompt."""
    if self._ui:
      self._ui.prompt()

  def flushUI(self):
    """ Tells the ui to flush its output."""
    self._ui.flush()


  ### ------------------------------------------------
  ### Command functions
  ### ------------------------------------------------

  def getCommands(self):
    """
    Returns a list of the commands we have registered.

    returns:

      (list of strings) all the commands that have been registered

    """
    return self._command_list.keys()

  def addCommand(self, name, func):
    """
    Registers a command.

    arguments:

      'name' -- (string) the command to add

      'func' -- (function) the function that handles it

    """
    if callable(func):
      self._command_list[name] = func
      return 1

    self.writeError(name + ' is uncallable.')

  def removeCommand(self, name):
    """
    Removes a command for whatever reasons.

    arguments:

      'name' -- (string) the name of the command to remove

    """
    try:    del self._command_list[name]
    except: pass

  def getCommand(self, name):
    """
    Returns the function for a given command name.

    arguments:

      'name' -- (string) the name of the command to retrieve

    returns:

      (function) the function in question or None

    """
    if self._command_list.has_key(name):
      return self._command_list[name]

    # this is kind of a kluge to handle the #@ arbitrary
    # python stuff so that it can be in its own module.
    if name[0] == "@" and self._command_list.has_key("@"):
      return self._command_list["@"]

    return None

  def getHistoryManager(self):
    """ Retrieves the history manager.

    returns:

      history.HistoryManager instance

    """
    return self._historymanager
