#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: engine.py,v 1.58 2002/06/21 02:34:21 willhelm Exp $
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
import Queue, traceback, copy, string, re, thread, inspect, sys

import session, ui.ui, lyntin, utils, event, argparser
import exported, hooks, helpmanager, history, threadmanager

"""
myengine is a singleton.  so when it gets instantiated, this
variable can be used to retrieve the engine singleton.
"""
myengine = None

class CommandData:
  """
  Holds data relating to a command.  It's a helper class.
  """
  def __init__(self):
    self._name = ""
    self._func = None
    self._argparser = None
    self._fqn = ""

  def __repr__(self): return self._name
  def __str__(self): return self._name

  def setName(self, name): self._name = name
  def getName(self): return self._name
  def setNameAdjusted(self, name): self._name_adjusted = name
  def getNameAdjusted(self): return self._name_adjusted
  def setFunc(self, func): self._func = func
  def getFunc(self): return self._func
  def setArgParser(self, ap): self._argparser = ap
  def getArgParser(self): return self._argparser
  def setFQN(self, fqn): self._fqn = fqn
  def getFQN(self): return self._fqn

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

    self._managers = {}

    # the thread manager manages all the threads in the engine.
    # there is only one thread manager
    self._managers["thread"] = threadmanager.ThreadManager()

    # the help manager manages all the help content in a hierarchical
    # structure.
    self._managers["help"] = helpmanager.HelpManager()

    # our history manager
    self._managers["history"] = history.HistoryManager()

    # there is only one ui in the system.
    self._ui = None

    # current tick count
    self._tick = 0

    # counts the total number of events processed--for diagnostics
    self._num_events_processed = 0

    # holds all the sessions
    self._sessions = {}

    # the current session.  points to a Session object.
    self._current_session = None

    # holds command name -> CommandData mappings
    self._commands = {}

    # we register ourselves with the shutdown hook
    hooks.shutdown_hook.register(self.shutdown)


  def initialize(self):
    """ Handles initialization that requires an engine object."""
    commonsession = session.Session()
    commonsession.setName("common")

    # this creates a "common" entry in all the managers that manage
    # session scoped data
    for mem in self._managers.values():
      mem.addSession(commonsession)

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
    self.getManager("thread").startThread(name, func)

  def checkthreads(self):
    """
    Calls the Thread Manager checkthreads method which goes
    through and checks the status of all the threads registered
    with the Thread Manager.

    returns:

      (list of strings) of the thread status

    """
    return self.getManager("thread").checkThreadsStatus()


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

  def handleUserData(self, input, internal=0, session=None ):
    """ This handles input lines from the user in a session-less context.

    The engine.handleUserData deals with global stuff and then
    passes the modified input to the session for session-oriented
    handling.  The session can call this method again with
    expanded input--this method is considered recursive.

    internal tells whether to spam the input hook and
    things of that nature.

    arguments:

      'input' -- (string) data from the user

      'internal=0' -- (int) 0 if we should spam the input hook
                      and record to history, 1 if we shouldn't

      'session=self._current_session' -- (session.Session instance)
                                         allows you to execute this
                                         and run all things in a
                                         specific session
    """ 
    inputlist = utils.split_commands(input)
    if session == None:
      session = self._current_session

    historyitems = []
    for mem in inputlist:
      mem = mem.strip()

      if len(mem) == 0:
        mem = lyntin.commandchar + "cr"

      # if it's not internal we spam the hook with the raw input
      if internal == 0:
        hooks.from_user_hook.spamhook((mem,))

      if mem[0] == "!":
        memhistory = self.getManager("history").getHistoryItem(mem)
        if memhistory != -1:
          self.handleUserData(memhistory, 1, session)
          historyitems.append(memhistory)
          continue

      #if we get here then it is not a valid !-expression.
      historyitems.append(mem)

      # if it starts with a # it's a loop, session or command
      if len(mem) > 0 and mem[0] == lyntin.commandchar:

        # pull off the first token without the commandchar
        ses = mem.split(" ", 1)[0][1:]

        # is it a loop (aka repeating command)?
        if ses.isdigit():
          num = int(ses)
          if mem.find(" ") != -1:
            for i in range(num):
              self.handleUserData(mem.split(" ", 1)[1], internal, session)
          continue

        # is it a session?
        if self._sessions.has_key(ses):
          input = mem.split(" ", 1)
          if len(input) < 2:
            self._current_session = self._sessions[ses]
            exported.write_message(ses + " now current session.")
          else:
            self._sessions[ses].handleUserData(mem.split(" ", 1)[1], 
                                                     internal )
          continue

        # is it "all" sessions?
        if ses == "all":
          newinput = mem.split(" ", 1)[1]
          for sessionname in self._sessions.keys():
            if sessionname != "common":
              self._sessions[sessionname].handleUserData(newinput, internal)
          continue

      # no command char, so we pass it on to the session.handleUserData
      # to do session oriented things
      session.handleUserData(mem, internal)

    # we don't record internal stuff or input that isn't supposed
    # to be echo'd
    if internal == 0 and lyntin.echo == 1:
      self.getManager("history").recordHistory(";".join(historyitems))


  def handleMudData(self, session, text):
    """ Handle input coming from the mud.

    We toss this to the current session to deal with.

    arguments:

      'session' -- (session) the session this mud data
                   applies to

      'text' -- (string) text coming from the mud

    """
    if session:
      session.handleMudData(text)
    else:
      exported.write_message("Unhandled data: %s" % text)


  ### ------------------------------------------
  ### session stuff
  ### ------------------------------------------

  def createSession(self, name):
    """ Copies the common session and returns it.

    arguments:

      'name' -- (string) the name of the session

    returns:

      (session.Session)

    """
    ses = session.Session()
    ses.setName(name)
    self.registerSession(ses, name)
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

    commonsession = self.getSession("common")
    for mem in self._managers.values():
      mem.addSession(session, commonsession)

    self._sessions[name] = session

  def unregisterSession(self, ses):
    """ Unregisters a session from the engine.

    arguments:

      'ses' -- (session instance)
    """
    if not self._sessions.has_key(ses.getName()):
      raise ValueError, "No session of that name."

    for mem in self._managers.values():
      try:
        mem.removeSession(ses)
      except Exception, e:
        exported.write_message("Exception with removing session %s." % e)

    del self._sessions[ses.getName()]

    if ses == self._current_session:
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

      # it's a little bit of finagling here to make sure
      # that the common session is the last one we would
      # switch to
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
    """ Writes a message to the network socket.

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
        e.execute()
      except KeyboardInterrupt:
        return
      except SystemExit:
        return
      except:
        self.tallyError()
        traceback.print_exc()
      self._num_events_processed += 1
        
  def tallyError(self):
    """ Adds one to the error count.

    If we see more than 20 errors, we shutdown.
    """
    lyntin.errorcount = lyntin.errorcount + 1
    exported.write_error("WARNING: Unhandled error encountered (%d out of %d)." 
                         % (lyntin.errorcount, 20))
    hooks.error_occurred_hook.spamhook((lyntin.errorcount,))
    if lyntin.errorcount > 20:
      hooks.too_many_errors_hook.spamhook()
      exported.write_error("Error count exceeded--shutting down.")
      sys.exit("Error count exceeded--shutting down.")


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
    data = []
    data.append("   events processed: %d" % self._num_events_processed)
    data.append("   queue size: %d" % self._event_queue.qsize())
    data.append("   ui: %s" % repr(self._ui))
    data.append("   thread manager: %s" % repr(self.getManager("thread")))
    data.append("   speedwalking: %d" % lyntin.speedwalk)
    data.append("   ansicolor: %d" % lyntin.ansicolor)
    data.append("   ticks: %d" % self._tick)
    data.append("   errors: %d" % lyntin.errorcount)

    # print info from each session
    data.append("Sessions:")
    data.append("   total sessions: %d" % len(self._sessions))
    data.append("   current session: %s" % self._current_session.getName())

    for mem in self._sessions.values():
      # we do some fancy footwork here to make it print nicely
      info = string.join(self.getStatus(mem), "\n   ")
      data.append('   %s\n' % info)

    return string.join(data, "\n")


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

    Theoretically you should use the exported module to write
    things to the ui--it calls this method.

    arguments:

      'text' -- (string or ui.Message) the message to write 
                to the ui
    """
    self._ui_lock.acquire(1)
    try:
      hooks.to_user_hook.spamhook((text,))
    finally:
      self._ui_lock.release()

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
    return self._commands.keys()

  def addCommand(self, name, func, arguments=None, argoptions=None, helptext=""):
    """
    Registers a command.

    arguments:

      'name' -- (string) the command to add

      'func' -- (function) the function that handles it

      'arguments=None' -- (string) argument specification to create 
                          the argparser

      'argoptions=None' -- (string) options for how the argument spec
                           should be parsed

      'helptext=""' -- (string) the help text for this command
      
    """
    if not callable(func):
      raise ValueError, "%s is uncallable." % name

    cd = CommandData()

    syntaxline = ""

    # try to figure out the arguments and syntax line stuff
    if arguments != None:
      try:
        cd.setName(name)
        cd.setArgParser(argparser.ArgumentParser(arguments, argoptions))
        syntaxline = cd.getArgParser().syntaxline
      except Exception, e:
        raise Exception, "Error with arguments for command %s, (%s)" % (name,e)

    # add the command to the command list
    cd.setFunc(func)

    # toss the command thing in the list
    self._commands[name] = cd

    # deal with the help text
    if not helptext:
      if func.__doc__:
        helptext = inspect.getdoc(func)
      else:
        helptext = "\nThis command has no help."

    if name[0] == "^":
      cd.setNameAdjusted(name[1:])
    else:
      cd.setNameAdjusted(name)

    if syntaxline:
      helptext = ("syntax: %s%s %s\n" % 
             (lyntin.commandchar, cd.getNameAdjusted(), syntaxline) + helptext)

    fqn = exported.add_help(cd.getNameAdjusted(), helptext)
    cd.setFQN(fqn)
        
  def removeCommand(self, name):
    """
    Removes a command (and the help text) for whatever reasons.

    arguments:

      'name' -- (string) the name of the command to remove

    """
    if self._commands.has_key(name):
      cd = self._commands[name]
      del self._commands[name]
      try:
        exported.remove_help(cd.getFQN())
      except:
        pass

  def getCommand(self, name):
    """
    Returns the function for a given command name.

    arguments:

      'name' -- (string) the name of the command to retrieve

    returns:

      (function) the function in question or None

    """
    if self._commands.has_key(name):
      return self._commands[name].getFunc()

    if self._commands.has_key("^" + name):
      return self._commands["^" + name].getFunc()

    # this is kind of a kluge to handle the #@ arbitrary
    # python stuff so that it can be in its own module.
    if name[0] == "@" and self._commands.has_key("@"):
      return self._commands["@"].getFunc()

    return None

  def getArgParser(self, name):
    """
    Returns the arguments parser for a given command name.

    arguments:

      'name' -- (string) the name of the command whose arguments should 
                be retrieved

    returns:

      (ArgParser) -- argument parsing object with parse(string) command 
                      to convert incoming arguments into a dictionary
      
    """
    if self._commands.has_key(name):
      return self._commands[name].getArgParser()

    return None

  
  ### ------------------------------------------------
  ### Manager functions
  ### ------------------------------------------------

  def addManager(self, name, mgr):
    """ Adds a manager to our list.

    arguments:

      'name' -- (string) the name of the manager to add.

      'manager' -- (instance) the manager to add.
    """
    self._managers[name] = mgr

  def removeManager(self, name):
    """ Removes a manager from our list.

    arguments:

      'name' -- (string) the name of the manager to remove.
    """
    if self._managers.has_key(name):
      del self._managers[name]

  def getManager(self, name):
    """ Retrieves a manager by name.

    arguments:

      'name' -- (string) the name of the manager to retrieve.

    returns:

      the manager instance
    """
    if self._managers.has_key(name):
      return self._managers[name]
    return None

  ### ------------------------------------------------
  ### Status stuff
  ### ------------------------------------------------
  def getStatus(self, ses):
    """ Gets the status for a specific session.

    arguments:

      'ses' -- (session instance) the session to get status for.
    """
    data = []
    # call session.getStatus() and get status from it too
    temp = ses.getStatus()

    for mem in temp:
      data.append(mem)

    # loop through our managers and get status from them
    managerkeys = self._managers.keys()
    managerkeys.sort()

    for mem in managerkeys:
      temp = self.getManager(mem).getStatus(ses)
      if temp:
        data.append("   %s: %s" % (mem, temp))

    # return the list of elements
    return data
