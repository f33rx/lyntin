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
basic.
"""

import data, string, sys, mud, app, select, os, time, regsub
import exported
if os.name != 'posix':
    import thread

# see if they have termios
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

# a thread-function for windows which polls for user input
def GetInputLine(host):
    # this can't be good--FIXME
    """
    while 1:
        while host.line_read != '':
            time.sleep(0.1)
        host.line_read = sys.stdin.readline()
    """
    while not host.closing:
        host.line_read = sys.stdin.readline()

def filter_crud(txt):
    txt = regsub.gsub('\015\\|\r', '', txt)
    # txt = regsub.gsub(chr(27) + '[[0-9;]+[mJ]', '', txt)
    return txt

class Textui:
    closing = 0

    def __init__(self):
        if os.name != 'posix':
            self.line_read = ''
            thread.start_new_thread(GetInputLine, (self,))
            
    def CloseUI(self):
        print "closing text ui"
        self.closing = 1
        pass

    def Putline(self, line):
        """Putline (self, line) -> None

        Prints a line from the client to the user.
        """
        if line:
            line = string.replace(line, "\n", "\n## ")
            print "##", line
            sys.stdout.flush()

    def PutUserInput(self, line):
        if line:
            print line
            sys.stdout.flush()

    def PutUntouchedLine(self, line):
        if line:
            line = filter_crud(line)
            print line
            sys.stdout.flush()
        
    def PutReallyUntouchedLine(self, line):
        if line:
            line = filter_crud(line)
            sys.stdout.write(line)
            sys.stdout.flush()


    # check for stuff from stdin
    def GetUserInput(self):
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

    def Prompt(self):
        self.PutReallyUntouchedLine('\n>')

    def has_echo(self):
        return tio

    # turn on echo
    def OnEcho(self, checktio="yes"):
        if not tio and chectio == "yes":
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

    # turn off echo
    def OffEcho(self, checktio="yes"):
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

    def WarnNoEcho(self):
        self.Putline('Warning, noecho unavailable. '+
                       'Your password will be visible')
        if os.name == 'posix':
            self.Putline('Install the termios module or Tkinter to enable '+
                         'echo toggling')

    def mainloop(self):
        while 1:
            try:
                if not self.app.Loop():
                    return
            except SystemExit:
                return
