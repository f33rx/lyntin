##################################################################
# This file is part of Lyntin
# copyright (c) Lyn Headley 1996-1998
#
# Lyntin is distributed under the GNU General Public License.  See
# the file COPYING for details.
#
# module textui
# text-based user interface functions
##################################################################
"""
Textui is the text user interface (the default).  It's _real_
basic as it's designed to work almost everywhere you can have
a command prompt.
"""

import data, string, sys, mud, app, select, os,  regsub
from basegui import BaseGUI
import exported


if os.name != 'posix':
    import thread

# see if they have termios for echo abilities
try:
    import termios, TERMIOS
except ImportError:
    tio = 0
else:
    tio = 1

# whether echo is on
echo = 1
if tio:
    stdinfd = sys.stdin.fileno()
    echonew = termios.tcgetattr(stdinfd)
    onecho_attr = echonew
    offecho_attr = echonew

def getinputline(host):
    """getinputline(host) -> None

    This polls for user input by blocking on readline.
    """
    while not host.closing:
        host.line_read = sys.stdin.readline()


class Textui(BaseGUI):
    closing = 0

    def filter_crud(self, txt):
        txt = regsub.gsub('\015\\|\r', '', txt)
        # txt = regsub.gsub(chr(27) + '[[0-9;]+[mJ]', '', txt)
        return txt

    """over-ridden from BaseGUI"""
    def setup(self):
        if os.name != 'posix':
            self.line_read = ''
            thread.start_new_thread(getinputline, (self,))
            
    """over-ridden from BaseGUI"""
    def close(self):
        self.turnonecho()
        sys.stdout.write("closing text ui\n")
        self.closing = 1
         

    """over-ridden from BaseGUI"""
    def print_string(self,line,modifiers=None,ending='\n',target=None):
        if modifiers == 'client' or modifiers == 'error':
            line = string.replace(line, "\n", "\n## ")
            line = "## " + line + "\n"

        line = self.filter_crud(line)
        sys.stdout.write(line)
        sys.stdout.flush()


    """over-ridden from BaseGUI"""
    def get_input(self):
        if os.name == 'posix':
            readers,w,e = select.select([sys.stdin], [], [], data.timeout)
            if not readers: # timer expired
                return
            for R in readers:
                thedata = R.readline()
                if thedata == chr(10):
                    thedata = "#cr"
                return thedata
        else:
            retval = self.line_read
            self.line_read = ''
            return retval

    """over-ridden from BaseGUI"""
    def prompt(self):
        self.print_string('\n> ','user','')

    """over-ridden from BaseGUI"""
    def has_echo(self):
        return tio

    """over-ridden from BaseGUI"""
    def echo(self,yesno):
        if yesno == 1:
            self.turnonecho()
        else:
            self.turnoffecho()

    def turnonecho(self, checktio="yes"):
        if not tio and checktio == "yes":
            return
        global echo
        global offecho_attr
        global onecho_attr

        echo = 1
        fd = sys.stdin.fileno()
        new = termios.tcgetattr(fd)
        offecho_attr = new[:]
        try:
            termios.tcsetattr(fd, TERMIOS.TCSADRAIN, onecho_attr)
        except:
            raise 'lt_echo_error', 'unable to turn on echo'

    def turnoffecho(self, checktio="yes"):
        if not tio and checktio == "yes":
            return
        global echo
        global onecho_attr
        global offecho_attr

        echo = 0
        fd = sys.stdin.fileno()
        new = termios.tcgetattr(fd)
        onecho_attr = new[:]
        new[3] = new[3] & ~TERMIOS.ECHO          # lflags
        offecho_attr = new[:]
        try:
            termios.tcsetattr(fd, TERMIOS.TCSADRAIN, new)
        except:
            raise 'lt_echo_error', 'unable to turn off echo'

    """over-ridden from BaseGUI"""
    def warn_no_echo(self):
        self.PutError('Warning, noecho unavailable. '+
                       'Your password will be visible')
        if os.name == 'posix':
            self.PutError('Install the termios module or Tkinter to enable '+
                         'echo toggling')
