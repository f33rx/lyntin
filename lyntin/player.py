##################################################################
# This file is part of Lyntin
# copyright (c) Lyn Headley 1996-1998
#
# Lyntin is distributed under the GNU General Public License.  See
# the file COPYING for details.
#
##################################################################
"""
defines lyntin's user-level commands
(of course they can all be used from user code too)

Commands can also be written in modules and when the modules are imported
(via the #import command) the commands can be added to the command
hash by importing exported.py and using the lyntin_add_command function
there.
"""

import string, sys, re, socket, time
import data, mud, app, hooks, cmdparse, os

# delay import of user module until we have more state
user = None

# exceptions
class SessionError: pass

command_table = {}

def dispatch_command(input, seslist):
   """dispatch_command(input, seslist) -> None

   input - the input string
   seslist - list of session objects

   parse command intended for the client, (i.e. one prefaced by
   data.ltchar)
   allows abbreviations for most commands.
   """

   import data

   if not input: return
   # strip any data.ltchar from the front
   if input[0] == data.ltchar:
      input = input[1:]
   if not seslist:
      raise SessionError, 'No session supplied'

   if len(input) <= 0:
      return

   words = string.split(input)

   # execute some python code?
   if input[0] == '@':
      input = input[1:]
      hooks.exec_user_code_hook.run((input,))

      # auto-bind lyntin variables to local variables some day?
      exec input in user.__dict__
      return

   # for commands in data.theapp.commands listing
   clist = data.theapp.commands.keys()
   for mem in clist:
      # this means it has to be matched exactly
      if mem[0] == "^":
         if re.compile(mem).search(words[0]):
            return data.theapp.commands[mem](words, input, seslist)
      else:
         if string.find(mem, words[0]) == 0:
            return data.theapp.commands[mem](words, input, seslist)

   # unrecognized command
   PutError('error: command is not defined --%s--'%words[0])
   return



###
### Player library functions
###

def expand_command(s, list):
   """expand_command(s, list) -> string

   Inputs a string and a list and returns a list of all the elements
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

def set_session(ses):
   """set_session(ses) -> None

   Sets the active session.  Run set_session hook *before*
   the actual switch
   """
   # pass old and new sessions to the set_session hook
   hooks.set_session_hook.run((data.currsession, ses))
   data.currsession = ses
   ans = 'ok, session "' + ses.name + '" activated.'
   PutMessage(ans)

def prompt():
   """prompt() -> None

   Prints a prompt.
   """
   data.theapp.ui.Prompt()

def time_update(seslist):
   """time_update(seslist) -> None

   Checks the current time and does time-related stuff (via the ticker).
   """
   for ses in seslist:
      click = time.time()
      ses.lastclockdelta = click - ses.lastclock
      if ses.ticker:
         TickerUpdate((ses,))
      ses.lastclock = click

def import_user():
   """import_user() -> None

   Want to delay this.
   (i have no clue what this means.)
   """
   global user
   user = get_user_module()

def get_user_module():
   """get_user_module() -> None

   Imports the user module and returns it.
   """
   import user
   return user




def PutError(line):
   """PutError(line) -> None

   Prints an error to the ui.
   """
   data.theapp.ui.PutError(line)

def PutMessage(line):
   """PutMessage(line) -> None

   Prints a lyntin message (non-error informative thing) to 
   the ui.
   """
   data.theapp.ui.PutMessage(line)

def PutRaw(line):
   """PutRaw(line) -> None

   Prints raw messages to the ui.  This is if you wanted
   to format it yourself or dislike the Error/Message methods.
   Output from the mud is always printed raw.
   """
   data.theapp.ui.PutRaw(line)


###
### User standard commands
###

def PrintCommands(words, input, seslist):
   """PrintCommands(words, input, seslist) -> None

   Prints all the commands to the screen in a pretty list.
   """
   the_list = data.theapp.ReturnCommandHash().keys()
   the_list.sort()
   PutMessage('Commands:')
   count = 1
   new_line = '   '
   for mem in the_list:
      if mem[0] == "^":
         new_line = new_line + string.ljust(mem[1:], 16)
      else:
         new_line = new_line + string.ljust(mem, 16)
      if (count % 3) == 0:
         PutMessage(new_line)
         new_line = '   '
      count = count + 1
   PutMessage(new_line)
   return

def AddCommand(words, input, seslist):
   """AddCommand(words, input, seslist) -> None

   Adds a command to the client.  This is a user command.
   If they don't pass in enough args, we print out the command
   list--we might want to change this later, but it makes 
   the 'command' command more like alias and action.
   """
   if len(words) > 2:
      ret = data.theapp.AddCommand(words[1], words[2])
      if ret == 1:
         PutMessage("command: " + words[1] + " added.")
      else:
         PutMessage("command: " + words[1] + " either doesn't exist, or is uncallable.")
   else:
      return PrintCommands(words, input, seslist)

def UnCommand(words, input, seslist):
   """UnCommand(words, input, seslist) -> None

   Removes a command from the client.
   This is a user command.
   """
   un = string.join(words[1:])
   # remove braces if necessary
   if un[0] == '{' and un[-1] == '}':
      un = un[1:-1]

   acs = expand_command(un, data.theapp.commands)

   if acs:
      for ac in acs:
         data.theapp.RemoveCommand(ac)

      PutMessage('uncommand: ' + str(len(acs)) + ' commands removed')
   else:
      PutError('uncommand: that command is not defined')


def LynImport(words, input, seslist):
   """LynImport(words, input, seslist) -> None

   Imports a module which adds itself to the app and such.
   This is a user command.  If the module has already
   been imported, then it gets reloaded.
   """
   import sys
   PutMessage("trying to import " + words[1])

   try:
      if sys.modules.has_key(words[1]):
         reload(sys.modules[words[1]])
         PutMessage("import (actually--we reloaded) successful.")
      else:
         exec ("import " + words[1])
         PutMessage("import successful.")
   except ImportError:
      PutError(words[1] + " module does not exist.")
   except:
      from sys import exc_info
      from traceback import format_exception

      info = exc_info()
      exc_class = info[0]
      PutError(string.join(format_exception(info[0], info[1], info[2]), ""))
   return

def Showme(words, input, seslist):
   """Showme(words, seslist) -> None

   Prints the words to the clients display
   This is a user command.
   """
   hooks.showme_command_hook.run((input, seslist))
   for ses in seslist:
      if len(words) == 1:
         PutError('showme: showme what?')
         return
      # only display if this is the current session
      if ses is data.currsession:
         PutMessage(string.join(words[1:]))

def Ses(words, input, seslist):
   """Ses(words, input, seslist) -> None

   to - 3 argument tuple: (name, host, port number)

   Creates a new session Connected to a mud.
   Increment global session count and add new session to global
   session list.
   This is a user command.
   """
   hooks.session_command_hook.run((input, seslist))
   to = words[1:]

   if len(to) == 0:
      PutMessage("sessions: ")
      # FIXME - print sessions here?

   elif len(to) >= 3:

      # see if there's an existing session with the same name
      for ses in data.sessionlist:
         if ses.name == to[0]:
            PutError('ses: session "'+ses.name+'" already exists.')
            return

      try:
         # extract parameters
         name = to[0]
         host = to[1]
         port = string.atoi(to[2])
      except ValueError:
         PutError('ses: bad arguments: #session sesname hostname port')
         return

      try:
         # try to connect with the given parameters
         PutMessage("ses: Trying to connect...")
         thisses = data.UserSession(name,host,port)

      except socket.error:
         PutError("ses: Unable to connect!")

         # pass the session name to the connect_failed hook
         hooks.connect_failed_hook.run((name, host, port))

      except ValueError:
         PutError('ses: illegal port number: %d'%port)
      else:
         # it worked
         # initialize new session as copy of common session
         thisses.InitLocalSession()
         data.currsession = thisses
         data.sessionlist = data.sessionlist + [thisses]
         data.numsessions = data.numsessions + 1

         # pass the session name to the connect_succeeded hook
         hooks.connect_succeeded_hook.run((name, host, port))
   else:
      PutMessage("ses: requires 3 arguments")
      PutMessage("ses <name> <address> <port>")

def SpeedWalk(words, input, seslist):
   """SpeedWalk(seslist) -> None

   Toggles speedwalking.
   This is a user command.
   """
   hooks.speedwalk_command_hook.run((seslist,))
   for ses in seslist:
      ses.speedwalk = not ses.speedwalk
      if ses.speedwalk:
         PutMessage('speedwalk: speedwalking is now ON')
      else:
         PutMessage('speedwalk: speedwalking is now OFF')

def DataBuffer(words, input, seslist):
   """DataBuffer(words, seslist) -> None

   With one argument, sets the size of the session's databuffer.
   With no arguments, it displays the databuffer.
   This is a user command.
   """
   hooks.databuffer_command_hook.run((input, seslist))
   for ses in seslist:
      if len(words) < 2:
         PutMessage('databuffer: databuffer size is %d'%ses.databuf.size)
         continue
      try:
         num = string.atoi(words[1])
      except ValueError:
         PutError('databuffer: invalid argument')
      else:
         ses.databuf.resize(num)
         PutMessage('databuffer: databuffer size set to %d'%num)

def Char(words, input, seslist):
   """Char(words, seslist) -> None

   with no arguments, prints the lyntin character.
   With one argument, sets the lyntin character.
   This is a user command.
   """
   hooks.char_command_hook.run((input, seslist))
   for ses in seslist:
      if len(words) == 1:
         PutMessage("current lyntin character: '%s'"%data.ltchar)
         if not data.currsession.connected:
            prompt()
      elif len(words) == 2:
         c = words[1]
         if len(c) != 1:
            PutError('char: %s is not a single character!'%c)
         else:
            data.ltchar = c
            PutMessage("ok, lyntin character set to '%s'"%c)
            if not data.currsession.connected:
               prompt()
      else:
         PutMessage('char: command requires zero or one argument')
         PutMessage("char")
         PutMessage("char <newchar>")

def DataGrep(words, input, seslist):
   """DataGrep(words, seslist) -> None

   Searches through the databuffer for a regex, printing all matches
   in their entirety.
   This is a user command.
   """
   hooks.datagrep_command_hook.run((input, seslist))
   for ses in seslist:
      if len(words) < 2:
         PutMessage('datagrep: command requires one argument')
         PutMessage("datagrep <regex>")
         continue
      pat = string.join(words[1:])
      got = ses.databuf.grep(pat)
      PutMessage('datagrep: %d match(es) found.'%len(got))
      for g in got:
         PutMessage(g)

def DataGrepLines(words, input, seslist):
   """DataGrepLines(words, seslist) -> None

   Searches through the databuffer for a regex, printing out only
   the _lines_ which contain a match.
   This is a user command.
   """
   hooks.datagreplines_command_hook.run((input, seslist))
   for ses in seslist:
      if len(words) < 2:
         PutMessage("datagreplines: command requires (at least) one argument")
         PutMessage("datagreplines <regex>")
         continue
      pat = string.join(words[1:])
      build = ses.databuf.greplines(pat)
      PutMessage('datagreplines: %d match(es) found.'%len(build))
      for b in build:
         PutMessage(b)

def Echo(words, input, seslist):
   """Echo(words, input, seslist) -> None

   Will turn on and shut off echo.
   """
   if len(words) < 2:
      PutMessage("echo: command requires one argument")
      PutMessage("echo <on|off>")
      return

   if (words[1] == "on"):
      data.theapp.ui.OnEcho()
      PutMessage("echo on")
   else:
      data.theapp.ui.OffEcho()
      PutMessage("echo off")

def Report(words, input, seslist):
   """Report(words, input, seslist) -> None

   With no args, prints all reports
   Otherwise, creates a report which prints the line containing
   args 2+ to the file given by arg1, whenever said line is seen
   in mud output.
   This is a user command.
   """
   hooks.report_command_hook.run((input, seslist))
   for eachses in seslist:
      if len(words) == 1:
         # print all defined reports
         for (file, text) in eachses.reports:
            PutMessage('REPORT TO FILE %s: "%s"'%(file, text))
         PutMessage('report: %d reports defined.'%len(eachses.reports))
      elif len(words) == 2:
         # reject it.
         PutError("report: not enough arguments.")
         PutError("report <filename> <text string>")
      else:
         try:
            # define a new report
            filename = words[1]
            text = string.join(words[2:])
            file = app.get_appropriate_file(filename, 'a')
            eachses.reports.append((file, text))
            PutMessage('ok, "%s" now reported to file %s'% (text, filename))
         except IOError:
            PutError('report: unable to open file %s'%filename)

def Variable(words, input, seslist):
   """Variable(words, seslist) -> None

   Defines a variable
   This is a user command.
   """
   hooks.variable_command_hook.run((input, seslist))
   for ses in seslist:
      if len(words) == 1:
         # display all variables
         if len(ses.vars.keys()) == 0:
            PutMessage('variable: no variables defined...nil')
         else:
            PutMessage('variable: defined variables:')
            for var in ses.vars.keys():
               PutMessage("  " + ses.GetVarDisplayString(var))
         continue
      elif len(words) == 2:
         # display just the matching variables
         which = words[1]
         whichl = ses.Expand(which, ses.vars.keys())
         if not len(whichl):
            PutError("variable: that variable is not defined")
         else:
            for w in whichl:
               PutMessage("  " + ses.GetVarDisplayString(w))
      else:
         # more than one argument: define
         # a new variable for the current session
         name, expansion = app.split_braced(string.join(words[1:]))
         if name and (not expansion):
            # display just the matching variables
            Variable(['#var', name], [ses])
            continue
         ses.vars[name] = expansion
         if ses.verbose:
            PutMessage('variable: variable defined:')
            PutMessage("  " + ses.GetVarDisplayString(name))

def WriteFile(words, input, seslist):
   """WriteFile(words, seslist) -> None

   Writes aliases/actions/gags, etc to a file.
   This saves the local session and the global session in one fell
   swoop.
   This is a user command.
   """
   hooks.write_command_hook.run((input, seslist))
   for ses in seslist:
      try:
         if len(words) != 2:
            PutError("write: command requires at least one argument")
            PutError("write <filename>")
            return
         thefile = app.get_appropriate_file(words[1], 'w')

         # aliases
         for al in ses.aliases.keys():
            str = '#al {%s} {%s}\n'%(al, ses.aliases[al])
            thefile.write(str)
         # actions
         for ac in ses.actions.keys():
            str = '#ac {%s} {%s}\n'%(ac, ses.actions[ac])
            thefile.write(str)
         # substitutes
         for sub in ses.subs.keys():
            str = '#sub {%s} {%s}\n'%(sub, ses.subs[sub])
            thefile.write(str)
         # gags
         for gag in ses.gags:
            thefile.write('#gag ' + gag + '\n')
         # variables
         for var in ses.vars.keys():
            str = '#var {%s} {%s}\n'%(var, ses.vars[var])
            thefile.write(str)

         PutMessage('write: ok, session "%s" saved'%ses.name)
      except IOError:
         PutMessage('write: unable to open file %s'%thefile)

def Textin(words, input, seslist):
   """Textin(words, seslist) -> None

   Sends the text to the mud from a file.
   This is a user command.
   """
   hooks.textin_command_hook.run((input, seslist))
   oldses = data.currsession

   for ses in seslist:
      if len(words) != 2:
         PutError("textin: command requires one argument")
         PutError("textin <filename>")
         data.currsession = oldses
         return

      # if they give us a full path name, we try to open it.
      # otherwise we prepend the datadir to the argument
      if words[1][0] == os.sep:
         filename = words[1]
      else:
         filename = data.datadir + words[1]

      try:
         f = open(filename, 'r')
      except IOError:
         PutError('textin: unable to open text file: ' + filename)
      else:
         # ok, got it open.  do the textin stuff...
         PutMessage('textin: ok, sending commands...')
         thelist = f.readlines()
         data.currsession = ses
         for line in thelist:
            if line:
               data.theapp.HandleUserInput(line)

   data.currsession = oldses

def ParseFile(ofile, input, seslist):
   """ParseFile(ofile, seslist) -> None

   Read in aliases/actions/gags/substitutes from a file.
   This is a user command.
   """
   hooks.read_command_hook.run((input, seslist))
   for ses in seslist:
      try:

         if len(ofile) != 2:
            PutError("read: command requires one argument")
            PutError("read <filename>")
            return

         # open a file for reading
         thefile = app.get_appropriate_file(ofile[1], 'r')

         thelist = thefile.readlines()
         other_count = al_count = ac_count = sub_count = gag_count = var_count = 0

         # set quiet mode which prevents PutMessage from printing
         # stuff--because it'd print a lot of stuff here.
         ses.quiet_mode = 1

         # go through the file, adding actions, aliases
         # etc where appropriate
         for s in thelist:
            dispatch_command(s, seslist)

            words = string.split(s)
            if len(words) > 2:
               # alias
               if words[0] == '#al':
                  al_count = al_count + 1
               # action
               elif words[0] == '#ac':
                  ac_count = ac_count + 1
               # substitute
               elif string.find('#substitute', words[0]) == 0:
                  sub_count = sub_count + 1
               # gag
               elif string.find('#gag', words[0]) == 0:
                  gag_count = gag_count + 1
               #variable
               elif string.find('#variable', words[0]) == 0:
                  var_count = var_count + 1
               else:
                  other_count = other_count + 1

         ses.quiet_mode = 0

         PutMessage('read: ok.')
         PutMessage(string.join([str(al_count), "aliases loaded."]))
         PutMessage(string.join([str(ac_count), "actions loaded."]))
         PutMessage(string.join([str(sub_count), "substitutes loaded."]))
         PutMessage(string.join([str(var_count), "variables loaded."]))
         PutMessage(string.join([str(gag_count), "gags loaded."]))
         PutMessage(string.join([str(other_count), "other things loaded."]))

      except IOError, arg:
         PutError(string.join(["read: unable to open input file:",
                              ofile[1], str(arg)]))

def CR(words, input, seslist):
   """CR(seslist) -> None

   Sends a carriage return from teh current session to its connection.
   Useful for aliases that want to send carriage returns.
   This is a user command.
   """
   hooks.cr_command_hook.run((seslist,))
   for ses in seslist:
      if ses.connected:
         ses.WriteTo('\n')


def Log(words, input, seslist):
   """Log(words, seslist) -> None

   Starts a log file for the current session.
   This is a user command.
   """
   hooks.log_command_hook.run((input, seslist))
   # check for bad argument like #all #log myfile
   if len(seslist) > 1:
      PutError( 'can\'t log more than one session to the same file!')
      return
   for ses in seslist: # pseudo for-loop through a one-element list
      if len(words) == 1:
         # cancel an in-progress log
         if ses.logging:
            PutMessage('log: ok, closing logfile '+ses.logfile.name)
            ses.logging = 0
            ses.logfile = None
            return
         else:
            # they aren't logging already, so they must have screwed up
            PutError('log: log what?')
            return
      if len(words) > 2:
         PutError('log: too many arguments')
         return
      if not ses.connected:
         PutMessage("log: this session is not connected--nothing to log.")
         return
      # if they give us a full path name, we try to open it.
      # otherwise we prepend the datadir to the argument
      if words[1][0] == os.sep:
         fullfile = words[1]
      else:
         fullfile = data.datadir + words[1]

      try:
         f = open(fullfile, 'a')
      except IOError:
         PutError('log: unable to open log file: ' + fullfile)
      else:
         # ok, got it open.  set up the logging stuff...
         PutMessage('log: ok, logging...')
         ses.logging = 1
         ses.logfile = f

def Quit(words, input, seslist):
   """Quit() -> None

   Quits lyntin.
   This is a user command.
   """
   PutMessage("quit: you'll be back...")
   # run the shutdown hook.
   hooks.shut_down_lyntin_hook.run()
   if data.numsessions:
      data.clear_all()

   # call CloseUI
   data.theapp.ui.CloseUI()

   sys.exit(0)

def KillAll(words,input,seslist):
   """KillAll() -> None

   Wipes clean all active session removing actions/gags/subs...
   This is a user command.
   """
   hooks.killall_command_hook.run((input, seslist))
   for ses in data.sessionlist:
      ses.Clear()
      PutMessage('killall: session "'+ses.name+'" cleared.')


def Action(words, input, seslist):
   """Action(input, seslist) -> None

   With no arguments, prints all the actions.
   With one argument, prints matching action(s).
   Otherwise, creates an action named arg1 which expands to the
   rest of the args.
   This is a user command.
   """
   hooks.action_command_hook.run((input, seslist))
   for eachses in seslist:
      count = 0
      trigger, response = cmdparse.split_action(input) 

      if trigger and response:
         eachses.add_action(trigger, response)
         PutMessage('ok, {%s} now triggers {%s}'%(trigger, response))

      elif trigger:
         # print action definition
         expanded = eachses.ExpandAction(trigger)
         if expanded:
            count = count + len(expanded)
            for ac in expanded:
               PutMessage('action: {%s}={%s}'%(ac, eachses.actions[ac]))

         if not count:
            PutMessage("action: That action is not defined")

      else: # print all current actions
         for ac in eachses.actions.keys():
            count = count + 1
            PutMessage('action {%s} = {%s}'%(ac, eachses.actions[ac]))
         if count == 0:
            PutMessage("action: No actions defined.")

def UnAction(words, input, seslist):
   """UnAction(words, seslist) -> None

   Removes all matching actions.
   This is a user command.
   """
   hooks.unaction_command_hook.run((input, seslist))
   for ses in seslist:
      if len(words) < 2:
         PutError('unaction: command requires one argument')
         PutError('unaction <action-name>')
         return

      un = string.join(words[1:])
      # remove braces if necessary
      if un[0] == '{' and un[-1] == '}':
         un = un[1:-1]
      acs = ses.ExpandAction(un)
      if acs:
         for ac in acs:
            # kill!!!
            del ses.actions[ac]
         # remove from action_list
         # FIXME - this causes an error--out of index range.
         for i in xrange(len(ses.action_list) - 2):
            if ses.action_list[i][0] in acs:
               del ses.action_list[i]


         PutMessage('unaction: ' + str(len(acs)) + ' actions removed')
      else:
         PutMessage('unaction: that action is not defined')

def Alias(words, input, seslist):
   """Alias(words, seslist) -> None

   With no arguments, prints all the aliases.
   With one argument, prints matching alias definitions.
   With many arguments, defines an alias named the first argument
   which expands to the rest of the arguments.
   This is a user command.
   """
   hooks.alias_command_hook.run((input, seslist))
   for ses in seslist:
      count = 0

      if len(words) > 2:
         name, expansion = app.split_braced(string.join(words[1:]))
         ses.aliases[name] = expansion
         PutMessage('ok, {%s} aliases {%s}'%(name, expansion))

      elif len(words) == 2:
         # print alias definition
         name = words[1]
         expanded = ses.ExpandAlias(name)
         if expanded:
            count = count + len(expanded)
            for al in expanded:
               PutMessage('alias: {%s} = {%s}'%(al, ses.aliases[al]))
         if not count:
            PutMessage("alias: that alias is not defined")

      else: 
         # print all current aliases
         for al in ses.aliases.keys():
            count = count + 1
            PutMessage('alias: {%s} = {%s}'%(al, ses.aliases[al]))
         if count == 0:
            PutMessage("alias: no aliases defined.")

def Help(words, input, seslist):
   """Help(words, seslist) -> None

   Eventually, this should call hooks for things that aren't
   defined in help.print_help.  Then folks can build modules and
   add help to their modules without putting new help files in the
   help directory.  Later though.
   This is a user command.
   """
   import os

   helpdir = data.initdir + "help"
   PutMessage('::lyntin help::')
   if words == ['help']:
      PutMessage("Topics Available:")
      the_list = os.listdir(helpdir)
      the_list.sort()
      new_line = '   '
      count = 1
      for mem in the_list:
         if len(mem) > 4 and mem[-4:] == ".hlp":
            new_line = new_line + string.ljust(mem[:-4], 16)
            if (count % 3) == 0:
               PutMessage(new_line)
               new_line = '   '
            count = count + 1
      PutMessage(new_line)
      return

   for mem in words[1:]:
      try:
         f = open(helpdir + "/" + mem + ".hlp", "r")
         lines = f.readlines()
         f.close()
         PutRaw(string.join(lines, ""))
      except:
         PutMessage(mem + " is not a valid help topic.")

def History(words, input, seslist):
   """History(words, seslist) -> None

   With one numeric argument, set history size.
   With no arguments, prints last histsize commands.
   This is a user command.
   """
   hooks.history_command_hook.run((input, seslist))
   for ses in seslist:
      if len(words) > 2:
         PutError('history: too many arguments')
         continue
      elif len(words) == 2:
         # try to set a new history size
         try:
            num = string.atoi(words[1])
         except ValueError:
            PutError('history: invalid argument')
            continue
         else:
            if num == 0:
               PutError('history: can\'t set history size to nothing.')
               continue
            data.histsize = num
            PutMessage('history: ok, history size set to '+str(num))
      # print last histsize history entries
      else:
         n = len(data.history)
         if n == 0:
            PutMessage('history: no history yet...')
            continue
         m = min([data.histsize, len(data.history)])
         PutMessage('History:')
         for i in range(m - 1, -1, -1):
            PutMessage(str(i)+' '+ str(data.history[i])[:-1])

def Info(words,input,seslist):
   """Info(seslist) -> None

   Prints session info to the client.
   This is a user command.
   """
   for ses in seslist:
      PutMessage('Session: ' + ses.name)
      PutMessage(repr(len(ses.actions.keys())) + ' actions.')
      PutMessage(repr(len(ses.aliases.keys())) + ' aliases.')
      PutMessage(repr(len(ses.gags)) + ' gags.')
      PutMessage(repr(len(ses.vars.keys())) + ' variables.')

      if ses.verbose:
         PutMessage('Verbose is on.')
      else:
         PutMessage('Verbose is off.')

      if ses.speedwalk:
         PutMessage('Speedwalking is on.')
      else:
         PutMessage('Speedwalking is off.')

      if ses.ticker:
         PutMessage('Ticker is on; ' + repr(ses.ticklen) + ses.tickaction)
      else:
         PutMessage('Ticker is off.')

def UnAlias(words, input, seslist):
   """UnAlias(words, seslist) -> None

   Removes all matching aliases.
   This is a user command.
   """
   hooks.unalias_command_hook.run((input, seslist))
   for ses in seslist:
      if len(words) != 2:
         PutError('unalias: command requires one argument')
         PutError('unalias <aliasname>')
         return

      als = ses.ExpandAlias(words[1])
      if als:
         for al in als:
            # kill!!!
            del ses.aliases[al]
         PutMessage('unalias: ' + str(len(als)) + ' aliases removed') 
      else:
         PutError('unalias: that alias is not defined')

def Gag(words, input, seslist):
   """Gag(words, seslist) -> None

   Cease displaying any text from the mud which contains the
   given string.  Useful for shutting up spammers or spammy
   events.
   This is a user command.
   """
   hooks.gag_command_hook.run((input, seslist))
   for ses in seslist:
      if len(words) < 2:
         # print all gags
         if len(ses.gags) == 0:
            PutMessage('gag: no gags are defined')
         else:
            for gag in ses.gags:
               PutMessage('gag: gag ' + gag)
         continue
      gagwhat = string.join(words[1:])

      # add string to current session's gags
      ses.gags = ses.gags + [gagwhat]
      PutMessage('ok, "' + gagwhat + '" is now gagged')

def UnGag(words, input, seslist):
   """UnGag(words, seslist) -> None

   Removes the given string from the session's gags.
   This is a user command.
   """
   hooks.ungag_command_hook.run((input, seslist))
   for ses in seslist:
      if len(words) < 2:
         PutError('ungag: command requires at least one argument')
         PutError('ungag <gagname>')
         return
      ungagwhat = string.join(words[1:])
      ungagwhatlist = ses.Expand(ungagwhat, ses.gags)
      # remove ungagwhat from the current session's gags
      for g in ungagwhatlist:
         if ses.gags.count(g) > 0:
            ses.gags.remove(g)
            PutMessage('ungag: ok, "' + g + '" is no longer gagged')
      if not ungagwhatlist:
         PutError('ungag: that gag is not defined')

def Substitute(words, input, seslist):
   """Substitute(words, seslist) -> None

   Anytime we see a certain string from the mud,
   substitute an alternate string for it.
   This is a user command.
   """
   hooks.substitute_command_hook.run((input, seslist))
   for ses in seslist:
      if len(words) < 3:
         PutError('substitute: command requires at least two arguments')
         continue
      pattern, replacement = app.split_braced(string.join(words[1:]))
      ses.subs[pattern] = replacement
      PutMessage('ok, ' + pattern + ' is now replaced by ' + replacement)

def UnSubstitute(words, input, seslist):
   """UnSubstitute(words, seslist) -> None

   Removes the substitute from the current session.
   This is a user command.
   """
   hooks.unsubstitute_command_hook.run((input, seslist))
   for ses in seslist:
      if len(words) < 2:
         PutError('unsubstitue: command requires at least one argument')
         return
      unlist = ses.Expand(string.join(words[1:]), ses.subs.keys())
      for sub in unlist:
         del ses.subs[sub]
      PutMessage("unsubstitute: " + str(len(unlist)) + ' substitutes removed')

def Clear(words, input, seslist):
   """Clear(seslist) -> None

   Clears the session of aliases, actions, subs, vars, and gags.
   This is a user command.
   """
   hooks.clear_command_hook.run((seslist,))
   for ses in seslist:
      ses.aliases = {}
      ses.actions = {}
      ses.action_list = []
      ses.subs = {}
      ses.vars = {}
      ses.gags = []
      PutMessage('clear: session ' + ses.name + ' cleared')


def Tickset(words, input, seslist):
   """Tickset(words, seslist) -> None

   With no arguments, synchronize tick start ot current time.
   With arg "on" set ticker on.  With arg "off" set ticker off.
   This is a user command.
   """
   hooks.tickset_command_hook.run((input, seslist))
   if len(words) == 1:
      # synchronize
      for ses in seslist:
         if not ses.ticker:
            PutMessage('tickset: ticker is off')
            return
         PutMessage('tickset: resetting ticker...')
         ses.lasttickclock = 0
         ses.lastclock = time.time()
         ses.warnedtick = 0

   else:
      if words[1] == 'on':
         # turn on ticker
         for ses in seslist:
            if not ses.ticker:
               ses.ticker = 1
               ses.lasttickclock = 0
               ses.lastclock = time.time()
               ses.warnedtick = 0
               PutMessage('tickset: ticker is now on (ticklen = %d) (tickaction = %s)'%(ses.ticklen, ses.tickaction))
            else:
               PutMessage('tickset: ticker is already on!')

      elif words[1] == 'off':
         # turn off ticker
         for ses in seslist:
            ses.ticker = 0
            PutMessage('tickset: ticker is now off (ticklen = %d) (tickaction = %s)'%(ses.ticklen, ses.tickaction))

      elif words[1] == 'clear':
         for ses in seslist:
            ses.ticker = 0
            ses.tickaction = ''
            PutMessage('tickset: ticklen and tickaction cleared.')

      elif words[1] == 'toggle':
         # toggle ticker status
         for ses in seslist:
            ses.ticker = not ses.ticker
            if ses.ticker:
               ses.lasttickclock = 0
               ses.lastclock = time.time()
               ses.warnedtick = 0
               PutMessage('tickset: ticker is now on (ticklen = %d) (tickaction = %s)'%(ses.ticklen, ses.tickaction))
            else:
               PutMessage('tickset: ticker is now off (ticklen = %d) (tickaction = %s)'%(ses.ticklen, ses.tickaction))

      elif words[1] == 'status':
         for ses in seslist:
            PutMessage('tickset: ticker status:')
            if ses.ticker:
               PutMessage('Ticker is on')
               PutMessage('Ticklength = %d'%ses.ticklen)
               PutMessage('Tickaction = %s'%ses.tickaction)
               PutMessage('Time to next tick = %d'%(ses.ticklen - ses.lasttickclock))
            else:
               PutMessage('Ticker is off')
               PutMessage('Ticklength = %d'%ses.ticklen)
               PutMessage('Tickaction = %s'%ses.tickaction)
               PutMessage('Time to next tick = %d'%(ses.ticklen - ses.lasttickclock))

      else:
         # set ticklength
         for ses in seslist:
            try:
               ses.ticklen = string.atoi(words[1])
               PutMessage('tickset: tick length set to %d'%ses.ticklen)
            except ValueError:
               ses.tickaction = string.join(words[1:], " ")
               PutMessage('tickset: tickaction set to %s'%ses.tickaction)


def Tick(words, input, seslist):
   """Tick(words, seslist) -> None

   Display tick status.
   This is a user command.
   """
   hooks.tick_command_hook.run((input, seslist))
   for ses in seslist:
      if not ses.ticker:
         PutMessage('tick: ticker is off')
         return
      PutMessage('tick: there are %d seconds to the next tick!!'% \
              (ses.ticklen - ses.lasttickclock))

def Version(words, input, seslist):
   """Version(words, input, seslist) -> None

   Prints out the version.
   """
   import data
   PutMessage(data.version)


def Verbose(words, input, seslist):
   """Verbose(seslist) -> None

   Toggles whether or not to be verbose.
   This is a user command.
   """
   for ses in seslist:
      ses.verbose = not ses.verbose
      if ses.verbose:
         PutMessage('verbose: verbose mode now on.')
      else:
         PutMessage('verbose: verbose mode now off.')


def TickerUpdate(seslist):
   """TickerUpdate(seslist) -> None

   Called periodically to see if tick-related events need handling.
   Informs the user when ticks are approaching and when they occur.
   """
   for ses in seslist:
      ses.lasttickclock = ses.lasttickclock + ses.lastclockdelta
      if ses.lasttickclock > (ses.ticklen - ses.tickwarn):
         if not ses.warnedtick:
            ses.warnedtick=1
            warntext='tickerupdate: %d seconds to tick!!!'%ses.tickwarn
            PutMessage(warntext)
            hooks.ticker_warn_hook.run((ses,))
      if ses.lasttickclock > ses.ticklen:
         PutMessage('tickerupdate: tick!!!')
         hooks.ticker_pass_hook.run((ses,))
         if ses.tickaction:
            data.theapp.HandleUserInput(ses.tickaction)

         ses.lasttickclock=0
         ses.warnedtick=0

###
### This function adds all the standard commands to data.theapp.commands
###

def init_player():
   import player
   data.theapp.AddCommand("^char", player.Char)
   data.theapp.AddCommand("^clear", player.Clear)
   data.theapp.AddCommand("^cr", player.CR)
   data.theapp.AddCommand("^quit", player.Quit)
   data.theapp.AddCommand("action", player.Action)
   data.theapp.AddCommand("alias", player.Alias)
   data.theapp.AddCommand("command", player.AddCommand)
   data.theapp.AddCommand("databuffer", player.DataBuffer)
   data.theapp.AddCommand("datagrep", player.DataGrep)
   data.theapp.AddCommand("datagreplines", player.DataGrepLines)
   data.theapp.AddCommand("echo", player.Echo)
   data.theapp.AddCommand("gag", player.Gag)
   data.theapp.AddCommand("help", player.Help)
   data.theapp.AddCommand("history", player.History)
   data.theapp.AddCommand("import", player.LynImport)
   data.theapp.AddCommand("info", player.Info)
   data.theapp.AddCommand("killall", player.KillAll)
   data.theapp.AddCommand("log", player.Log)
   data.theapp.AddCommand("printcommands", player.PrintCommands)
   data.theapp.AddCommand("read", player.ParseFile)
   data.theapp.AddCommand("report", player.Report)
   data.theapp.AddCommand("session", player.Ses)
   data.theapp.AddCommand("showme", player.Showme)
   data.theapp.AddCommand("speedwalk", player.SpeedWalk)
   data.theapp.AddCommand("substitute", player.Substitute)
   data.theapp.AddCommand("textin", player.Textin)
   data.theapp.AddCommand("tick", player.Tick)
   data.theapp.AddCommand("tickset", player.Tickset)
   data.theapp.AddCommand("unaction", player.UnAction)
   data.theapp.AddCommand("unalias", player.UnAlias)
   data.theapp.AddCommand("uncommand", player.UnCommand)
   data.theapp.AddCommand("ungag", player.UnGag)
   data.theapp.AddCommand("unsubstitute", player.UnSubstitute)
   data.theapp.AddCommand("variable", player.Variable)
   data.theapp.AddCommand("verbose", player.Verbose)
   data.theapp.AddCommand("version", player.Version)
   data.theapp.AddCommand("write", player.WriteFile)



# Local variables:
# mode:python
# py-indent-offset:3
# tab-width:3
# End:
