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
import curses

class CUI_Window:
    

#    curses_window = None

    std_fgcolor = '7'
    std_bgcolor = '0'
    cur_fgcolor = '7'
    cur_bgcolor = '0'
    cur_attr = ''

    def set_colors(self, fg, bg):
	self.cur_fgcolor = fg
	self.cur_bgcolor = bg

    def reset_colors(self):
	self.cur_fgcolor = self.std_fgcolor
	self.cur_bgcolor = self.std_bgcolor
	
    def __init__(self, cur, **args):
	self.cui_curses = cur
	if args.has_key('location'):
	    (_x, _y, _width, _height) = args['location']
	    self.x = _x
	    self.y = _y
	    self.width = _width
	    self.height = _height
	    print (
					       _height + _y - 1,
					       _width + _x - 1,
					       _y,
					       _x
					       )
	    self.curses_window = self.cui_curses.get_main_window().get_curses_window().subwin(
					       _height,
					       _width,
					       _y,
					       _x
					       )
#	    self.curses_window.box()
#	    self.insert_text(0,0, str(self.curses_window.getbegyx()))
#	    self.insert_text(10,0, str(self.curses_window.getmaxyx()))
	if args.has_key('window'):
	    win = args['window']
	    self.curses_window = win
	    (self.y, self.x) = win.getbegyx()
	    (self.height, self.width) = win.getmaxyx()
#	self.curses_window.leaveok(1)

    def get_curses_window(self):
	return self.curses_window

    def insert_text(self, x, y, text):
	t = CUI_AnsiWriter(self.cui_curses, self, x, y)
	t.parse(text)

    def refresh(self):
	self.curses_window.refresh()

    def get_x(self):
	return self.x
    
    def get_y(self):
	return self.y
    
    def get_width(self):
	return self.width
    
    def get_height(self):
	return self.height

class CUI_AnsiParser:
    parse_attrib = 0
    attrib_str = ''

    def parse(self, string):
	plain_str = ''
	for nr in range(0, len(string)):
	    c = ord(string[nr]);
	    if not self.parse_attrib:
		
		if c == 27:
		    if len(plain_str) > 0:
			self.plain(plain_str)
			plain_str = ''
		    self.parse_attrib = 1
		    
		elif c >= 32 and c <= 255 and c != ord('\n') and c != 127:
		    plain_str = plain_str + chr(c)

		elif c == 127:
		    self.backspace()

		elif c == ord('\n'):
		    self.newline()
		else:
		    self.ctrl_char(c)
	    else:
		if c == ord('m'):
		    self.found_attrib()
		    self.parse_attrib = 0;

		elif c == ord('\n'):
		    self.newline()

		elif c == ord('A'):
		    self.cursor_up(self.attrib_str[1:])
		    self.parse_attrib = 0;

		elif c == ord('B'):
		    self.cursor_down(self.attrib_str[1:])
		    self.parse_attrib = 0;

		elif c == ord('C'):
		    self.cursor_right(self.attrib_str[1:])
		    self.parse_attrib = 0;

		elif c == ord('D'):
		    self.cursor_left(self.attrib_str[1:])
		    self.parse_attrib = 0;
		    
		elif c == 27:
		    self.found_attrib()
		    
		else:
		    self.attrib_str = self.attrib_str + chr(c)
	if len(plain_str) > 0:
	    self.plain(plain_str)

    def found_attrib(self):
	if(len(self.attrib_str) == 2):
	    self.attribute(self.attrib_str[1])
	    
	elif(len(self.attrib_str) == 3):
	    if(self.attrib_str[1] == '3'):
		self.fgcolor(self.attrib_str[2])
	    elif(self.attrib_str[1] == '4'):
		self.bgcolor(self.attrib_str[2])
			
	self.attrib_str = ''

    def cursor_up(self, nr):
	pass

    def cursor_down(self, nr):
	pass

    def cursor_right(self, nr):
	pass

    def cursor_left(self, nr):
	pass

    def newline(self):
	pass

    def backspace(self):
	pass
    
    def fgcolor(self, color):
	pass
    
    def bgcolor(self, color):
	pass
    
    def attribute(self, attr):
	pass
    
    def plain(self, char):
	pass

    def ctrl_char(self, char):
	pass


class CUI_AnsiWriter(CUI_AnsiParser):
    def __init__(self, cur, win, x, y):
	self.win = win
	self.cur_win = self.win.get_curses_window()
	self.x = x
	self.y = y
	self.cur = cur

    def newline(self):
	self.y = self.y + 1
    
    def fgcolor(self, color):
	self.win.cur_fgcolor = color
    
    def bgcolor(self, color):
	self.win.cur_bgcolor = color
    
    def attribute(self, attr):
	if attr == '0':
	    self.win.cur_attr = ''
	    self.win.cur_fgcolor = self.win.std_fgcolor
	    self.win.cur_bgcolor = self.win.std_bgcolor
	elif attr == '8':
	    self.win.cur_attr = '8'
	else:
	    self.win.cur_attr = self.win.cur_attr + attr

    def plain(self, text):
	fg = self.win.cur_fgcolor
	bg = self.win.cur_bgcolor
	(last_y, last_x)  = self.cur_win.getmaxyx()
#	(y, x) = self.cur_win.getbegyx()
	if self.x < last_x:
	    
	    if len(text) + self.x >= last_x:
		text = text[:(last_x - self.x)]

	    attr = 0
            col = 0
	    if not (self.win.cur_attr == '8'):
		for a in self.win.cur_attr:
		    attr = attr | self.cur.get_attribute(a)
                if self.cur.has_colors():
                    mud.log(str(self.cur.get_color_pair_nr(fg, bg)))
                    col = curses.color_pair(self.cur.get_color_pair_nr(fg, bg))
		self.cur_win.addstr(self.y, self.x, text,
				    col | attr)
	    self.x = self.x + len(text)
    
import mud
