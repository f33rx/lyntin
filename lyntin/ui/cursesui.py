##################################################################
# This file is part of Lyntin
# copyright (c) Lyn Headley 1996-1998
#
# ... and the Lyntin curses frontend
# copyright (c) Manuel Klimek
#
# Lyntin is distributed under the GNU General Public License.  See
# the file COPYING for details.
#
# module curseui
# curses-based user interface functions
# -- lot of changes: wbg (1/28/2001)
##################################################################
"""
Cursesui is based on curses and will run in a telnet window just
fine.
"""

import data, string, sys, mud, app, select, os, time, regsub
sys.path.append(app.getPath() + 'ui/cui')

from basegui import BaseGUI
from cui_curses import CUI_Curses
from cui_window import CUI_Window
from cui_textwindow import CUI_TextWindow
from cui_lineinput import CUI_LineInput

# why this?
curslib = 'curses'
exec 'import ' + curslib

if os.name != 'posix':
   import thread

class Textui(BaseGUI):
    
   def setup(self):
      self.line_read = ''
      self.support_hash['echo'] = 1

      self.__cui_curses = CUI_Curses()
      self.__main_window = self.__cui_curses.get_main_window()
      self.__output_window = CUI_TextWindow(
            self.__cui_curses,
            location=(self.__main_window.get_x(),
                  self.__main_window.get_y(),
                  self.__main_window.get_width(),
                  self.__main_window.get_height() - 1
            )
      )
      self.__input_window = CUI_LineInput( 
            self.__cui_curses,
            location=(self.__main_window.get_x(),
                  self.__main_window.get_y() +
                  self.__main_window.get_height() - 1 ,
                  self.__main_window.get_width(),
                  1
            )
      )

   def close(self):
      """CloseUI(self) -> None

      Any routines for closing down the ui go here.
      """
      self.__cui_curses.close()

   def CloseUI(self):
      self.close()

   def print_string(self,line,modifiers=None,ending='\n',target=None):
      mud.log(line)
      if modifiers == 'client':
         line = string.replace(line, "\n", "\n## ")
      self.__output_window.put_text(line + ending)
      self.__output_window.refresh()
    
   def get_input(self):
      retval = ''
      self.__input_window.update_input()
      if self.__input_window.has_line():
         retval = self.__input_window.get_line()
         self.__output_window.set_colors('7', '4')
         if self.__input_window.is_echo():
            self.__output_window.put_text(retval + '\n')
         else:
            self.__output_window.put_text('*' * len(retval) + '\n')
         self.__output_window.reset_colors()
      return retval

   def prompt(self):
      self.print_string('\n> ','user','')

   def echo(self,yesno):
      self.__input_window.set_echo(yesno)
    
   def has_echo(self):
      return 1
