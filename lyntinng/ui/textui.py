#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: textui.py,v 1.17 2002/05/09 23:20:12 willhelm Exp $
#######################################################################
"""
Holds the text ui class.
"""
import string, re, sys, traceback
import engine, hooks, event, utils, ui, exported

myui = None

def get_ui_instance():
  global myui
  if myui == None:
    myui = Textui()
  return myui

class Textui(ui.BaseUI):
  """
  This is the text ui.  It's super basic and should run almost
  anywhere.  It lacks several useful functions that the TkGui
  and the Curses ui (eventually) will have.
  """
  def __init__(self):
    """ Initialize the textui."""
    ui.BaseUI.__init__(self)
    hooks.startup_hook.register(self.startui)

  def startui(self, args):
    """ Sets up the UI."""
    hooks.to_user_hook.register(self.write)
    engine.myengine.startthread("ui", self.run)

  def run(self):
    """ This is the poll loop for user input."""

    # FIXME - should look into reworking this code
    import event, sys, select, os
    try:
      if os.name == 'posix':
        while not self.shutdownflag:
          readers,w,e = select.select([sys.stdin], [], [])
          if readers:
            for mem in readers:
              try:
                data = mem.readline()
                self.handleinput(data)
              except IOError:
                # traceback.print_exc()
                pass

      else:
        while not self.shutdownflag:
          self.handleinput(sys.stdin.readline())

    except select.error, e:
      (errno,name) = e
      if errno == 4:
        exported.write_message("system exit: you'll be back...")
        event.ShutdownEvent().enqueue()
        return

    except SystemExit:
      exported.write_message("system exit: you'll be back...")
      event.ShutdownEvent().enqueue()

    except:
      traceback.print_exc()
      event.ShutdownEvent().enqueue()


  def write(self, message):
    """ Handles writing information from the mud and/or SB
    to the user.
    """
    if type(message) == type(''):
      sys.stdout.write ("lyntin: " + message.replace("\n", "\nlyntin: ") + 
                        "\n")
      return

    pretext = ""
    if (message.session != None 
        and message.session != exported.get_current_session()):
      pretext = "[" + message.session.getName() + "] "

    if message.type == ui.ERROR:
      pretext = "error: " + pretext

    elif message.type == ui.LTDATA:
      pretext = "lyntin: " + pretext

    elif message.type == ui.TESTDATA:
      pretext = "TEST: " + pretext

    elif message.type == ui.USERDATA:
      # we don't print user data in the textui
      return

    if pretext != "":
      if len(message.data) > 0 and message.data[-1] == "\n":
        message.data = (pretext + 
                        message.data[:-1].replace("\n", "\n" + pretext) + 
                        "\n")
      else:
        message.data = pretext + message.data.replace("\n", "\n" + pretext)

    sys.stdout.write(message.data)
    sys.stdout.flush()

  def prompt(self):
    """ Prints a prompt to the user."""
    sys.stdout.write("> ")
    sys.stdout.flush()

  def flush(self):
    """ Flushes the stdout.  Not sure we really need this
    but it's here."""
    sys.stdout.flush()
