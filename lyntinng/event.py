#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: event.py,v 1.6 2002/02/04 01:10:16 willhelm Exp $
#######################################################################
"""
Holds the event structures in lyntin.  All events inherit from 
Event.  This is pretty standard, nothing really exciting here.
Each event class implements the execute function which gets called
by the event handler thread when it pulls the event object off the
event queue.  You can use the __init__ function to initialize
your event as it is not used in the base Event class.
"""
import string, os, traceback, sys, getopt
import engine, ui.ui, lyntin

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
    return ret[string.find(ret, ".") + 1:]

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
  inside of the SstartupEvent and through the Startup frequency.
  """
  def __init__(self, args):
    """ Initialize.

    arguments:

      'args' -- (list of strings) the sys.args sent in

    """
    self._args = args

  def execute(self):
    """ Execute."""

    # instantiate a ui
    # FIXME - do we want to handle arbitrary ui's?
    if lyntin.options['ui'] == 'tk':
      from ui.tkgui import TkGui
      engine.myengine.setUI(TkGui())

    elif lyntin.options['ui'] == 'curses':
      from ui.cursesui import Cursesui
      engine.myengine.setUI(Cursesui())

    else:
      from ui.textui import Textui
      engine.myengine.setUI(Textui())

    engine.write_message("UI started.")

    # import modules listed in modulesinit
    engine.write_message("Importing modules in modules directory.")
    try:
      import modules.__init__
      modules.__init__.load_modules()
    except:
      engine.write_error("Modules did not load correctly.")
      ShutdownEvent().enqueue()
      traceback.print_exc()

    # spam the startup frequency
    engine.myengine.spamfreq(engine.STARTUPFREQ, ())

    # handle command files
    f = lyntin.options['readfile']
    if f != '':
      engine.write_message("Reading in file " + f)
      engine.myengine.getSession('common').handleUserData('#read ' + f)

    # start the timer thread
    engine.myengine.startthread("timer", engine.myengine.runtimer)

    # we're done initialization!
    message = ("Initialization complete.\n" +
               "------------------------------------\n" + 
               "Welcome to Lyntin.\n" + 
               "For help, type #help general.\n" +
               "------------------------------------\n")

    engine.write_message(message)
    engine.myengine.writePrompt()


class ShutdownEvent(Event):
  """
  When the user shuts down lyntin, it triggers a shutdown
  event to close all network connections, close ui's, return the 
  user's session to a normal state, and shuts down whatever modules
  have registered with the shutdown frequency.
  """
  def __init__(self):
    """ Initialize."""
    pass

  def execute(self):
    """ Execute the shutdown."""
    import time
    engine.write_message("shutting down...  goodbye.")
    engine.myengine.spamfreq(engine.SHUTDOWNFREQ)
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
    """ 1 means turn echo on, 0 means turn it off."""
    engine.myengine.spamfreq(engine.ECHOFREQ, (self._state))


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
      message = "reload successful: " + self._name
    except:
      message = "reload unsuccessful: " + self._name

    engine.write_message(message)
 

class MudEvent(Event):
  """
  A mud event is when the connected mud sends data to us.  We
  spam that data to the mud event frequency.
  """
  def __init__(self, input):
    """ Initialize.

    arguments:

      'input' -- (string) the data sent from the mud

    """
    self._input = input

  def execute(self):
    """ Execute."""
    engine.myengine.handleMudData(self._input)


class InputEvent(Event):
  """
  A user input event is created whenever the user types something
  into their ui and it creates a user event from it.
  """
  def __init__(self, input):
    """ Initialize.

    arguments:

      'input' -- (string) the data from the user

    """
    self._input = input

  def execute(self):
    """ Execute."""
    engine.write_user_data(self._input)
    engine.myengine.handleUserData(self._input)


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
    engine.write_ui(self._message)


class SpamEvent(Event):
  """
  Certain things can kick off a call to spam a frequency.  Rather
  than doing it "inline" so to speak, it's sometimes nice to kick
  it off in its own event.  The timer uses this to handle kicking
  anything that's listening to the TIMERFREQ.
  """
  def __init__(self, frequency, args):
    """ Initialize.

    arguments:

      'frequency' -- (string) the frequency to spam

      'args' -- (list of arguments) the arguments to send to
                the functions--refer to the documentation on 
                the frequencies

    """
    self._frequency = frequency
    self._args = args

  def execute(self):
    """ Execute."""
    engine.myengine.spamfreq(self._frequency, self._args)
