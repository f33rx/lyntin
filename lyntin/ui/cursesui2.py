##################################################################
# This file is part of Lyntin
# copyright (c) Lyn Headley 1996-1998
#
# Lyntin is distributed under the GNU General Public License.  See
# the file COPYING for details.
#
# curses ui (2--wbg)
##################################################################

import data, string, sys, mud, app, select, os, time, regsub
import regsub
import mud
from basegui import BaseGUI

import curses


class Cursesui(BaseGUI):
   def __init__(self):
      self._main = None
      self._input = None
      self._output = None

      BaseGUI.__init__(self)
      self._closing = 0
      self._echoon = 1
      self._newline = ''
      self.support_hash['echo'] = 1
      self._echoon = 1


   def setup(self):
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
      # self._output.box()
      self._output.scrollok(1)
      # self._output.setscrreg(0, self._height - 1)
      self._output.nodelay(1)
      self._input.nodelay(1) 
      self.refresh_all()



   def refresh_all(self):
      self._main.refresh()
      # self._input.refresh()


   def close(self):
      """close(self) -> None

      Over-ridden from basegui.  This is called when the client
      is closing down.
      """
      self._closing = 1
      curses.nocbreak()
      self._stdscr.keypad(0)
      # curses.keypad(0)
      curses.echo()
      curses.endwin()


   def filter_crud(self,txt):
      txt = regsub.gsub('\015\\|\r', '', txt)
      txt = regsub.gsub('[[0-9;]*[mJ]', '', txt)
      return txt


   def print_string(self,line,modifiers=None,ending='\n',target=None):
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
            self._output.addstr(lines[n] + ending)

         self._output.refresh()
 
      else:
         self._output.addstr(line + ending)

      self._output.refresh()

    
   def get_input(self):
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

         elif newchar == curses.KEY_DC or newchar == curses.KEY_BACKSPACE or newchar == 8 or newchar == 127:
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


   def prompt(self):
      # self.print_string('\n> ','user','')
      pass


   def echo(self,yesno):
      self._echoon = yesno

    
   def has_echo(self):
      return 1
