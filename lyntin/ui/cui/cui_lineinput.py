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
from cui_window import CUI_Window, CUI_AnsiParser

class CUI_LineInput(CUI_Window):

    has_line_flag = 0
    x = 0
    echo_flag = 1

    def __init__(self, cur, **args):
	CUI_Window.__init__(self, cur, **args)
	self.line = ''
	self.curses_window.nodelay(1)
	self.refresh()

    def is_echo(self):
	return self.echo_flag

    def set_echo(self, yesno):
	self.echo_flag = yesno

    def update_input(self):
	i = CUI_AnsiInput(self)
	
	self.refresh()
	c = self.curses_window.getch()
	while (not self.has_line_flag) and c != -1:
	    i.parse(chr(c))
	    
	    if not self.has_line_flag:
		c = self.curses_window.getch()

    def refresh(self):
	if self.echo_flag:
	    whole_line = ('> ' + self.line +
			  ' ' * (self.width - len(self.line) - 3))
	else:
	    whole_line = ('> ' +
			  '*' * len(self.line) +
			  ' ' * (self.width - len(self.line) - 3))
			  
	self.insert_text(0, 0, whole_line)
	self.curses_window.move(0, self.x + 2)
	self.curses_window.refresh()
    
    def has_line(self):
	return self.has_line_flag

    def clear(self):
	self.has_line_flag = 0
	self.line = ''
	self.x = 0
	self.refresh()
    
    def get_line(self):
	if self.has_line_flag:
	    retval = self.line
	    self.clear()
	    return retval


class CUI_AnsiInput(CUI_AnsiParser):
    def __init__(self, li):
	self.line_input = li

    def newline(self):
	self.line_input.has_line_flag = 1

    def backspace(self):
	self.line_input.line = self.line_input.line[:(len(self.line_input.line)-1)]
	if self.line_input.x > 0:
	    self.line_input.x = self.line_input.x - 1
	self.line_input.refresh()

    def cursor_left(self, nr):
	if self.line_input.x > 0:
	    self.line_input.x = self.line_input.x - 1
	self.line_input.refresh()
	
    def cursor_right(self, nr):
	if self.line_input.x < len(self.line_input.line):
	    self.line_input.x = self.line_input.x + 1
	self.line_input.refresh()

    def plain(self, text):
	self.line_input.line = self.line_input.line[:self.line_input.x] + text +self.line_input.line[self.line_input.x:]
	self.line_input.x = self.line_input.x + len(text)
	self.line_input.refresh()

    def ctrl_char(self, char):
	if char == 1:
	    self.line_input.x = 0
	    self.line_input.refresh()
	elif char == 5:
	    self.line_input.x = len(self.line_input.line)
	    self.line_input.refresh()
	elif char == 11:
	    self.line_input.line = self.line_input.line[:self.line_input.x]
	    self.line_input.refresh()
	else:
	    mud.log('other: ' + str(char))

