#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: textui.py,v 1.28 2002/10/26 04:32:40 willhelm Exp $
#######################################################################
"""
Holds the text ui class.
"""
import string, re, sys, traceback, os
import lyntin, ansi, engine, hooks, event, utils, ui, exported

HELP_TEXT = """
The textui is the most basic ui you can get.  It works great over
telnet/ssh, but terrible in the Win32 command window.  At the same 
time, because it's so basic, it tends to be a good testing ui.

The textui has no special features.
"""
myui = None

DEFAULT = [-1, -1, -1]
DEFAULT_ANSI = chr(27) + "[0m"

def get_ui_instance():
  global myui
  if myui == None:
    myui = Textui()
  return myui

class Textui(ui.BaseUI):
  """
  This is the text ui.  It's super basic and should run almost
  anywhere.  It lacks several useful functions that the Tkui
  and the Curses ui (eventually) will have.
  """
  def __init__(self):
    """ Initialize the textui."""
    ui.BaseUI.__init__(self)
    hooks.startup_hook.register(self.startui)
    hooks.to_user_hook.register(self.write)
    self._currcolors = {}
    self._unfinishedcolor = {}

  def startui(self, args):
    """ Sets up the UI."""
    global HELP_TEXT
    exported.add_help("textui", HELP_TEXT)
    engine.myengine.startthread("ui", self.run)
    exported.write_message("For textui help, type \"#help textui\".")

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


  def write(self, args):
    """
    Handles writing information from the mud and/or Lyntin
    to the user.
    """
    message = args[0]

    if type(message) == type(''):
      message = ui.Message(message)

    line = message.data
    ses = message.session

    # we prepend the session name to the text if this is not the 
    # current session sending text.
    pretext = ""
    if (ses != None and ses != exported.get_current_session()):
      pretext = "[" + ses.getName() + "] "

    if message.type == ui.ERROR or message.type == ui.LTDATA:
      if message.type == ui.ERROR:
        pretext = "error: " + pretext
      else:
        pretext = "lyntin: " + pretext

      line = pretext + utils.chomp(line).replace("\n", "\n" + pretext)
      if lyntin.ansicolor == 1:
        line = DEFAULT_ANSI + line 
      sys.stdout.write(line + "\n")
      return

    elif message.type == ui.USERDATA:
      # we don't print user data in the textui
      return

    if lyntin.ansicolor == 0:
      if pretext:
        if line[-1] == "\n":
          line = (pretext + line[:-1].replace("\n", "\n" + pretext) + "\n")
        else:
          line = pretext + line.replace("\n", "\n" + pretext)
      sys.stdout.write(line)
      sys.stdout.flush()
      return

    # each session has a saved current color for mud data.  we grab
    # that current color--or user our default if we don't have one
    # for the session yet.
    if self._currcolors.has_key(ses):
      color = self._currcolors[ses]
    else:
      # need a copy of the list and not a reference to the list itself.
      color = DEFAULT[:]


    # some sessions have an unfinished color as well--in case we
    # got a part of an ansi color code in a mud message, and the other
    # part is in another message.
    if self._unfinishedcolor.has_key(ses):
      leftover = self._unfinishedcolor[ses]
    else:
      leftover = ""

    lines = line.splitlines(1)
    if lines:
      for i in range(0, len(lines)):
        mem = lines[i]
        acolor = ansi.convert_tuple_to_ansi(color)

        color, leftover = ansi.figure_color(mem, color, leftover)

        if pretext:
          lines[i] = DEFAULT_ANSI + pretext + acolor + mem
        else:
          lines[i] = DEFAULT_ANSI + acolor + mem

      sys.stdout.write("".join(lines) + DEFAULT_ANSI)
      sys.stdout.flush()

    self._currcolors[ses] = color
    self._unfinishedcolor[ses] = leftover


  def prompt(self):
    """ Prints a prompt to the user."""
    sys.stdout.write("> ")
    sys.stdout.flush()

  def flush(self):
    """ Flushes the stdout.  Not sure we really need this
    but it's here."""
    sys.stdout.flush()

# Local variables:
# mode:python
# py-indent-offset:2
# tab-width:2
# End:
