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

import string, regex, sys, regsub, socket, time
import data, mud, app, hooks, cmdparse, os

# delay import of user module until we have more state
user = None

# exceptions
class SesError: pass

command_table = {}

# parse command intended for client, (i.e. one prefaced by data.ltchar)
# allow abbreviations for most commands
def DispatchCommand(input, seslist):
    """DispatchCommand(input, seslist) -> None

    input - the input string
    seslist - list of session objects

    parse command intended for the client, (i.e. one prefaced by
    data.ltchar)
    allows abbreviations for most commands.
    """

## 2.0-JA  Because input is needed to run the hook anyway, we're sending
##         both input and words to the functions.

    import data

    if not input: return
    # strip any data.ltchar from the front
    if input[0] == data.ltchar:
        input = input[1:]
    if not seslist:
        raise SesError, 'No session supplied'

    if len(input) <= 0:
        return

    words = string.split(input)

    # execute some python code?
    if input[0] == '@':
        hooks.exec_user_code_hook.run((input,))
        input = input[1:]
        exec input in user.__dict__
        return

    # for commands in data.theapp.commands listing
    clist = data.theapp.commands.keys()
    for mem in clist:
        # this means it has to be matched exactly
        if mem[0] == "^":
            if regex.search(mem, words[0]) != -1:
                return data.theapp.commands[mem](words, input, seslist)
        else:
            if string.find(mem, words[0]) == 0:
                return data.theapp.commands[mem](words, input, seslist)

    # unrecognized command
    Putline('error: command is not defined --%s--'%words[0])
    return

###
### Player library functions
###

def ExpandCommand(s, list):
    """ExpandCommand(s, list) -> string

    Inputs a string and a list and returns a list of all the elements
    in the list that match the string.
    """
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

def SetSes(ses):
    """SetSes(ses) -> None

    Sets the active session.  Run set_session hook *before*
    the actual switch
    """
    # pass old and new sessions to the set_session hook
    hooks.set_session_hook.run((data.currsession, ses))
    data.currsession = ses
    ans = 'ok, session "' + ses.name + '" activated.'
    Putline(ans)

def Prompt():
    """Prompt() -> None

    Prints a prompt.
    """
    data.theapp.ui.Prompt()

def TimeUpdate(seslist):
    """TimeUpdate(seslist) -> None

    Checks the current time and does time-related stuff (via the ticker).
    """
    for ses in seslist:
        click = time.time()
        ses.lastclockdelta = click - ses.lastclock
        if ses.ticker:
            TickerUpdate((ses,))
        ses.lastclock = click

def ImportUser():
    """ImportUser() -> None

    Want to delay this.
    (i have no clue what this means.)
    """
    global user
    user = GetUserModule()

def GetUserModule():
    """GetUserModule() -> None

    Imports the user module and returns it.
    """
    import user
    return user

def Putline(line):
    """Putline(line) -> None

    Prints a message from the client to the player prepending
    a "#".  This is Lyntin output. 
    " # studid emacs
    """
    data.theapp.ui.Putline(line)

def PutUntouchedLine(line):
    """PutUntouchedLine(line) -> None
    """
    data.theapp.ui.PutUntouchedLine(line)
    
def PutReallyUntouchedLine(line):
    """PutReallyUntouchedLine(line) -> None
    """
    data.theapp.ui.PutReallyUntouchedLine(line)


###
### User standard commands
###

def PrintCommands(words, input, seslist):
    """PrintCommands(words, input, seslist) -> None

    Prints all the commands to the screen in a pretty list.
    """
    the_list = data.theapp.ReturnCommandHash().keys()
    the_list.sort()
    new_line = 'Commands:\n   '
    count = 1
    for mem in the_list:
        new_line = new_line + string.ljust(mem, 16)
        if (count % 3) == 0:
            PutUntouchedLine(new_line)
            new_line = '   '
        count = count + 1
    PutUntouchedLine(new_line + "\n")
    return

def AddCommand(words, input, seslist):
    """AddCommand(words, input, seslist) -> None

    Adds a command to the client.  This is a user command.
    If they don't pass in enough args, we print out the command
    list--we might want to change this later, but it makes 
    the 'command' command more like alias and action.
    """
    if len(words) > 2:
        # FIXME - we actually have to go out and find the command
        # mentioned.  should be in notation /path/module.function
        # or something similar.
        data.theapp.AddCommand(words[1], words[2])
    else:
        # raise error? or something because there aren't enough
        # arguments.
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

    acs = ExpandCommand(un, data.theapp.commands)

    if acs:
        for ac in acs:
            data.theapp.RemoveCommand(ac)

        Putline('uncommand: ' + str(len(acs)) + ' commands removed')
    else:
        Putline('uncommand: that command is not defined')


def LynImport(words, input, seslist):
    """LynImport(words, input, seslist) -> None

    Imports a module which adds itself to the app and such.
    This is a user command.  If the module has already
    been imported, then it gets reloaded.
    """
    import sys
    Putline("trying to import " + words[1])

    try:
        if sys.modules.has_key(words[1]):
            reload(sys.modules[words[1]])
            Putline("import (actually--we reloaded) successful.")
        else:
            exec ("import " + words[1])
            Putline("import successful.")
    except ImportError:
        Putline(words[1] + " module does not exist.")
    except:
        from sys import exc_info
        from traceback import format_exception

        info = exc_info()
        exc_class = info[0]
        Putline(string.join(format_exception(info[0], info[1], info[2]), ""))
    return

def Showme(words, input, seslist):
    """Showme(words, seslist) -> None

    Prints the words to the clients display
    This is a user command.
    """
    hooks.showme_command_hook.run((input, seslist))
    for ses in seslist:
        if len(words) == 1:
            Putline('showme: showme what?')
            return
        # only display if this is the current session
        if ses is data.currsession:
            PutUntouchedLine(string.join(words[1:]))

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
        Putline("sessions: ")
    elif len(to) >= 3:

        # see if there's an existing session with the same name
        for ses in data.sessionlist:
            if ses.name == to[0]:
                Putline('ses: session "'+ses.name+'" already exists.')
                return

        try:
            # extract parameters
            name = to[0]
            host = to[1]
            port = string.atoi(to[2])
        except ValueError:
            Putline('ses: bad arguments: #session sesname hostname port')
            return

        try:
            # try to connect with the given parameters
            Putline("ses: Trying to connect...")
            thisses = data.UserSession(name,host,port)
            
        except socket.error:
            Putline("ses: Unable to connect!")
            # pass the session name to the connect_failed hook
            hooks.connect_failed_hook.run((name, host, port))
            
        except ValueError:
            Putline('ses: illegal port number: %d'%port)
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
        Putline("ses: requires 3 arguments")
        Putline("ses <name> <address> <port>")

def SpeedWalk(words, input, seslist):
    """SpeedWalk(seslist) -> None

    Toggles speedwalking.
    This is a user command.
    """
    hooks.speedwalk_command_hook.run((seslist,))
    for ses in seslist:
        ses.speedwalk = not ses.speedwalk
        if ses.speedwalk:
            Putline('speedwalk: speedwalking is now ON')
        else:
            Putline('speedwalk: speedwalking is now OFF')

def DataBuffer(words, input, seslist):
    """DataBuffer(words, seslist) -> None

    With one argument, sets the size of the session's databuffer.
    With no arguments, it displays the databuffer.
    This is a user command.
    """
    hooks.databuffer_command_hook.run((input, seslist))
    for ses in seslist:
        if len(words) < 2:
            Putline('databuffer: databuffer size is %d'%ses.databuf.size)
            continue
        try:
            num = string.atoi(words[1])
        except ValueError:
            Putline('databuffer: invalid argument')
        else:
            ses.databuf.resize(num)
            Putline('databuffer: databuffer size set to %d'%num)

def Char(words, input, seslist):
    """Char(words, seslist) -> None

    with no arguments, prints the lyntin character.
    With one argument, sets the lyntin character.
    This is a user command.
    """
    hooks.char_command_hook.run((input, seslist))
    for ses in seslist:
        if len(words) == 1:
            PutReallyUntouchedLine("CURRENT LYNTIN CHARACTER: '%s'\n"%data.ltchar)
            if not data.currsession.connected:
                Prompt()
        elif len(words) == 2:
            c = words[1]
            if len(c) != 1:
                Putline('char: %s is not a single character!'%c)
            else:
                data.ltchar = c
                PutReallyUntouchedLine("OK, LYNTIN CHARACTER SET TO '%s'\n"%c)
                if not data.currsession.connected:
                    Prompt()
        else:
            Putline('char: command requires zero or one argument')
            Putline("char")
            Putline("char <newchar>")

def DataGrep(words, input, seslist):
    """DataGrep(words, seslist) -> None

    Searches through the databuffer for a regex, printing all matches
    in their entirety.
    This is a user command.
    """
    hooks.datagrep_command_hook.run((input, seslist))
    for ses in seslist:
        if len(words) < 2:
            Putline('datagrep: command requires one argument')
            Putline("datagrep <regex>")
            continue
        pat = string.join(words[1:])
        got = ses.databuf.grep(pat)
        for g in got:
            PutReallyUntouchedLine(g)
        Putline('datagrep: %d match(es) found.'%len(got))

def DataGrepLines(words, input, seslist):
    """DataGrepLines(words, seslist) -> None

    Searches through the databuffer for a regex, printing out only
    the _lines_ which contain a match.
    This is a user command.
    """
    hooks.datagreplines_command_hook.run((input, seslist))
    for ses in seslist:
        if len(words) < 2:
            Putline("datagreplines: command requires (at least) one argument")
            Putline("datagreplines <regex>")
            continue
        pat = string.join(words[1:])
        build = ses.databuf.greplines(pat)
        for b in build:
            PutUntouchedLine(b)
        Putline('datagreplines: %d match(es) found.'%len(build))

def Echo(words, input, seslist):
    """Echo(words, input, seslist) -> None

    Will turn on and shut off echo.
    """
    if len(words) < 2:
        Putline("echo: command requires one argument")
        Putline("echo <on|off>")
        return

    if (words[1] == "on"):
        data.theapp.ui.OnEcho("no")
        Putline("echo on")
    else:
        data.theapp.ui.OffEcho("no")
        Putline("echo off")

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
                PutUntouchedLine('#REPORT TO FILE %s: "%s"'%(file, text))
            Putline('report: %d reports defined.'%len(eachses.reports))
        elif len(words) == 2:
            # reject it.
            Putline("report: not enough arguments.")
            Putline("report [tofile] [text string]")
        else:
            try:
                # define a new report
                filename = words[1]
                text = string.join(words[2:])
                file = app.GetAppropriateFile(filename, 'a')
                eachses.reports.append((file, text))
                PutUntouchedLine('OK, "%s" NOW REPORTED TO FILE %s'% \
                                 (text, file))
            except IOError:
                Putline('report: unable to open file %s'%filename)
                    
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
                Putline('variable: no variables defined...nil')
            else:
                Putline('variable: defined variables:')
                for var in ses.vars.keys():
                    display = ses.GetVarDisplayString(var)
                    PutUntouchedLine(display)
            continue
        elif len(words) == 2:
            # display just the matching variables
            which = words[1]
            whichl = ses.Expand(which, ses.vars.keys())
            if not len(whichl):
                Putline("variable: that variable is not defined")
            else:
                for w in whichl:
                    display = ses.GetVarDisplayString(w)
                    PutUntouchedLine(display)
        else:
            # more than one argument: define
            # a new variable for the current session
            name, expansion = app.SplitBraced(string.join(words[1:]))
            if name and (not expansion):
                # display just the matching variables
                Variable(['#var', name], [ses])
                continue
            ses.vars[name] = expansion
	    if ses.verbose:
                Putline('variable: variable defined:')
                display = ses.GetVarDisplayString(name)
                PutUntouchedLine(display)

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
                Putline("write: command requires at least one argument")
                Putline("write <filename>")
                return
            thefile = app.GetAppropriateFile(words[1], 'w')

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

            Putline('write: ok, session "%s" saved'%ses.name)
        except IOError:
            Putline('write: unable to open file %s'%thefile)

def Textin(words, input, seslist):
    """Textin(words, seslist) -> None

    Sends the text to the mud from a file.
    This is a user command.
    """
    hooks.textin_command_hook.run((input, seslist))
    oldses = data.currsession
    
    for ses in seslist:
        if len(words) != 2:
            Putline("textin: command requires one argument")
            Putline("textin <filename>")
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
            Putline('textin: unable to open text file: ' + filename)
        else:
            # ok, got it open.  do the textin stuff...
            Putline('textin: ok, sending commands...')
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
                Putline("read: command requires one argument")
                Putline("read <filename>")
                return
            
            # open a file for reading
            thefile = app.GetAppropriateFile(ofile[1], 'r')
            
            thelist = thefile.readlines()
            al_count = ac_count = sub_count = gag_count = var_count = 0

            # go through the file, adding actions, aliases
            # etc where appropriate
            for s in thelist:
                words = string.split(s)
                if len(words) > 2:
                    # alias
                    if words[0] == '#al':
                        al_count = al_count + 1
                        name, expansion = \
                              app.SplitBraced(string.join(words[1:]))
                        ses.aliases[name] = expansion
                    # action
                    elif words[0] == '#ac':
                        ac_count = ac_count + 1
                        trigger, response = cmdparse.SplitAction(s)
                        
                        ses.add_action(trigger, response)
                    # substitute
                    elif string.find('#substitute', words[0]) == 0:
                        sub_count = sub_count + 1
                        pat, repl = app.SplitBraced(string.join(words[1]))
                        ses.subs[pat] = repl
                    # gag
                    elif string.find('#gag', words[0]) == 0:
                        if len(words) > 1:
                            gag_count = gag_count + 1
                            ses.gags = ses.gags + \
                                                    [string.join(words[1:])]
                    #variable
                    elif string.find('#variable', words[0]) == 0:
                        if len(words) > 2:
                            var_count = var_count + 1
                            name, val = \
                                  app.SplitBraced(string.join(words[1:]))
                            ses.vars[name] = val


            Putline('read: ok.')
            Putline(string.join([str(al_count), "aliases loaded."]))
            Putline(string.join([str(ac_count), "actions loaded."]))
            Putline(string.join([str(sub_count), "substitutes loaded."]))
            Putline(string.join([str(var_count), "variables loaded."]))
            Putline(string.join([str(gag_count), "gags loaded."]))

        except IOError, arg:
            Putline(string.join(["read: unable to open input file:",
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
        Putline( 'can\'t log more than one session to the same file!')
        return
    for ses in seslist: # pseudo for-loop through a one-element list
        if len(words) == 1:
            # cancel an in-progress log
            if ses.logging:
                Putline('log: ok, closing logfile '+ses.logfile.name)
                ses.logging = 0
                ses.logfile = None
                return
            else:
                # they aren't logging already, so they must have screwed up
                Putline('log: log what?')
                return
        if len(words) > 2:
            Putline('log: too many arguments')
            return
        if not ses.connected:
            Putline("log: this session is not connected--nothing to log.")
            return
        # if they give us a full path name, we try to open it.
        # otherwise we prepend the datadir to the argument
        if words[1][0] == os.sep:
            fullfile = words[1]
        else:
            fullfile = data.datadir + words[1]

        try:
            f = open(fullfile, 'w')
        except IOError:
            Putline('log: unable to open log file: ' + fullfile)
        else:
            # ok, got it open.  set up the logging stuff...
            Putline('log: ok, logging...')
            ses.logging = 1
            ses.logfile = f

def Quit(words, input, seslist):
    """Quit() -> None

    Quits lyntin.
    This is a user command.
    """
    Putline("quit: you'll be back...")
    # run the shutdown hook.
    hooks.shut_down_lyntin_hook.run()
    if data.numsessions:
        data.ClearAll()

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
        Putline('killall: session "'+ses.name+'" cleared.')


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
        trigger, response = cmdparse.SplitAction(input) 
    
        if trigger and response:
            eachses.add_action(trigger, response)
            PutUntouchedLine('#OK, {%s} NOW TRIGGERS {%s}'%(trigger, response))

        elif trigger:
            # print action definition
            expanded = eachses.ExpandAction(trigger)
            if expanded:
                count = count + len(expanded)
                for ac in expanded:
                    PutUntouchedLine('#ac {%s}={%s}'%(ac, eachses.actions[ac]))

            if not count:
                Putline("action: That action is not defined")

        else: # print all current actions
            for ac in eachses.actions.keys():
                count = count + 1
                PutUntouchedLine('#ac {%s}={%s}'%(ac, eachses.actions[ac]))
            if count == 0:
                Putline("action: No actions defined.")

def UnAction(words, input, seslist):
    """UnAction(words, seslist) -> None

    Removes all matching actions.
    This is a user command.
    """
    hooks.unaction_command_hook.run((input, seslist))
    for ses in seslist:
        if len(words) < 2:
            Putline('unaction: command requires one argument')
            Putline('unaction <action-name>')
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
            for i in xrange(len(ses.action_list) - 1):
                if ses.action_list[i][0] in acs:
                    del ses.action_list[i]

                
            Putline('unaction: ' + str(len(acs)) + ' actions removed')
        else:
            Putline('unaction: that action is not defined')

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
            name, expansion = app.SplitBraced(string.join(words[1:]))
            ses.aliases[name] = expansion
            PutUntouchedLine('#OK, {%s} ALIASES {%s}'%(name, expansion))

        elif len(words) == 2:
            # print alias definition
            name = words[1]
            expanded = ses.ExpandAlias(name)
            if expanded:
                count = count + len(expanded)
                for al in expanded:
                    PutUntouchedLine('#al {%s} = {%s}'%(al, ses.aliases[al]) + "\n")
            if not count:
                Putline("alias: that alias is not defined")

        else: 
            # print all current aliases
            for al in ses.aliases.keys():
                count = count + 1
                PutUntouchedLine('#al {%s} = {%s}'%(al, ses.aliases[al]) + "\n")
            if count == 0:
                Putline("alias: no aliases defined.")

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
    PutUntouchedLine('::lyntin help::\n')
    if words == ['help']:
        PutUntouchedLine("Topics Available:\n")
        the_list = os.listdir(helpdir)
        the_list.sort()
        new_line = '   '
        count = 1
        for mem in the_list:
            new_line = new_line + string.ljust(mem, 16)
            if (count % 3) == 0:
                PutUntouchedLine(new_line + "\n")
                new_line = '   '
            count = count + 1
        PutUntouchedLine(new_line + "\n")
        return

    for mem in words[1:]:
        the_list = os.listdir(helpdir)
        if mem in the_list:
            f = open(helpdir + "/" + mem, "r")
            lines = f.readlines()
            f.close()
            PutUntouchedLine(string.join(lines, "") + "\n")
        else:
            PutUntouchedLine(mem + " is not a valid help topic.")

def History(words, input, seslist):
    """History(words, seslist) -> None

    With one numeric argument, set history size.
    With no arguments, prints last histsize commands.
    This is a user command.
    """
    hooks.history_command_hook.run((input, seslist))
    for ses in seslist:
        if len(words) > 2:
            Putline('history: too many arguments')
            continue
        elif len(words) == 2:
            # try to set a new history size
            try:
                num = string.atoi(words[1])
            except ValueError:
                Putline('history: invalid argument')
                continue
            else:
                if num == 0:
                    Putline('history: can\'t set history size to nothing.')
                    continue
                data.histsize = num
                Putline('history: ok, history size set to '+str(num))
        # print last histsize history entries
        else:
            n = len(data.history)
            if n == 0:
                Putline('history: no history yet...')
                continue
            m = min([data.histsize, len(data.history)])
            PutUntouchedLine('\nHistory:')
            for i in range(m - 1, -1, -1):
                PutUntouchedLine(str(i)+' '+str(data.history[i]))
                
def Info(words,input,seslist):
    """Info(seslist) -> None

    Prints session info to the client.
    This is a user command.
    """
    for ses in seslist:
        Putline('Session: ' + ses.name)
        Putline(repr(len(ses.actions.keys())) + ' actions.')
        Putline(repr(len(ses.aliases.keys())) + ' aliases.')
        Putline(repr(len(ses.gags)) + ' gags.')
        Putline(repr(len(ses.vars.keys())) + ' variables.')
        if ses.verbose: Putline('Verbose is on.')
        else:           Putline('Verbose is off.')
        if ses.speedwalk: Putline('Speedwalking is on.')
        else:             Putline('Speedwalking is off.')
        if ses.ticker: Putline('Ticker is on; ' + repr(ses.ticklen) + ses.tickaction)
        else:          Putline('Ticker is off.')
    
def UnAlias(words, input, seslist):
    """UnAlias(words, seslist) -> None

    Removes all matching aliases.
    This is a user command.
    """
    hooks.unalias_command_hook.run((input, seslist))
    for ses in seslist:
        if len(words) != 2:
            Putline('unalias: command requires one argument')
            Putline('unalias <aliasname>')
            return

        als = ses.ExpandAlias(words[1])
        if als:
            for al in als:
                # kill!!!
                del ses.aliases[al]
            Putline('unalias: ' + str(len(als)) + ' aliases removed') 
        else:
            Putline('unalias: that alias is not defined')

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
                Putline('gag: no gags are defined')
            else:
                for gag in ses.gags:
                    Putline('gag: gag ' + gag)
            continue
        gagwhat = string.join(words[1:])
        # add string to current session's gags
        ses.gags = ses.gags + [gagwhat]
        Putline('gag: ok, "' + gagwhat + '" is now gagged')

def UnGag(words, input, seslist):
    """UnGag(words, seslist) -> None

    Removes the given string from the session's gags.
    This is a user command.
    """
    hooks.ungag_command_hook.run((input, seslist))
    for ses in seslist:
        if len(words) < 2:
            Putline('ungag: command requires at least one argument')
            Putline('ungag <gagname>')
            return
        ungagwhat = string.join(words[1:])
        ungagwhatlist = ses.Expand(ungagwhat, ses.gags)
        # remove ungagwhat from the current session's gags
        for g in ungagwhatlist:
            if ses.gags.count(g) > 0:
                ses.gags.remove(g)
                Putline('gag: ok, "' + g + '" is no longer gagged')
        if not ungagwhatlist:
            Putline('gag: that gag is not defined')

def Substitute(words, input, seslist):
    """Substitute(words, seslist) -> None

    Anytime we see a certain string from the mud,
    substitute an alternate string for it.
    This is a user command.
    """
    hooks.substitute_command_hook.run((input, seslist))
    for ses in seslist:
        if len(words) < 3:
            Putline('substitute: command requires at least two arguments')
            continue
        pattern, replacement = app.SplitBraced(string.join(words[1:]))
        ses.subs[pattern] = replacement
        Putline('ok, ' + pattern + ' is now replaced by ' + replacement)

def UnSubstitute(words, input, seslist):
    """UnSubstitute(words, seslist) -> None

    Removes the substitute from the current session.
    This is a user command.
    """
    hooks.unsubstitute_command_hook.run((input, seslist))
    for ses in seslist:
        if len(words) < 2:
            Putline('command requires at least one argument')
            return
        unlist = ses.Expand(string.join(words[1:]), ses.subs.keys())
        for sub in unlist:
            del ses.subs[sub]
        Putline(str(len(unlist)) + ' substitutes removed')

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
        Putline('session ' + ses.name + ' cleared')


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
                Putline('Ticker is off')
                return
            Putline('resetting ticker...')
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
                    Putline('Ticker is now on (ticklen = %d) (tickaction = %s)'%(ses.ticklen, ses.tickaction))
                else:
                    Putline('Ticker is already on!')

        elif words[1] == 'off':
            # turn off ticker
            for ses in seslist:
                ses.ticker = 0
                Putline('Ticker is now off (ticklen = %d) (tickaction = %s)'%(ses.ticklen, ses.tickaction))
            
        elif words[1] == 'clear':
            for ses in seslist:
                ses.ticker = 0
                ses.tickaction = ''
                Putline('ticklen and tickaction cleared.')

        elif words[1] == 'toggle':
            # toggle ticker status
            for ses in seslist:
                ses.ticker = not ses.ticker
                if ses.ticker:
                    ses.lasttickclock = 0
                    ses.lastclock = time.time()
                    ses.warnedtick = 0
                    Putline('Ticker is now on (ticklen = %d) (tickaction = %s)'%(ses.ticklen, ses.tickaction))
                else:
                    Putline('Ticker is now off (ticklen = %d) (tickaction = %s)'%(ses.ticklen, ses.tickaction))

        elif words[1] == 'status':
            for ses in seslist:
                Putline('Ticker status:')
                if ses.ticker:
                    Putline('Ticker is on')
                    Putline('Ticklength = %d'%ses.ticklen)
                    Putline('Tickaction = %s'%ses.tickaction)
                    Putline('Time to next tick = %d'%(ses.ticklen - ses.lasttickclock))
                else:
                    Putline('Ticker is off')
                    Putline('Ticklength = %d'%ses.ticklen)
                    Putline('Tickaction = %s'%ses.tickaction)
                    Putline('Time to next tick = %d'%(ses.ticklen - ses.lasttickclock))
                    
        else:
            # set ticklength
            for ses in seslist:
                try:
                    ses.ticklen = string.atoi(words[1])
                    Putline('tick length set to %d'%ses.ticklen)
                except ValueError:
                    # Putline('invalid argument -- must be an integer')
                    ses.tickaction = string.join(words[1:], " ")
                    Putline('tickaction set to %s'%ses.tickaction)


def Tick(words, input, seslist):
    """Tick(words, seslist) -> None

    Display tick status.
    This is a user command.
    """
    hooks.tick_command_hook.run((input, seslist))
    if len(words) == 1: # display tick status
        for ses in seslist:
            if not ses.ticker:
                Putline('Ticker is off')
                return
            Putline('there are %d seconds to the next tick!!'%\
                    (ses.ticklen - ses.lasttickclock))
    else:
        Putline('command accepts no arguments')

def Version(words, input, seslist):
    """Version(words, input, seslist) -> None

    Prints out the version.
    """
    import data
    PutUntouchedLine(data.version)


def Verbose(words, input, seslist):
    """Verbose(seslist) -> None

    Toggles whether or not to be verbose.
    This is a user command.
    """
    for ses in seslist:
        ses.verbose = not ses.verbose
        if ses.verbose:
	    Putline('Verbose mode now on.')

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
                warntext='%d seconds to tick!!!'%ses.tickwarn
                Putline(warntext)
                hooks.ticker_warn_hook.run((ses,))
        if ses.lasttickclock > ses.ticklen:
            Putline('tick!!!')
            hooks.ticker_pass_hook.run((ses,))
            if ses.tickaction:
                data.theapp.HandleUserInput(ses.tickaction)
                
            ses.lasttickclock=0
            ses.warnedtick=0

###
### This function adds all the standard commands to data.theapp.commands
###

def InitPlayer():
    import player
    data.theapp.AddCommand("version", player.Version)
    data.theapp.AddCommand("alias", player.Alias)
    data.theapp.AddCommand("unalias", player.UnAlias)
    data.theapp.AddCommand("import", player.LynImport)
    data.theapp.AddCommand("^clear", player.Clear)
    data.theapp.AddCommand("^cr", player.CR)
    data.theapp.AddCommand("^char", player.Char)
    data.theapp.AddCommand("help", player.Help)
    data.theapp.AddCommand("^quit", player.Quit)
    data.theapp.AddCommand("uncommand", player.UnCommand)
    data.theapp.AddCommand("command", player.AddCommand)
    data.theapp.AddCommand("printcommands", player.PrintCommands)
    data.theapp.AddCommand("action", player.Action)
    data.theapp.AddCommand("databuffer", player.DataBuffer)
    data.theapp.AddCommand("datagreplines", player.DataGrepLines)
    data.theapp.AddCommand("gag", player.Gag)
    data.theapp.AddCommand("history", player.History)
    data.theapp.AddCommand("info", player.Info)
    data.theapp.AddCommand("killall", player.KillAll)
    data.theapp.AddCommand("log", player.Log)
    data.theapp.AddCommand("read", player.ParseFile)
    data.theapp.AddCommand("report", player.Report)
    data.theapp.AddCommand("session", player.Ses)
    data.theapp.AddCommand("showme", player.Showme)
    data.theapp.AddCommand("substitute", player.Substitute)
    data.theapp.AddCommand("speedwalk", player.SpeedWalk)
    data.theapp.AddCommand("unaction", player.UnAction)
    data.theapp.AddCommand("textin", player.Textin)
    data.theapp.AddCommand("alias", player.Alias)
    data.theapp.AddCommand("ungag", player.UnGag)
    data.theapp.AddCommand("unsubstitute", player.UnSubstitute)
    data.theapp.AddCommand("variable", player.Variable)
    data.theapp.AddCommand("write", player.WriteFile)
    data.theapp.AddCommand("tick", player.Tick)
    data.theapp.AddCommand("tickset", player.Tickset)
    data.theapp.AddCommand("verbose", player.Verbose)
    data.theapp.AddCommand("version", player.Version)
    data.theapp.AddCommand("read", player.ParseFile)
    data.theapp.AddCommand("echo", player.Echo)
