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
##################################################################
from cui_window import CUI_Window

import mud

class CUI_TextWindow(CUI_Window):
   buffer = []
   pos = 0
   scrollmode = 1
    
   def __init__(self, cur, **args):
      CUI_Window.__init__(self, cur, **args)
      self.buffer.append('')
      self.curses_window.scrollok(1)
      self.curses_window.idlok(1)

   def set_scrollmode(self, to):
      self.scrollmode = to

   def is_scrollmode(self):
      return self.scrollmode

   def put_text(self, text):
      color_str = ''
      color_str = color_str + chr(27) + '[3' + self.cur_fgcolor + 'm'
      color_str = color_str + chr(27) + '[4' + self.cur_bgcolor + 'm'
        
      self.insert_buffer(color_str + text)
      # self.refresh()

   def insert_buffer(self, text):
      for c in text:
         if c == '\n':
            self.buffer.append('')
         else:
            self.buffer[len(self.buffer)-1] = self.buffer[len(self.buffer)-1] + c 
      self.curses_window.addstr(text)
      
         

   def refresh(self):
      self.curses_window.clear()
      if self.scrollmode:
         self.pos = len(self.buffer) - self.height
         if self.pos < 0: self.pos = 0

      for n in range(0, self.height):
         if self.pos + n < len(self.buffer):
            self.insert_text(0, n, self.buffer[self.pos + n])
      self.curses_window.refresh()
