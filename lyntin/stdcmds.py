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
"""
import data
from player import Putline, PutUntouchedLine, PutReallyUntouchedLine

def AddCommand(words, input, seslist):
    """AddCommand(words, input, seslist) -> None

    Adds a command to the client.
    """
    if len(words) > 2:
        data.theapp.AddCommand(words[1], words[2])
    else:
        # raise error? or something because there aren't enough
        # arguments.
        pass


# input a string and a list, return a list of all the elements
# in the list that match the string
def ExpandCommand(s, list):
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

 
def UnCommand(words, input, seslist):
    """UnCommand(words, input, seslist) -> None

    Removes a command from the client.
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


def Version(words, input, seslist):
    PutUntouchedLine(data.version)


def Showme(words, input, seslist):
    """Showme(words, seslist) -> None

    Prints the words to the clients display
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

        # extract parameters
        name = to[0]
        host = to[1]
        port = string.atoi(to[2])

        # try to connect with the given parameters
        try:
            Putline("ses: Trying to connect...")
            thisses = data.session(name,host,port)
            
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

def DataGrep(words, input, seslist):
    """DataGrep(words, seslist) -> None

    Searches through the databuffer for a regex, printing all matches
    in their entirety.
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

def Report(words, input, seslist):
    """Report(words, seslist) -> None

    With no args, prints all reports
    Otherwise, creates a report which prints the line containing
    args 2+ to the file given by arg1, whenever said line is seen
    in mud output.
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

# write aliases/actions, etc to a file
# this saves the local session and the global session in one fell swoop
def WriteFile(words, input, seslist):
    """WriteFile(words, seslist) -> None
    
    Writes aliases/actions/gags, etc to a file.
    This saves the local session and the global session in one fell
    swoop.
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
        # otherwise we prepend the initdir to the argument
        if words[1][0] == os.sep:
            filename = words[1]
        else:
            filename = data.initdir + words[1]

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



def Log(words, input, seslist):
    """Log(words, seslist) -> None

    Starts a log file for the current session.
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
        # otherwise we prepend the initdir to the argument
        if words[1][0] == os.sep:
            fullfile = words[1]
        else:
            fullfile = data.initdir + words[1]

        try:
            f = open(fullfile, 'w')
        except IOError:
            Putline('log: unable to open log file: ' + fullfile)
        else:
            # ok, got it open.  set up the logging stuff...
            Putline('log: ok, logging...')
            ses.logging = 1
            ses.logfile = f


def KillAll(words,input,seslist):
    """KillAll() -> None

    Wipes clean all active session removing actions/gags/subs...
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
            for i in xrange(len(ses.action_list)):
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
                    PutUntouchedLine('#al {%s} = {%s}'%(al, ses.aliases[al]))
            if not count:
                Putline("alias: that alias is not defined")

        else: 
            # print all current aliases
            for al in ses.aliases.keys():
                count = count + 1
                PutUntouchedLine('#al {%s} = {%s}'%(al, ses.aliases[al]))
            if count == 0:
                Putline("alias: no aliases defined.")



def Help(words, input, seslist):
    """Help(words, seslist) -> None

    Eventually, this should call hooks for things that aren't
    defined in help.print_help.  Then folks can build modules and
    add help to their modules without putting new help files in the
    help directory.  Later though.
    """
    import os

    helpdir = data.initdir + "help"
    PutUntouchedLine('::lyntin help::')
    if words == ['help']:
        PutUntouchedLine("Topics Available:\n")
        the_list = os.listdir(helpdir)
        the_list.sort()
        new_line = '   '
        count = 1
        for mem in the_list:
            new_line = new_line + string.ljust(mem, 16)
            if (count % 3) == 0:
                PutUntouchedLine(new_line)
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
            PutUntouchedLine(string.join(lines, ""))
        else:
            PutUntouchedLine(mem + " is not a valid help topic.")

    
def History(words, input, seslist):
    """History(words, seslist) -> None

    With one numeric argument, set history size.
    With no arguments, prints last histsize commands.
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
            for i in range(m - 1, -1, -1):
                PutReallyUntouchedLine(str(i)+' '+str(data.history[i]))
                
def Info(words,input,seslist):
    """Info(seslist) -> None

    Prints session info to the client.
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



# TICKER AND COMMANDS FUNCTIONS

def Tickset(words, input, seslist):
    """Tickset(words, seslist) -> None

    With no arguments, synchronize tick start ot current time.
    With arg "on" set ticker on.  With arg "off" set ticker off.
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

    display tick status.
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


def Verbose(words, input, seslist):
    """Verbose(seslist) -> None

    Toggles whether or not to be verbose.
    """
    for ses in seslist:
        ses.verbose = not ses.verbose
        if ses.verbose:
	    Putline('Verbose mode now on.')


import stdcmds
data.theapp.AddCommand("version", stdcmds.Version)
