##################################################################
# This file is part of Lyntin
# copyright (c) Lyn Headley 1996-2001
#
# Lyntin is distributed under the GNU General Public License.  See
# the file LICENSE in the distribution for details.
# $Id: data.py,v 1.33 2001/08/06 02:00:19 willhelm Exp $
##################################################################
"""
contains the session class, which represents a user connection
and its associated state (actions, aliases, etc), and operations
over its information

contains the databuffer class, where mud output is stored for
later inspection by python functions

contains global variables
"""


import socket, select, re, os, string, copy
import mud, app, player, hooks, handler



##################################################################
#  Global Variables (ick)
##################################################################

"""this is the current lyntin version number and such."""
version = """
For bugs, suggestions, mailing list info, feature requests,
architecture docs, et al, see http://lyntin.sourceforge.net/

lyntin 2.0.1, (May 25, 2001) copyright 2000, 2001 Lyn Headley
"""




"""The application global variable.  It becomes an instance of app.client."""
theapp = None


"""initdir is the base directory to look for lyntin files and other such
goodies in."""
initdir = ''
if os.environ.has_key('LYNTINDIR'):
   initdir = os.environ['LYNTINDIR']
   if not initdir:
      initdir = os.getcwd()
else:
   initdir = os.getcwd()
if initdir[-1] != os.sep:
   initdir = initdir + os.sep


"""datadir is the directory to store the log in. Default to initdir"""
datadir = ''
if os.environ.has_key('LYNTINDATADIR'):
   datadir = os.environ['LYNTINDATADIR']
   if not datadir:
      datadir = initdir
else:
   datadir = initdir
if datadir[-1] != os.sep:
   datadir = datadir + os.sep


"""the logfile."""
logfile = ''
try:
   logfile = open(datadir + 'mudlog', 'w')
except:
   player.PutError('Unable to write log to LYNTINDATADIR %s!'%datadir)
   logfile = None

def log(text):
   """logs output to a mudlog opened in the previous couple of
   lines
   """
   if logfile != None:
      logfile.write(filter_crud(text))

"""The lyntin character: prepended to all lyntin commands."""
ltchar = '#'


"""Current number of derived (non-common) sessions."""
numsessions = 0


"""The timeout value which is how long we wait on a socket for data.  Keep
this low."""
timeout = .01


""" The initial session started for the user, from which other, derived,
sessions inherit """
common = None


"""currsession is the current session.  It is initialized to common."""
currsession = None


"""sessionlist is the list of session objects.  Starts out with just the
common session."""
sessionlist = None


"""BUFSIZE is the amount of data that we read each loop."""
BUFSIZE = 4096


"""var_regex is the regular expression that matches variables."""
var_regex = re.compile('%(\d+)')


"""history is the list of the last 30 or so commands the user has
recently typed."""
history = []


"""this is the maximum size of the history list."""
histsize = 30


"""this sets whether we're in debug mode or not.  affects mud.log."""
debug = 1



##################################################################
#  Functions
##################################################################


def clear_all():
   """
   Closes all open sessions which are stored in the ses global
   variable.
   """
   for ses in sessionlist:
      ses.Close()


def get_session(str):
   """
   Retrieves the session by name or None if it's not found.
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
   """
   Filter ansi and ^M stuff out of text used when logging 
   files.
   """
   txt = re.sub('\015|\r', '', txt)
   txt = re.sub('\[[0-9;]*[mJ]', '', txt)
   return txt

def filter_cm(txt):
   """
   Filter ^M stuff out of text.
   """
   txt = re.sub('\015|\r', '', txt)
   return txt

def split_into_lines(str):
   """
   Split a string into a list of lines.
   """
   if string.find(str, '\r') != -1:
      return string.splitfields(str, '\r')
   else:
      return string.splitfields(str, '\n')


def compile_trigger(trig):
   """
   Convert a trigger with pattern variables into a
   compiled regular expression
   """
   regx = re.sub('%[0-9]+', '(.*)', trig)
   return re.compile(regx)




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

      self.ansi_colors = 1  # should we show ansi colors?

      self.verbose = 1      # verbose mode--do we want to print
                            # lots of silly messages 1/0

      self.quietmode = 0    # quells PutMessage totally


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
      """
      Pull data from the mud and return it.
      """
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

   def Die(self, exc=''):
      """
      Die closure.
      """
      pass


class UserSession(Session):
   """
   Session class for the user interface
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
      self.handlers.append(handler.AppHandler())

   def tickUpdate(self):
      player.time_update((self,))

   def __repr__(self):
      if self.connected:
         return '<session "%s" at %s>'%(self.name, self.domain)
      else:
         return '<session "%s">'%self.name

   def InitLocalSession(self):
      """
      Initialize a new local session.  Inherits all its aliases
      etc from the common session.
      """
      self.aliases = copy.copy(common.aliases)
      self.actions = copy.copy(common.actions)
      self.action_list = copy.copy(common.action_list)
      self.gags = copy.copy(common.gags)
      self.subs = copy.copy(common.subs)

   def Die(self, exc=''):
      """
      Triggers death_hook which takes a session argument
      death_hook called *before* the session is actually killed.
      """
      global common, numsessions, sessionlist, currsession
      import types
      if type(exc) == types.StringType:
         player.PutError(exc)
      else:
         player.PutMessage(exc[1])
      # run the death hook; feed self as argument
      hooks.death_hook.run((self,))

      # mop up this session
      self.Close()
      player.PutError('session "' + self.name + '" died.')
      numsessions = numsessions - 1
      sessionlist.remove(self)

      # try to switch to another live session
      if len(sessionlist) > 1:
         currsession = sessionlist[1]
         player.PutError('session "' + currsession.name + '" activated.')
      else:
         # no more live sessions
         currsession = common
         player.PutError('no more active sessions')
         player.prompt()
      theapp.ui.OnEcho()

   def log(self, text):
      """
      Writes text to a session's log file but only if logging is turned
      on.
      """
      if self.logging and self.logfile != None:
         self.logfile.write(data.filter_crud(text))

   # add trigger as an action which invokes response
   # also compile and insert trigger's regex into action_list
   def add_action(self, trigger, response):
      """
      Add trigger as an action which invokes response
      Also compiles and inserts trigger's regex into the
      action_list.
      """
      if self.actions.has_key(trigger):
         self.actions[trigger] = response
      else:
         self.actions[trigger] = response
         compiled = compile_trigger(trigger)
         self.action_list.append((trigger, compiled))

   def CheckForGaggedText(self, text):
      """
      See if text contains anything in our gag list.
      If so, returns a 1, else a 0.
      """
      if text:
         for gt in self.gags:
            if re.compile(gt).search(text):
               return 1
         return 0

   def Connect(domain, port):
      """
      Connects to a mud.
      """
      try:
         if not self.domain or not self.port:
            return
         self.sorck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         self.sorck.connect((domain, port))
         self.connected = 1
      except:
         player.PutError('unable to connect')

   def WriteTo(self, data):
      """
      Writes something out to our connection.
      """
      # mud.log(data)
      self.log(data)
      if not self.connected:
         player.PutError("data.WriteTo: ** Internal Error: not connected  **")
         return
      try:
         self.sorck.send(data)
      except socket.error, x:
         self.Die(x)

   # close the instance's socket
   def Close(self):
      """
      Closes the socket connection.
      """
      if self.connected:
         try:
            self.sorck.close()
         except socket.error:
            pass

   def ExpandAlias(self, str):
      """
      Returns a list of all the aliases that matches given string.
      """
      return self.Expand(str, self.aliases.keys())

   def ExpandAction(self, str):
      """
      Returns a list of all the action triggers that match a given
      string.
      """
      return self.Expand(str, self.actions.keys())

   # input a string and a list, return a list of all the elements
   # in the list that match the string
   def Expand(self, s, list):
      """
      Given a string and a list, returns a list of all the elements
      in the list that match the string.
      """
      str = s[:]
      ret = []
      wildcard = string.count(str, '*')
      if wildcard:
         # convert '*' to '.*'
         str = re.sub('\*', '.*', str)
         # insert anchors
         str = '^' + str + '$'
      for s in list:
         if wildcard:
            if re.compile(str).match(s):
               ret = ret + [s]
         else:
            if str == s:
               ret = ret + [s]
      return ret

   # wipe session clean of actions/aliases/subs/gags
   def Clear(self):
      """
      Wipes a session clean of actions/aliases/subs/gags.
      """
      self.aliases = {}
      self.actions = {}
      self.action_list = [] # -- JA Was not cleared before... oops :)
      self.subs = {}
      self.gags = []
      self.vars = {}

   def IsVar(self, text):
      """
      See if text is either a variable or the beginning of a variable.
      """
      for v in self.vars.keys():
         if string.find(v, text) == 0:
            return 1
      return 0

   def IsRealVar(self, text):
      """
      See if the text is a variable.
      """
      for v in self.vars.keys():
         if v == text:
            return 1
      return 0

   def GetVarDisplayString(self, name):
      """
      Get a string suitable for displaying the value of a var name.
      """
      val = self.vars[name]
      ans = '{%s} = {%s}'%(name, val)
      return ans

   def CheckActions(self, output):
      """
      see if any mud output triggers an action.
      any trigger causes the action_hook to be run, just
      before the action response is taken

      FIXME - need to handle $n as well as %n syntax.
      the former should replace all ; with \; and I think
      that'll fix the problem.
      """
      def orderedvars(instr):
         """
         works with the trigger
         get a list of variables in str, in the order in
         which they appear.
         i.e., for the three variables %4 %1 %3, keylist
         will get the list ["4","1","3"]
         """
         str = instr[:] # we'll mutilate this copy
         keylist = []
         speckeylist = []
         # loop over the pattern-variables in the string
         # adding the variables to the keylist
         # each time we process one, delete it from the string
         # thus the loop halts when there are no more variables
         match = var_regex.search(str)
         while match:
            var = match.group(1)
            keylist.append('%' + var)
            # this is not a gsub!
            str = re.sub('%[0-9]+', '', str, 1)
            match = var_regex.search(str)
         return keylist


      # FIXME - It's somewhere below this line....
      acs = self.action_list  
      matched = [] # list of lines that match
      for line in split_into_lines(output):
         for (ac, regac) in acs:
            match = regac.search(line)
            if match:
               line = filter_crud(line)
               matched.append((line, ac, regac))

      for (match, ac, regac) in matched:

         matchobj = regac.search(match)
         response = self.actions[ac] # the response

         # get variables from the action
         actionvars = orderedvars(ac)
         varvals = {}
         # fill in values for all the variables in the match
         for i in xrange(len(actionvars)):
            #varvals[actionvars[i]]=string.replace(regac.group(i+1),';','_')
            varvals[actionvars[i]]=matchobj.group(i+1)

         # add special variables
         varvals['%a'] = string.replace(match,';','_')
            
         # fill in response variables from those that
         # matched on the trigger
         for var in varvals.keys():
            # replace occurrences of '%i' with val
            if string.find(var, response):
               response = re.sub(var, varvals[var], response)
            if string.find("$" + var[1:], response):
               response = re.sub("$" + var[1:],
                                 string.replace(varvals[var], ";", "\;"), response, 1)

         # run the action hook
         hooks.action_hook.run((self, match, response))
         # make my day
         theapp.HandleUserInput(response)            



##################################################################
# databuffer class:
##################################################################

class databuffer:
   """
   Class for storing previous output from the mud.
   mainly for inspection from python functions, but 
   grepping methods are also provided.
   Anytime text is added to the databuffer, the hook 'data_hook',
   is called.  It receives a one elt tuple containing the 
   databuffer.
   """
   def __init__(self, size=20):
      self.size = size
      self.list = []


   def add(self, text):
      """
      Add a chunk of text to the data buffer.
      """
      self.list = [text] + self.list  # ack, optimize
      # chop the storage list if it's too big
      if len(self.list) > self.size:
         while len(self.list) > self.size:
            del self.list[-1]
      # run the hook, which does nothing by default
      hooks.data_hook.run((self,))


   def resize(self, s):
      """
      Resize the buffer.
      """
      if not (0 < s):
         raise 'LTDatabufferError', 'Negative Size Argument'
      self.size = s


   def grep(self, pat):
      """
      Search through the databuffer for a regular expression.
      Return a list of all the entries that matched it.
      """
      ret = []
      for l in self.list:
         if re.compile(pat).search(l):
            ret.append(l)
      return ret

   def greplines(self, pat):
      """
      Search through the databuffer for a regular expression.
      Return a list of all the _lines_ that matched it.
      """
      build = []
      for g in self.list:
         lines = split_into_lines(g)
         for line in lines:
            if re.compile(pat).search(line):
               build.append(line)
      build.reverse()
      return build



# Local variables:
# mode:python
# py-indent-offset:3
# tab-width:3
# End:
