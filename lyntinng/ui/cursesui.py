#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License.  See
# the file LICENSE in the distribution for details.
# $Id: cursesui.py,v 1.7 2002/04/11 03:58:22 willhelm Exp $
#######################################################################
"""
This module holds the Curses ui.  It could use some _serious_ work.
"""
import regsub, curses, string
import ui, hooks, event, engine, utils


class Cursesui(ui.BaseUI):
  """
  Anyhow, this is a very un-fully-featured curses ui at the moment.
  It's missing such diverse things as:

    - ansi colors

    - scrollback

    - it should echo back input

    - speed it up

    - fix that scrolling bug (prolly bad math)

    - switch to 4 space indenting
  """
   
  def __init__(self):
    """ Initializes."""
    ui.BaseUI.__init__(self)
    self._main = None
    self._input = None
    self._output = None

    self._newline = []
    self._shutdown = 0
    self._echoon = 1

    self._stdscr = curses.initscr()
    self._stdscr.refresh()
    if curses.has_colors():
      curses.start_color()
      self._colors = 1

    curses.noecho()
    curses.cbreak()

    self._stdscr.nodelay(0)
    self._stdscr.keypad(1)

    (self._height, self._width) = self._stdscr.getmaxyx()
    self._main = curses.newwin(self._height, self._width, 0, 0)

    self._output = self._main.subwin(self._height - 3, self._width, 0, 0)
    # FIXME - might want to try a textbox here
    self._input = self._main.subwin(self._height - 2, 0)

    # self._output.nodelay(1)
    # self._input.nodelay(0) 
    self.refresh_all()
    hooks.startup_hook.register(self.shutdown)
    hooks.shutdown_hook.register(self.startui)


  def startui(self, args):
    """ Starts the ui."""
    import engine
    hooks.to_user_hook.register(self.write)
    engine.myengine.startthread("ui", self.run)


  def shutdown(self, args):
    """
    Gets called (it's registered with the shutdown hook).
    This is important because it ends the curses session
    returning the client back to "normal" land.
    """
    self._shutdown = 1 
    curses.nocbreak()
    self._stdscr.keypad(0)
    curses.echo()
    curses.endwin()
    print "end: you'll be back...."


  def write(self, message):
    """ Writes text to the buffer for viewing by the user.

    Overridden from the baseui.
    """
    if type(message) == type(''):
      message = ui.Message(message, ui.LTDATA)

    message.data = utils.filter_cm(utils.filter_ansi(message.data))

    if message.type == ui.ERROR:
      message.data = message.data.replace("\n", "\nerror: ") + "\n"

    elif message.type == ui.LTDATA:
      message.data = message.data.replace("\n", "\nlyntin: ") + "\n"

    elif message.type == ui.TESTDATA:
      message.data = message.data.replace("\n", "\nTEST: ") + "\n"

    elif message.type == ui.USERDATA:
      message.data += "\n"

    if message.data == '':
      return

 
    ls = message.data.count("\n")
    (y,x) = self._output.getyx()
    (maxy,maxx) = self._output.getmaxyx()
      
    if y + ls > maxy:
      lines = message.data.splitlines()
      for n in range(0, len(lines)):
        (y,x) = self._output.getyx()
        self._output.move(0,0)
        self._output.deleteln()
        self._output.move(y,0)
        self._output.addstr(lines[n])

      if message.data[-1] == "\n":
        (y,x) = self._output.getyx()
        self._output.move(0,0)
        self._output.deleteln()
        self._output.move(y,0)
        self._output.addstr("\n")

      self._output.refresh()
    else:
      self._output.addstr(message.data)

    self._output.refresh()

 
  def run(self):
    """ Reads through keys typed one by one and handles them accordingly."""
    while not self._shutdown:
      newchar = self._input.getch()
      if newchar == 10:
        self.handleinput(string.join(self._newline, ''))
        self._newline = []
        self._input.erase()

      elif newchar == 13:
        continue

      elif (newchar == curses.KEY_DC or 
        newchar == curses.KEY_BACKSPACE or 
        newchar == 8 or newchar == 127):
        if len(self._newline) > 0:
          self._newline = self._newline[:-1]
          (y,x) = self._input.getyx()
          self._input.delch(y, x - 1)

      elif newchar == 21:
        self._input.erase()
        self._newline = []

      elif newchar > 0 and newchar < 256:
        self._input.addch(newchar)
        self._newline.append(chr(newchar))


  def refresh_all(self):
    """
    Refreshes the display.
    """
    self._main.refresh()


  def echo(self, yesno):
    """
    Overridden function.  Changes echo to yesno (hopefully
    either a 1 or 0).
    """
    self._echoon = yesno

