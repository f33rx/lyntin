#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: event.py,v 1.30 2002/05/29 23:58:03 willhelm Exp $
#######################################################################
"""
Holds the event structures in lyntin.  All events inherit from 
Event.  This is pretty standard, nothing really exciting here.
Each event class implements the execute function which gets called
by the event handler thread when it pulls the event object off the
event queue.  You can use the __init__ function to initialize
your event as it is not used in the base Event class.
"""
import string, os, traceback, sys, glob
import engine, hooks, ui.ui, lyntin, exported

class Event:
  """ Base Event class.

  This is the basic Event class.  It has an enqueue method
  which enqueues the event in the event queue (in the engine
  module).  It also has an execute method which is executed
  when the event is dequeued and handled.  Override the
  'execute' function for your functionality to get executed.
  """
  def __init__(self):
    """ Initialize."""
    pass

  def __str__(self):
    """ Allows us to print out event objects."""
    ret = str(self.__class__)
    return ret[ret.find(".") + 1:]

  def enqueue(self):
    """ This enqueues this event into the event queue.  Don't
    overload this unless you have to.
    """
    engine.myengine.enqueue(self)

  def execute(self):
    """ Override this.  This gets called by the event handler
    to execute your event.
    """
    pass


class StartupEvent(Event):
  """ Starts up and initializes Lyntin.

  When Lyntin is started, we try to do as much as we can
  inside of the SstartupEvent and through the startup hook.
  """
  def __init__(self):
    """ Initialize."""
    pass

  def execute(self):
    """ Execute."""

    try:
      # instantiate a ui
      uiname = lyntin.options['ui']
      modulename = uiname + "ui"

      import ui.__init__

      uiinstance = ui.__init__.get_ui(modulename)
      if not uiinstance:
        uiinstance = ui.__init__.get_ui("textui")

      if not uiinstance:
        raise ValueError, "Can't start ui."

      engine.myengine.setUI(uiinstance)

      exported.write_message("UI started.")
    except Exception, e:
      print "Cannot start ui: %s" % e
      sys.exit(0)

    # import modules listed in modulesinit
    exported.write_message("Importing modules in modules directory.")

    try:
      import modules.__init__
      modules.__init__.load_modules()
    except:
      exported.write_error("Modules did not load correctly.")
      ShutdownEvent().enqueue()
      traceback.print_exc()

    try:
      import help.__init__
      help.__init__.load_help()
    except:
      exported.write_error("Help did not load correctly.")
      ShutdownEvent().enqueue()
      traceback.print_exc()

    # spam the startup hook 
    hooks.startup_hook.spamhook()

    # if we don't have a readfile set by --read flag, then we
    # try to use ~/.lyntinrc
    if len(lyntin.options['readfile']) == 0 and lyntin.options['datadir'] != '':
      lyntinrcfile = lyntin.options['datadir'] + ".lyntinrc"
      lyntin.options['readfile'].append(lyntinrcfile)
      exported.write_message("Setting readfile to " + lyntinrcfile)

    # handle command files
    for mem in lyntin.options['readfile']:
      exported.write_message("Reading in file " + mem)
      # we have to escape windows os separators because \ has a specific
      # meaning in the argparser
      mem = mem.replace("\\", "\\\\")
      exported.get_session('common').handleUserData("%sread %s" % 
                                                   (lyntin.commandchar, mem))

    # start the timer thread
    engine.myengine.startthread("timer", engine.myengine.runtimer)

    # we're done initialization!
    message = ("Initialization complete.\n" +
               "------------------------------------\n" + 
               "Welcome to Lyntin.\n" + 
               "For help, type #help general.\n" +
               "------------------------------------\n")

    exported.write_message(message)
    engine.myengine.writePrompt()


class ShutdownEvent(Event):
  """
  This calls sys.exit(0) which will trigger the Python atexit stuff.
  """
  def __init__(self):
    """ Initialize."""
    pass

  def execute(self):
    """ Execute the shutdown."""
    sys.exit(0)


class EchoEvent(Event):
  """
  Echo events get created when the connected server sends a Telnet
  Echo request--either to tell us that the server is handling echo
  (echo off) or that the server will not handle echo (echo on).
  """
  def __init__(self, onoff):
    """ Initialize.

    arguments:

      'onoff' -- (int) 1 if echo turns on, or 0 if echo turns off

    """
    self._state = onoff

  def execute(self):
    """ Runs the echo event through anything listening."""
    hooks.echo_hook.spamhook((self._state))
    lyntin.echo = self._state


class ReloadEvent(Event):
  """
  Reload events are kind of non-self-explanatory until you understand
  that what is being reloaded is a module and it's being reloaded
  by some kind of user direction.  i.e. the user types "reload modulex"
  will kick of a reload event.
  """
  def __init__(self, name, mod):
    """ Initialize.

    arguments:

      'name' -- (string) i don't know what this is

      'mod' -- (module) the module to reload

    """
    self._name = name
    self._mod = mod

  def execute(self):
    """ Execute."""
    try:
      reload(self._mod)
      message = "reload successful: %s" % self._name
    except:
      message = "reload unsuccessful: %s" % self._name

    exported.write_message(message)
 

class MudEvent(Event):
  """
  A mud event is when the connected mud sends data to us.  We
  spam that data to the mud event hook.
  """
  def __init__(self, session, input):
    """ Initialize.

    arguments:

      'session' -- (session) the session handling this mud
                   connection

      'input' -- (string) the data sent from the mud

    """
    self._session = session
    self._input = input

  def execute(self):
    """ Execute."""
    hooks.from_mud_hook.spamhook((self._session, self._input))
    engine.myengine.handleMudData(self._session, self._input)


class InputEvent(Event):
  """
  A user input event is created whenever the user types something
  into their ui and it creates a user event from it.
  """
  def __init__(self, input, internal=0, session=None):
    """ Initialize.

    arguments:

      'input' -- (string) the data from the user

      'internal=0' -- (int) whether (1) or not (0) this is an 
                      internally generated user input.  if it 
                      is internally generated, then we don't 
                      record it in the history and such.

      'session=None' -- (session.Session instance) which session
                        to execute the input event in

    """
    self._input = input
    self._internal = internal
    self._session = session

  def execute(self):
    """ Execute."""
    exported.write_user_data(self._input)

    # we don't record internal stuff or input that isn't supposed
    # to be echo'd
    if self._internal == 0 and lyntin.echo == 1:
      exported.get_engine().getHistoryManager().recordHistory(self._input)

    engine.myengine.handleUserData(self._input, session=self._session)


class OutputEvent(Event):
  """
  Sometimes it's necessary to put data that's going to the ui
  into an event so that it is displayed in the correct order.
  This event allows you to do that.
  """
  def __init__(self, message):
    """ Initialize.

    arguments:

      'message' -- (string) the message

    """
    self._message = message

  def execute(self):
    """ Execute."""
    exported.write_ui(self._message)


class SpamEvent(Event):
  """
  Certain things can kick off a call to spam a hook.  Rather
  than doing it "inline" so to speak, it's sometimes nice to kick
  it off in its own event.  The timer uses this to handle kicking
  anything that's listening to the hooks.timer_hook.
  """
  def __init__(self, hook, args):
    """ Initialize.

    arguments:

      'hook' -- (hooks.Hook instance) the hook to spam

      'args' -- (list of arguments) the arguments to send to
                the functions--refer to the documentation on 
                the hook 

    """
    self._hook = hook
    self._args = args

  def execute(self):
    """ Execute."""
    self._hook.spamhook(self._args)
