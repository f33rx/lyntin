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
from cui_textwindow import CUI_TextWindow
from cui_window import CUI_Window

class CUI_Curses:
    
    # Attributes (txt/color): ^[{attr1};...;{attrn}m
    txtAttribs = { "0": "None",             # Reset all attributes
		     "1": curses.A_BOLD,      # Bright
		     "2": curses.A_DIM,       # Dim
		     # 3 ????
		     "4": curses.A_UNDERLINE, # Underscore
		     "5": curses.A_BLINK,     # Blink
		     # 6 ????
		     "7": curses.A_REVERSE,   # Reverse
		     "8": "None"              # Hidden
		     }
    
    # Color codes have the form xy, where x is
    # 3: fg color
    # 4: bg color
    # and y is one of the following
    colorCodes = { "0": curses.COLOR_BLACK,
		     "1": curses.COLOR_RED,
		     "2": curses.COLOR_GREEN,
		     "3": curses.COLOR_YELLOW,
		     "4": curses.COLOR_BLUE,
		     "5": curses.COLOR_MAGENTA,
		     "6": curses.COLOR_CYAN,
		     "7": curses.COLOR_WHITE
		     }

    __main_window = None
    __hasColorSupport = 0
    
    color_pairs = {}
    color_pair_next = 1

    def __init__(self):
	# get the main screen
        stdscr = curses.initscr()

	# clear the terminal
        stdscr.refresh()

	if curses.has_colors():
            # start color support
            curses.start_color()
            self.__hasColorSupport = 1

	# don't echo characters we type
        curses.noecho()
	# don't wait for carriage return before getting input
	curses.cbreak()

	# getch() in the main window is noblocking
	stdscr.nodelay(1)

	# get keypad-keys
        stdscr.keypad(1)

	self.__main_window = CUI_TextWindow(self, window=stdscr)

    def get_main_window(self):
	return self.__main_window

    def has_colors(self):
        return self.__hasColorSupport

    def get_color_pair_nr(self, fg, bg):
	if self.color_pairs.has_key(fg + bg):
	    #mud.log("Has!" + str(self.color_pairs[fg + bg]))
	    return self.color_pairs[fg + bg]
	else:
	    #mud.log("New!")
	    curses.init_pair(self.color_pair_next,
			     self.colorCodes[fg],
			     self.colorCodes[bg])
	    self.color_pairs[fg + bg] = self.color_pair_next
	    self.color_pair_next = self.color_pair_next + 1
	    return (self.color_pair_next - 1)

    def get_attribute(self, attr):
	return self.txtAttribs[attr]

    def close(self):
        curses.endwin()
	
import mud
