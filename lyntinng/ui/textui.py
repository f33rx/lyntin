#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2001
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: textui.py,v 1.2 2002/01/20 07:21:02 willhelm Exp $
#######################################################################
"""
Holds the text ui class.
"""
import string, re, sys
import engine, event, utils, ui

class Textui(ui.BaseUI):
  """
  This is the text ui.  It's super basic and should run almost
  anywhere.  It lacks several useful functions that the TkGui
  and the Curses ui (eventually) will have.
  """
  def __init__(self):
    """ Initialize the textui."""
    ui.BaseUI.__init__(self)
    engine.myengine.register(engine.STARTUPFREQ, self.startui)

  def startui(self, args):
    """ Sets up the UI."""
    engine.myengine.startthread("ui", self.run)
     
  def run(self):
    """ This is the poll loop for user input."""
    import event, sys, select, os
    try:
      if os.name == 'posix':
        while not self.shutdownflag:
          readers,w,e = select.select([sys.stdin], [], [])
          if readers:
            for mem in readers:
              data = mem.readline()
              if data == chr(10):
                data = "#cr"
              self.handleinput(data)

      else:
        while not self.shutdownflag:
          self.handleinput(sys.stdin.readline())

    except SystemExit:
      pass

    except:
      event.ShutdownEvent().enqueue()

  def write(self, message):
    """ Handles writing information from the mud and/or SB
    to the user.
    """
    if type(message) == type(''):
      sys.stdout.write ("lyntin: " + 
           message.replace("\n", "\nlyntin: ") + "\n")
      return

    if message.type == ui.MUDDATA:
      sys.stdout.write ( message.data )
      sys.stdout.flush()

    elif message.type == ui.ERROR:
      sys.stdout.write ("error: " + 
            message.data.replace("\n", "\nerror: ") + "\n")

    elif message.type == ui.LTDATA:
      sys.stdout.write ("lyntin: " + 
            message.data.replace("\n", "\nlyntin: ") + "\n")

    elif message.type == ui.TESTDATA:
      sys.stdout.write ("\nTEST: " + 
            message.data.replace("\n", "\nTEST: ") + "\n")

    elif message.type == ui.USERDATA:
      pass

  def prompt(self):
    """ Prints a prompt to the user."""
    sys.stdout.write("> ")
    sys.stdout.flush()

  def flush(self):
    """ Flushes the stdout.  Not sure we really need this
    but it's here."""
    sys.stdout.flush()
