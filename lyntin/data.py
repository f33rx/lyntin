##################################################################
# This file is part of Lyntin
# copyright (c) Lyn Headley 1996-1998
#
# Lyntin is distributed under the GNU General Public License.  See
# the file COPYING for details.
#
# module data:
##################################################################
"""
contains the session class, which represents a user connection
and its associated state (actions, aliases, etc), and operations
over its information

contains the databuffer class, where mud output is stored for
later inspection by python functions

contains global variables
"""


import socket, select, regex, os, string, regsub, copy
import mud, app, player, hooks, handler

def clear_all():
    """clear_all() -> None

    Closes all open sessions which are stored in the ses global
    variable.
    """
    for ses in sessionlist:
        ses.Close()


def get_session(str):
    """get_session(str) -> Session

    retrieves the session by name or None if it's not found.
    """
    global sessionlist

    # remove the common session and return the rest
    if str == 'all':
        ret = sessionlist[:]
        ret.remove(common)
        if not ret:
            # tried to do an #all when there were no active sessions
            raise ValueError
        return ret
    # find the desired session
    for ses in sessionlist:
        if ses.name == str:
            return [ses]
    return None

def filter_crud(txt):
    """filter_crud(txt) -> string

    filter ansi and ^M stuff out of text used when logging 
    files.
    """
    txt = regsub.gsub('\015\\|\r', '', txt)
    txt = regsub.gsub('[[0-9;]*[mJ]', '', txt)
    return txt

def filter_cm(txt):
    """filter_cm(txt) -> string
 
    filter ^M stuff out of text.
    """
    txt = regsub.gsub('\015\\|\r', '', txt)
    return txt

def split_into_lines(str):
    """split_into_lines(str) -> []

    Split a string into a list of lines.
    """
    if string.find(str, '\r') != -1:
        return string.splitfields(str, '\r')
    else:
        return string.splitfields(str, '\n')


def compile_trigger(trig):
    """compile_trigger(trig) -> regex

    Convert a trigger with pattern variables into a
    compiled regular expression
    """
    regx = regsub.gsub('%[0-9]+', '\(.*\)', trig)
    return regex.compile(regx)




class Session:
    """
    Session class the framework knows about
    """
    def __init__(self, name, domain, port):
        # we save a certain amount of previous mud output in the 'databuffer'
        # for later inspection by python functions
        self.databuf = databuffer()
        self.connected = 0
        self.name = ''
        self.logfile = None
        self.logging = 0
        self.sorck = None # the socket
        self.domain = None
        self.handlers = []
        
        if name:
            self.name = name
        if domain and port:
            self.sorck= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sorck.connect((domain, port))
            self.domain = domain
            self.name = name
            self.connected = 1        
            
    def tickUpdate(self):
        pass

    def Poll(self):
        read = ''        
        if len(self.handlers) > 0:
            for handler in self.handlers:
                (goahead, read) = handler.handle(self, read)
                

    # write anything from our connection to stdout
    def ReadMud(self):
        try:
            # check if there's anything to read
            if not self.connected:
                return ''
            readers,w,e = select.select([self.sorck], [], [], timeout)
            if readers:
                data = readers[0].recv(BUFSIZE)
                if data == '':    # socket disconnect
                    self.Die()
                    return ''
                return data       # good data
            return ''             # no data
        except socket.error, x:
            self.Die(x)

    
class UserSession(Session):
    """
    session class for the user interface
    """
    def __init__(self, name, domain, port):
        Session.__init__(self, name, domain, port)
        self.aliases = {}
        self.actions = {}
        self.subs = {}
        self.vars = {}
        self.reports = [] # tuples of (file, string)
        self.gags = []
        self.speedwalk = 1
        self.action_list = [] # a list of pairs of the form
                              # (action_trigger, trigger_compiled_regex)
                              # for optimizing action-response
    
        self.lastclock = 0
        self.lastclockdelta = 0
        self.ticklen = 60
        self.lasttickclock = 0
        self.tickwarn = 10
        self.ticker = 0
        self.tickaction = ''
        self.warnedtick = 0
        self.verbose = 1      # verbose mode        

        self.handlers.append(handler.AppHandler())

    def tickUpdate(self):
        player.TimeUpdate((self,))

    def __repr__(self):
        if self.connected:
            return '<session "%s" at %s>'%(self.name, self.domain)
        else:
            return '<session "%s">'%self.name

    def InitLocalSession(self):
        """InitLocalSession(self) -> None

        initialize a new local session.  inherits all its aliases
        etc from the common session.
        """
        self.aliases = copy.copy(common.aliases)
        self.actions = copy.copy(common.actions)
        self.action_list = copy.copy(common.action_list)
        self.gags = copy.copy(common.gags)
        self.subs = copy.copy(common.subs)

    # die
    # triggers hooks.death_hook, which takes a session argument
    # death_hook called *before* the session is actually killed
    def Die(self, exc=''):
        global common, numsessions, sessionlist, currsession
        import types
        if type(exc) == types.StringType:
            player.Putline(exc)
        else:
            player.Putline(exc[1])
        # run the death hook; feed self as argument
        hooks.death_hook.run((self,))

        # mop up this session
        self.Close()
        player.Putline('session "' + self.name + '" died.')
        numsessions = numsessions - 1
        sessionlist.remove(self)
        
        # try to switch to another live session
        if len(sessionlist) > 1:
            currsession = sessionlist[1]
            player.Putline('session "' + currsession.name + '" activated.')
        else:
            # no more live sessions
            currsession = common
            player.Putline('no more active sessions')
            player.Prompt()
        theapp.ui.OnEcho()

    # write text to session's log file, but only if logging is turned on
    def log(self, text):
        if self.logging:
            text = filter_crud(text)
            self.logfile.write(text)

    # add trigger as an action which invokes response
    # also compile and insert trigger's regex into action_list
    def add_action(self, trigger, response):
        if self.actions.has_key(trigger):
            self.actions[trigger] = response
        else:
            self.actions[trigger] = response
            compiled = compile_trigger(trigger)
            self.action_list.append((trigger, compiled))

    # see if text contains anything in our gag list
    def CheckForGaggedText(self, text):
        if text:
            for gt in self.gags:
                if regex.search(gt, text) != -1:
                    return 1
            return 0

    # connect to a mud
    def Connect(domain, port):
        try:
            if not self.domain or not self.port:
                return
            self.sorck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sorck.connect((domain, port))
            self.connected = 1
        except:
            player.Putline('unable to connect')

    # write something to our connection
    def WriteTo(self, data):
        mud.log(data)
        self.log(data)
        if not self.connected:
            player.Putline("data.WriteTo: ** Internal Error: not connected  **")
            return
        try:
            self.sorck.send(data)
        except socket.error, x:
            self.Die(x)

    # close the instance's socket
    def Close(self):
        if self.connected:
            try:
                self.sorck.close()
            except socket.error:
                pass
    
    # input a string, return a list of all the aliases that match it
    def ExpandAlias(self, str):
        return self.Expand(str, self.aliases.keys())

    # input a string, return a list of all the action triggers that match it
    def ExpandAction(self, str):
        return self.Expand(str, self.actions.keys())

    # input a string and a list, return a list of all the elements
    # in the list that match the string
    def Expand(self, s, list):
        str = s[:]
        ret = []
        wildcard = string.count(str, '*')
        if wildcard:
            # convert '*' to '.*'
            str = regsub.gsub('\*', '.*', str)
            # insert anchors
            str = '^' + str + '$'
        for s in list:
            if wildcard:
                if regex.match(str, s) != -1:
                    ret = ret + [s]
            else:
                if str == s:
                    ret = ret + [s]
        return ret

    # wipe session clean of actions/aliases/subs/gags
    def Clear(self):
        self.aliases = {}
        self.actions = {}
        self.action_list = [] # -- JA Was not cleared before... oops :)
        self.subs = {}
        self.gags = []
        self.vars = {}

    # see if text is either a variable or the beginning of a variable
    def Isvar(self, text):
        for v in self.vars.keys():
            if string.find(v, text) == 0:
                return 1
        return 0
        
    # see if text is a variable
    def IsRealvar(self, text):
        for v in self.vars.keys():
            if v == text:
                return 1
        return 0
        
    # get a string suitable for displaying the value of var name
    def GetVarDisplayString(self, name):
        val = self.vars[name]
        ans = '{%s} = {%s}'%(name, val)
        return ans

    # see if any mud output triggers an action.
    # any trigger causes the action_hook to be run, just
    # before the action response is taken

    # FIXME - need to handle $n as well as %n syntax.
    # the former should replace all ; with \; and I think
    # that'll fix the problem.
    def CheckActions(self, output):

        # works with the trigger
        # get a list of variables in str, in the order in
        # which they appear.
        # i.e., for the three variables %4 %1 %3, keylist
        # will get the list ["4","1","3"]
        def orderedvars(instr):
            str = instr[:] # we'll mutilate this copy
            keylist = []
            speckeylist = []
            # loop over the pattern-variables in the string
            # adding the variables to the keylist
            # each time we process one, delete it from the string
            # thus the loop halts when there are no more variables
            while var_regex.search(str) != -1:
                var = var_regex.group(1)
                keylist.append('%' + var)
                # this is not a gsub!
                str = regsub.sub('%[0-9]+', '', str)
            return keylist


        # FIXME - It's somewhere below this line....
        acs = self.action_list  
        matched = [] # list of lines that match
        for line in split_into_lines(output):
            for (ac, regac) in acs:
                if regac.search(line) != -1:
                    line = filter_crud(line)
                    matched.append((line, ac, regac))

        for (match, ac, regac) in matched:
            
            # register the backreferences ('group' method on regex objects)
            regac.search(match)
            response = self.actions[ac] # the response

            # get variables from the action
            actionvars = orderedvars(ac)

            varvals = {}
            # fill in values for all the variables in the match
            for i in xrange(len(actionvars)):
                 #varvals[actionvars[i]]=string.replace(regac.group(i+1),';','_')
                 varvals[actionvars[i]]=regac.group(i+1)

            # add special variables
            varvals['%a'] = string.replace(match,';','_')

            # fill in response variables from those that
            # matched on the trigger
            for var in varvals.keys():
                # replace occurrences of '%i' with val
                if string.find(var, response):
                    response = regsub.sub(var, varvals[var], response)
                if string.find("$" + var[1:], response):
                    response = regsub.sub("$" + var[1:], string.replace(varvals[var], ";", "\;"), response)

            # run the action hook
            hooks.action_hook.run((self, match, response))
            # make my day
            theapp.HandleUserInput(response)            



##################################################################
# databuffer class:
# class for storing previous output from the mud.
# mainly for inspection from python functions, but 
# grepping methods are also provided.
# anytime text is added to the databuffer, the hook 'data_hook',
# is called.  it receives a one elt tuple containing the databuffer.
##################################################################

class databuffer:
    def __init__(self, size=20):
        self.size = size
        self.list = []

    # add a chunk of text
    def add(self, text):
        self.list = [text] + self.list  # ack, optimize
        # chop the storage list if it's too big
        if len(self.list) > self.size:
            while len(self.list) > self.size:
                del self.list[-1]
        # run the hook, which does nothing by default
        hooks.data_hook.run((self,))
    
    # resize the buffer
    def resize(self, s):
        if not (0 < s):
            raise 'LTDatabufferError', 'Negative Size Argument'
        self.size = s

    # search through the databuffer for a regular expression.
    # return a list of all the entries that matched it.
    def grep(self, pat):
        ret = []
        regsearch = regex.search
        for l in self.list:
            if regsearch(pat, l) != -1:
                ret.append(l)
        return ret

    # search through the databuffer for a regular expression.
    # return a list of all the _lines_ that matched it.
    def greplines(self, pat):
        build = []
        regsearch = regex.search
        for g in self.list:
            lines = split_into_lines(g)
            for line in lines:
                if regsearch(pat, line) != -1:
                    build.append(line)
        return build


##################################################################
# Global Variables (ick)
##################################################################

# The application
theapp = None
"""The application global variable.  It becomes an instance of app.client."""

# base directory to look for lyntin files in
initdir = ''
"""initdir is the base directory to look for lyntin files and other such
goodies in."""
if os.environ.has_key('LYNTINDIR'):
    initdir = os.environ['LYNTINDIR']
    if not initdir:
        initdir = os.getcwd()
else:
    initdir = os.getcwd()
if initdir[-1] != os.sep:
    initdir = initdir + os.sep

# datadir
datadir = ''
"""datadir is the directory to store the log in. Default to initdir"""
if os.environ.has_key('LYNTINDATADIR'):
	datadir = os.environ['LYNTINDATADIR']
	if not datadir:
		datadir = initdir
else:
	datadir = initdir
if datadir[-1] != os.sep:
	datadir = datadir + os.sep


# the lyntin character: prepended to all commands
ltchar = '#'
"""The lyntin character: prepended to all lyntin commands."""

# current number of derived sessions
numsessions = 0
"""Current number of derived sessions.  (Heck if i know what this is.)"""

# log file
logfile = ''
"""the logfile."""
try:
    logfile = open(datadir + 'mudlog', 'w')
except:
    player.Putline('\nUnable to write log to LYNTINDATADIR %s!'%datadir)
    logfile = None

# how long we'll wait on a socket for new data
timeout = .01
"""The timeout value which is how long we wait on a socket for data.  Keep
this low."""

common = None
""" The initial session started for the user, from which other
sessions inherit """

# the active session
currsession = None
"""currsession is the current session.  It is initialized to common."""

# global session list
sessionlist = None
"""sessionlist is the list of session objects.  Starts out with just the
common session."""

# how much data we'll read at once from a host
BUFSIZE = 4096
"""BUFSIZE is the amount of data that we read each loop."""

# what a variable looks like
var_regex = regex.compile('%\([0-9]+\)')
"""var_regex is the regular expression that matches variables."""

# latest commands mudder typed
history = []
"""history is the list of the last 30 or so commands the user has
recently typed."""

# size of history
histsize = 30
"""this is the maximum size of the history list."""

# whether we're debugging (affects the function mud.log)
debug = 1
"""this sets whether we're in debug mode or not.  affects mud.log."""

# current lyntin version number
version = "lyntin 2.0b2, maintained by willhelm@users.sourceforge.net"
"""this is the current lyntin version number and such."""
