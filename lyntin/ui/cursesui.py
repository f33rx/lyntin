##################################################################
# This file is part of Lyntin
# copyright (c) Will Guaraldi 2001
#
# Lyntin is distributed under the GNU General Public License.  See
# the file LICENSE in the distribution for details.
# $Id: cursesui.py,v 1.8 2001/08/06 02:00:19 willhelm Exp $
##################################################################
"""
This module holds the Curses ui.  It could use some serious work.
"""
import data, string, sys, mud, app, select, os, time, regsub
import regsub
from basegui import BaseGUI

import curses

class Cursesui(BaseGUI):
   """
   This is the second curses ui.  The first one was very unwieldy
   and even though my curses programming skill suck, I wrote this one
   to replace that one because I can maintain this one.

   Anyhow, this is a very un-fully-featured curses ui at the moment.
   It's missing such diverse things as:
    * ansi colors
    * scrollback
    * it should echo back input
    * speed it up
    * fix that scrolling bug (prolly bad math)
    * switch to 4 space indenting
   """
   
   def setup(self):
      """
      Sets up the screen into a series of windows.  Then initializes
      the ui.
      """
      self._main = None
      self._input = None
      self._output = None

      self._closing = 0
      self._echoon = 1
      self._newline = ''
      self.support_hash['echo'] = 1
      self._echoon = 1

      self._stdscr = curses.initscr()
      self._stdscr.refresh()
      if curses.has_colors():
         curses.start_color()
         self._colors = 1

      curses.noecho()
      curses.cbreak()

      self._stdscr.nodelay(1)
      self._stdscr.keypad(1)

      (self._height, self._width) = self._stdscr.getmaxyx()
      self._main = curses.newwin(self._height, self._width, 0, 0)

      self._output = self._main.subwin(self._height - 3, self._width, 0, 0)
      self._input = self._main.subwin(self._height - 2, 0)

      self._output.scrollok(1)
      self._output.nodelay(1)
      self._input.nodelay(1) 
      self.refresh_all()



   def refresh_all(self):
      """
      Refreshes the display.
      """
      self._main.refresh()


   def close(self):
      """
      Over-ridden from basegui.  This is called when the client
      is closing down.

      This is important because it ends the curses session
      returning the client back to "normal" land.
      """
      self._closing = 1
      curses.nocbreak()
      self._stdscr.keypad(0)
      curses.echo()
      curses.endwin()


   def filter_crud(self,txt):
      """
      Filters out crud (and ansi colors).
      """
      txt = regsub.gsub('\015\\|\r', '', txt)
      txt = regsub.gsub('[[0-9;]*[mJ]', '', txt)
      return txt


   def print_string(self,line,modifiers=None,ending='\n',target=None):
      """
      Prints a string to the output so the user can read it.
      """
      if modifiers == 'client':
         line = string.replace(line, "\n", "\n## ")
     
      line = self.filter_crud(line)
 
      ls = line.count("\n")
      (y,x) = self._output.getyx()
      (maxy,maxx) = self._output.getmaxyx()
      
      if y + ls > maxy:
         lines = line.splitlines()
         for n in range(0, len(lines)):
            (y,x) = self._output.getyx()
            self._output.move(0,0)
            self._output.deleteln()
            self._output.move(y,0)
            self._output.addstr(lines[n])

         if line[-1] == "\n":
            self._output.addstr("\n")

         self._output.refresh()
      else:
         self._output.addstr(line + ending)

      self._output.refresh()

    
   def get_input(self):
      """
      Retrieves input 20 characters at a time.
      """
      newline = self._newline
      newchar = 0

      for i in range(0,20):
         try:
            newchar = self._input.getch()
         except:
            break
         if newchar < 0:
            break 

         if newchar == 10:
            if not newline:
               newline = "#cr"
            self._input.erase()
            self._newline = ''
            return newline

         elif newchar == 13:
            pass

         elif newchar == curses.KEY_DC or 
            newchar == curses.KEY_BACKSPACE or 
            newchar == 8 or newchar == 127:
            if newline:
               newline = newline[:-1]
               (y,x) = self._input.getyx()
               self._input.delch(y, x - 1)

         elif newchar == 21:
            self._input.erase()
            newline = ''

         elif newchar > 0 and newchar < 256:
            self._input.addch(newchar)
            newline = newline + chr(newchar)

      self._newline = newline



   def echo(self, yesno):
      """
      Overridden function.  Changes echo to yesno (hopefully
      either a 1 or 0).
      """
      self._echoon = yesno

    
   def has_echo(self):
      """
      Returns whether or not we have the echo ability--which
      we do.
      """
      return 1
