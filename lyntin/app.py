##################################################################
# This file is part of Lyntin
# copyright (c) Lyn Headley 1996-1998
#
# Lyntin is distributed under the GNU General Public License.  See
# the file COPYING for details.
#
##################################################################
"""
contains the client class, which represents lyntin the process,
some utility functions are at the end of the file.
"""

import socket, select, sys, regex, time, regsub
import os, string, types, traceback
import data, player, mud, hooks, cmdparse
import dict_plus

_ltd = ''           # LYNTINDIR

##################################################################
# Client class
# high level application kinda thingy
##################################################################
class client(dict_plus.c):
   """
   high level applications kinda thing
   """

   def __init__(self):
       self.too_many_errors = 20
       self.numerrors = 0
       self.commands = {}  # holds command mappings above and beyond core
      
   def ReturnCommandHash(self):
       """ReturnCommandList(self) -> command hash

       Returns the hash of commands.
       """
       return self.commands

   def AddCommand(self, name, func):
       """AddCommand(self) -> None
       
       Adds a command binding to self.commands .
       """
       if callable(func):
           self.commands[name] = func
       else:
           player.Putline('##' + name + ' is uncallable.  Sorry kiddo.')

   def RemoveCommand(self, name):
       """RemoveCommand(self) -> None
       
       Removes a command binding from self.commands .
       """
       try:    del self.commands[name]
       except: pass
       
   def Loop(self):
       """
       The main loop.
       """
       try:
           datato = self.ui.GetUserInput()
           # get input for all connected sessions
           for ses in data.sessionlist:
               if ses.connected:
                   ses.Poll()
               if ses.ticker:
                   ses.TickUpdate()
               if ses is data.currsession:
                   self.PreHandleUserInput(datato)
                   break
           hooks.internal_tick_hook.run(())
       except KeyboardInterrupt:
           player.Quit(None,None,None)
       except SystemExit: # handle sys.exit
           return None
       except BadUser, spec:
           player.Putline('User variable %s unset!  Abort!'%spec.why)
           return None


       # if anything else goes wrong, we get ugly and print a traceback
       # back to the user.
       #
       # this is helpful for the user's programs; otherwise lyntin
       # would crash completely.
       except:
           from sys import exc_info
           from traceback import format_exception

           info = exc_info()
           exc_class = info[0]
           player.Putline("Cough...  sputter...  lyntin internal error:")
           player.Putline(string.join(format_exception(info[0], info[1], info[2]), ""))

           self.numerrors = self.numerrors + 1
           hooks.error_occurred_hook.run(())
           try:
               if self.numerrors >= self.too_many_errors:
                   hooks.too_many_errors_hook.run(())
           except BadUser, spec:
               player.Putline('User variable %s unset!  Abort!'%spec.why)
               raise SystemExit
       return 1

   def CommandLine1(self):
      """
      The first pass over the command line to determine the user
      interface.
      """
      # FIXME - this needs to be changed to adjust for multiple
      # interfaces.
      # what does that mean?   [2000/08/10 :lh]

      # could even be a socket. hmm...
      # leave a connection open from a box, and hook up to it
      # from another one.
      self.ui = None
      
      if len(sys.argv) > 1:
         if sys.argv[1] == '-ui' and not self.ui:
            # need to do arbitrary importing here of argv[2]
            ui = null
            self.ui = ui
            ui.app = self
         if sys.argv[1] == '-c2' and not self.ui:
            import cursesui2
            ui = cursesui2.Cursesui()
            self.ui = ui
            ui.app = self
         if sys.argv[1] == '-curses' and not self.ui:
            import cursesui
            ui = cursesui.Textui()
            self.ui = ui
            ui.app = self
         if sys.argv[1] == '-nc' and not self.ui:
            import ncgui
            ui = ncgui.Gui()
            self.ui = ui
            ui.app = self
         if sys.argv[1] == '-tk' and not self.ui:
            import tkgui
            ui = tkgui.Gui()
            self.ui = ui
            ui.app = self # circular ref... *shudder*

      if not self.ui:
         import textui
         tui = textui.Textui()
         self.ui = tui
         tui.app = self


   def CommandLine2(self):
      """
      The second pass over the command line to determine files
      to parse.
      """
      # FIXME - this needs to be changed to allow for multiple ui's.
      if len(sys.argv) > 1:
         # handle file args
         for opt in sys.argv[1:]:
            if opt[0] == '-': pass
            else:
               player.DispatchCommand('#read %s'%opt,[data.common])


   def Initialize(self):
      """
      Initializes stuff like the sys.path and cmdparse.
      """
      self.too_many_errors = GetUserCustom('too_many_errors')
      data.histsize = GetUserCustom('history_size')
      cmdparse.Initialize()
      # add source code directories to sys.path
      for dir in GetUserCustom('extra_source_dirs'):
         if dir[0] == os.sep:
            sys.path.append(dir)
         else:
            sys.path.append(data.initdir + dir)


   def PreInitialize(self):
      """
      Does really early initialization.
      """
      hooks.too_many_errors_hook.add(abort_due_to_errors)
      sys.path.append(data.initdir + 'stdlib')

        
   def PreHandleUserInput(self, input):
      """
      do stuff that we want to do one time for each command, like
      registering the command in the history list.
      we can't do this in HandleUserInput because it is recursive
      """
      if input == '\n':
          self.SendPlainInput('\r')

      elif input:
          self.RecordHistory(input)

          # run the received_user_input hook
          newinput = StripFinalEltIf(input, ['\r', '\n'])
          hooks.received_user_input_hook.run((newinput,))

          # send it along to the recursive workhorse
          self.HandleUserInput(input)


   def HandleUserInput(self, input):
      """
      The main "eval" command for lyntin.  This function is
      recursive.
      """
      if not input:
         return
      ses = None
      # trim leading/trailing whitespace
      #input = string.strip(input)

      # check for a sequence of commands separated by ';'
      whether, result = IsSequence(input)
      if whether:
         for s in result:
            self.HandleUserInput(s)
         return
        
      # IsSequence() returns new value for input
      input = result
      if not input:
         return
        
      # check for a braced command
      if IsBrace(input):
         input = input[1:-1]
         self.HandleUserInput(input)
         return

      # fill in values for any variables
      whether, input = cmdparse.SubVars(input)
      if whether:
         self.HandleUserInput(input)
         return

      # check for a reference to the history list
      if input[0] == '!':
         self.DoHistoricCommand(input)
         return

      # work input over for aliases/speedwalking
      whether, input = cmdparse.WorkOver(input, data.currsession)

      if whether == 'speed':
         # speedwalk
         self.DoSpeedWalk(input)
         return

      # triggered an alias, recurse
      elif whether:
         self.HandleUserInput(input)
         return

      # handle commands to client
      goahead = self.HandleExplicitCommands(input)
      if not goahead:
         return

      # expanded to non-command, just send it
      return self.SendPlainInput(input)


   def HandleExplicitCommands(self, input):
      """
      Handle commands to the client (as opposed to the mud).
      """

      if input and input[0] == data.ltchar:
         if input[-1] == '\n':
            # remove data.ltchar at beginning and '\n' at end
            input = input[1:-1] 
         else: input = input[1:] # just remove data.ltchar at beginning.
         words = string.split(input)
         if not words: # nothing to do
            return
            
         # repeat command?
         if self.RepeatCommand(words):
            return 0

         # see if the command applies to a certain session
         try:
            seslist = data.GetSes(words[0])
         except ValueError:
            # tried to do an #all when there aren't any connections
            player.Putline('there aren\'t any sessions!')
            return 0
         # did player specify a target session for this command?
         if seslist:
            if self.IsSessionChange(words):
               player.SetSes(seslist[0])
            # recursively handle whatever was typed
            else:
               oldses = data.currsession
               for ses in seslist:
                  data.currsession = ses
                  self.HandleUserInput(string.join(words[1:]))
               data.currsession = oldses               
            return 0
         else:
            # ok, just apply a command to the current session
            player.DispatchCommand(input, [data.currsession])
            return 0
      return 1
    

   def SessionSend(self, words, seslist):
      """
      Sends some text to the mud from a list of sessions.
      """
      oldses = data.currsession
      for ses in seslist:
         data.currsession = ses
         self.SendPlainInput(string.join(words[1:]))
      data.currsession = oldses

   def IsSessionChange(self, words):
      """
      Checks whether words is a change session request.
      """
      return len(words) == 1

   def DoHistoricCommand(self, input):
      """
      Re-does a command from the history list.
      """
      if regex.search('^![0-9]*', input) == -1:
         # not a valid history command
         self.SendPlainInput(input)
      else:
         num = HistNumber(input)
         # we need to add one to num because the history list
         # has already increased in size thanks to PreHandleUserInput
         h = data.history[num+1]
         input = cmdparse.DoHistorySubs(input, h)
         self.HandleUserInput(input)

   # save input in the history list
   def RecordHistory(self, input):
      """
      Save input in the history list.
      """
      if input == '\n':
         # don't record this crap
         return
      if IsHistory(input):
         # we want to record the actual command, instead of 
         # something like !4, so we have to look it up
         num = HistNumber(input)
         old = data.history[num]
         # perform any requested substitutions
         input = cmdparse.DoHistorySubs(input, old)

      # do what we came here for
      data.history = [input] + data.history
      # 'allocate' a new (smaller) history list if this one 
      # has gotten too huge
      if len(data.history) >= 2 * data.histsize:
         newhist = []
         for i in range(data.histsize):
            newhist = newhist + [data.history[i]]
         data.history = newhist


   def SendPlainInput(self, input):
      """
      If the user is connected, send the input to the mud.
      Otherwise remind her we're not connected.
      """
      if input and data.currsession.connected:
         if input[-1] != '\n' and input[-1] != '\r': 
            # FIXME?
            input = input + '\r'
         mud.log(input)
         data.currsession.WriteTo(input)

      elif not data.numsessions:
         ans = "no session active. " + \
               "use the #session command to start one"
         player.Putline(ans)
         player.Prompt()


   def DoSpeedWalk(self, input):
      """
      Speedwalk stuff.  Sends strings of directions one letter at
      a time.
      """
      # just send it if session has speedwalking off
      if not data.currsession.speedwalk:
         self.SendPlainInput(input)
         return

      send = ''
      i = 0
      num = ''
      n = len(input)
      # build a string called send which is purely letters.
      # convert stuff like 2e5s into eesssss.
      while i < n:
         c = input[i]
         if regex.match('[0-9]', c) != -1:
            # number: keep saving them till we see a char
            num = num + c
         elif num:
            send = send + c * string.atoi(num)
            num = ''
         # just a character, tack it on
         else:
            send = send + c
         i = i + 1
      for s in send:
         if s != '\n':
            self.SendPlainInput(s)
        
   def RepeatCommand(self, words):
      """
      Repeatedly executes a command.
      """
      if words:
         if regex.match('^[0-9]+$', words[0]) != -1:
            num = string.atoi(words[0]) # number of repeats
            words = words[1:]
            for i in range(num):
               self.HandleUserInput(string.join(words))
            return 1
         else: 
            return 0


class BadUser:
   """
   BadUser exception
   """
   def __init__(self, why):
      self.why = why

##################################################################
# Utility Functions
##################################################################

def setPath(path):
   global _ltd
   _ltd = path

def getPath():
   global _ltd
   return _ltd

def Run():
   """
   Initialize app and enter main loop.

   -------------------------
   app bootstrapping order:
   -------------------------
   
   core modules are imported directly.
   app object is created
   initial (common) session is created
   app commands table is initialized
   lyntin stdlib is added to path
   app determines which ui to use, imports and instantiates it
   files are read in and executed from the command line
   user module is imported -- switch with last step?
   usercustom variables are loaded and any extra libs are added to path
   """
   cl = client()
   data.theapp = cl

   # The initial session started for the user
   data.common = data.UserSession('common', None, None)
   data.currsession = data.common   
   # global session list
   data.sessionlist = [data.common]

   # needed to wait until data.theapp is there until we can
   # add all the commands (which is what InitPlayer does).
   player.InitPlayer()

   cl.PreInitialize()
    
   cl.CommandLine1()

   def prul(l): player.PutReallyUntouchedLine(l)
   prul('############################################\n')
   prul("#          Welcome to LynTin...            #\n")
   prul('#          The Hacker\'s mud client.        #\n')
   prul('#          For help, type #help general.   #\n')     
   prul('############################################\n')
   prul('\n\n')

   cl.CommandLine2()

   # process user customizations
   try:
      import user
      player.ImportUser()
   except ImportError:
      player.Putline('Unable to load user customizations')
    
   # warn player if no-echo not possible
   if not mud.has_echo():
      cl.ui.WarnNoEcho()

   cl.Initialize()
   player.Prompt()
   cl.ui.mainloop()

def StripFinalEltIf(seq, remlist):
   """
   If the final element of the seq is in remlist, remove it.
   """
   if seq:
      for elt in remlist:
         if seq[-1] == elt:
            return seq[:-1]
   return seq

def GetAppropriateFile(str, Access):
   """GetApproproateFile(str, Access) -> file

   return a file opened from the given string, with the given 
   access paramter.  if they give us a full path name, try to open it.
   otherwise prepend the datadir to the argument.
   may raise exception IOError.
   """
   if str[0] == os.sep:
      filename = str
   else:
      filename = data.datadir + str
        
   try:
      file = open(filename, Access)
      return file
   except IOError:
      return open(str, Access)

    
def SplitBraced(str):
   """SplitBraced(str) -> tuple of innards

   Takes a string like {blah} {blah} and returns a tuple of the innards
   """
   nesting = 0
   one = ''
   two = ''
   parsed = ''
   if string.find(str, '{') == -1:
      # unbraced, just chop it into two parts and return it
      sp = string.split(str)
      return sp[0], string.join(sp[1:])

   while str[0] == ' ':
      # trim leading whitespace
      str = str[1:]
    
   for c in str:
      if c == '{' and (not nesting) and parsed:
         # we know one is unbraced, two braced
         one, parsed = parsed, ''
         nesting = nesting + 1
         # chop off final whitespace from one
         if one[-1] == ' ':
            one = one[:-1]
      elif c == '{':
         if nesting:
            # preserve brace if we are alread nested
            parsed = parsed + c
         nesting = nesting + 1
      elif c == '}':
         if nesting > 1:
            # preserve brace if we are doubly(or more) nested
            parsed = parsed + c
         nesting = nesting - 1 
         if nesting == 0:
            if one:
               two = parsed
            else:
               one = parsed
      else:
         parsed = parsed + c

   if nesting < 0:
      raise 'LTSyntaxError', 'unmatched braces'
   return one, two

def CountRegex(pat, str):
   """CountRegex(pat, str) -> int

   Returns the number of occurances of pattern in a string.
   """
   s = str[:]
   r = regex.compile(pat)
   count = 0
   while r.search(s) != -1:
      count = count + 1
      s = regsub.sub(pat, '', s)
   return count

def StripVars(s):
   """StripVars(s) -> list

   Returns a list of all variables in a string.  No element
   will occur twice in the list.
   """
   str = s[:]
   vars = []
   # regex to match nested variables within braces
   nested_var = regex.compile('{.*%%\([0-9]+\).*}')
   while nested_var.search(str) != -1:
      # found a nested variable: replace it with an unnested var
      pat = '%%'+nested_var.group(1)
      repl = '%'+nested_var.group(1)
      str = regsub.gsub(pat, repl, str)
   ret = str[:]
   while data.var_regex.search(str) != -1:
      var = data.var_regex.group(1)
      if var not in vars:
         vars = vars + [var]
      str = regsub.sub(data.var_regex.givenpat, '', str)
   return vars, ret

# is input enclosed in braces?
def IsBrace(input):
   """IsBrace(input) -> bool

   Returns whether the input is enclosed in braces.
   """
   if len(input) < 2:
      return 0
   return input[0] == '{' and input[-1] == '}'

def IsSequence(input):
   """IsSequence(input) -> bool

   check for sequencing, i.e. commands separated by ';'
   no choice but to do a grungy old parse
   on the way, we find syntax errors in lyntin commands
   """
   if not input:
      return 0, ''
   ind = regex.search(';', input)
   # are we dealing with a lyntin command?
   # if not, then syntax errors don't matter
   if input[0] == data.ltchar:
      is_command = 1
   else:
      is_command = 0
   whether = 0 # whether it's a sequence
   seq = [] # a list of strings to return as the sequence
   parsed = ''
   if ind != -1:
      nesting = 0
      for c in input:
         if nesting < 0 and is_command:
            raise 'LTSyntaxError', 'Unmatched Braces'
         elif c == '{':
            nesting = nesting + 1
            parsed = parsed + c
         elif c == '}':
            nesting = nesting - 1
            parsed = parsed + c
         elif c == ';' and nesting == 0:
            # this is a command sequence, unless the 
            # preceeding char was a backslash
            if not parsed:
               # empty command
               continue
            elif parsed[-1] == '\\':
               parsed = parsed[:-1]
               parsed = parsed + c # keep the semi
            else:
               whether = 1
               seq = seq + [parsed]
               parsed = ''
         else:
            parsed = parsed + c
      # done parsing, check for mismatched braces
      if nesting != 0 and is_command:
         raise 'LTSyntaxError', 'Unmatched Braces'
   else:
      return 0, input

   if seq:
      if parsed:
         # tack on final command
         seq = seq + [parsed]
      return whether, seq
   return whether, parsed


def IsHistory(input):
   """IsHistory(input) -> bool

   Returns whether this is a history command.
   """
   return regex.search('^![0-9]*', input) == 0

def HistNumber(input):
   """HistNumber(input) -> int

   Returns the number of a history command that input
   is referencing.
   e.g. !4 returns 4
   """
   rx = regex.compile('!\([0-9]+\)')
   if rx.search(input) == -1:
      return 0
   return string.atoi(rx.group(1))

def GetUserCustom(var):
   """GetUserCustom(var) -> depends

   Gets a user-customized variable
   """
   try:
      uc = player.user.user_custom
   except:
      raise BadUser, BadUser('NoModule')
   if uc.has_key(var):
      return uc[var]
   raise BadUser, BadUser(var)

# too many errors; quit lyntin
def abort_due_to_errors(arg):
   """abort_due_to_errors(arg) -> None

   There have been too many errors.  so we quit.
   """
   player.Putline('too many errors! abort! abort! abort!')
   player.Quit(None, None, None)

