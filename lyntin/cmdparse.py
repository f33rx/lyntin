##################################################################
# This file is part of Lyntin
# copyright (c) Lyn Headley 1996-1998
#
# Lyntin is distributed under the GNU General Public License.  See
# the file COPYING for details.
#
# module cmdparse
##################################################################
"""
contains utility functions for parsing user-commands
This should be re-written to use commands that make sense to
normal human beings.
"""

import string, regex, regsub
import data, app

var_char = '$'

def Initialize():
    var_char = app.GetUserCustom('lyntin_variable_char')
    
# fill in values for any variables found in the input
# unless they're braced
def SubVars(input):
    if string.find(input, var_char) == -1:
        # no variables in this
        return 0, input
    nesting = 0
    varhunt = 0
    parsed = ''
    v = ''
    whether = 0
    for c in input:
        if varhunt:
            if data.currsession.Isvar(v+c):
                v = v + c
            elif data.currsession.IsRealvar(v):
                # found a complete variable
                # chop off var_char from parsed
                parsed = parsed[:-1] + data.currsession.vars[v]
                parsed = parsed + c
                whether = 1
                varhunt = 0
                v = ''
            else:
                # this is not a variable. just put v back onto parsed
                parsed = parsed + v
                v = ''
                varhunt = 0
        elif c == '{':
            parsed = parsed + c
            nesting = nesting + 1
        elif c == '}':
            parsed = parsed + c
            nesting = nesting - 1
        elif c == var_char:
            if not parsed or parsed[-1] == '\\':
                parsed = parsed[:-1] + c
            else:
                parsed = parsed + c
                if not nesting:
                    varhunt = 1
        else:
            parsed = parsed + c
    if v:
        # there could've been a variable at the end of the input
        for var in data.currsession.vars.keys():
            if v == var:
                whether = 1
                parsed = parsed[:-1] + data.currsession.vars[v]
    return whether, parsed
    


# regex for history substitutions
# looks like '!4 joe=john' or '! I like=I hate'
sub_regex = regex.compile('^![0-9]* \(.*\)=\(.*\)')

# when requesting a redo from the history list, the user has
# the option of substituting for some of the text in the command, 
# along the lines of !3 jay=joe.
# here's where we do that.
def DoHistorySubs(hist, input):
    if sub_regex.search(hist) != -1:
        # user wants to substitute something in this command
        pat = sub_regex.group(1)
        repl = sub_regex.group(2)
        input = regsub.gsub(pat,repl, input)
    return input


# search input for speedwalking/aliases
# return a 2 elt tuple, of whether an alias was found,
# and what it expanded to
def WorkOver(input, ses):
    ret = input
    splitup = string.split(input)
    whether = 0

    if splitup: 

        for each in ses.aliases.keys():
            if splitup[0] == each:
                # found a match
                whether = 1
                # make a copy
                ret = ses.aliases[each][:]
                # get the variables that we'll need to fill in
                varlist, ret = app.StripVars(ret)
                varcount = len(varlist)
                if varcount == 0:
                    # this alias has no variables. just concatenate
                    # its expansion with anything else the user typed,
                    # and return
                    if len(splitup) > 1:
                        ret = ret + ' ' + string.join(splitup[1:])
                    return whether, ret

                # find the values of the %0..%n variables
                # %0 is the entire text (except for the command word of course)
                # %n is the nth word after the command word
                # unlike tintin, we don't restrict mudders to a mere
                # nine variables
                vars = {}
                for v in varlist:
                    n = string.atoi(v)
                    if n == 0:
                        if len(splitup) > 1:
                            vars[v] = string.join(splitup[1:])
                        else:
                            vars[v] = ''
                    else:
                        if len(splitup) > n:
                            vars[v] = splitup[n]
                        else:
                            vars[v] = ''

                # go through the alias definition, substituting whatever
                # the player typed for the variables %1...%n
                for var in vars.keys():
                    pat = '%' + var
                    ret = regsub.gsub(pat, vars[var], ret)

    # check for a speedwalking string, like 3n5wsse
    # we do this so here so that aliases will always
    # have precedence over speedwalks
    # note: wbg 12/6/1999 -- added second regex check to make sure that 
    # plain numbers don't kick off the speedwalk code.  there's prob a 
    # better way to do it though.
    if regex.search('^[udnswe0-9][udnswe0-9]+$', input) != -1 and regex.search('[udnswe]', input) != -1:
        if not whether:
            whether = 'speed'
            ret = input

    return whether, ret



# return (trigger, response) from action string 
# input looks like '#ac {you see a dog} {kill dog}'
def SplitAction(ac): 
    ac_trigger = ''
    ac_response = ''
    
    # regex to match an action command
    action_regex = regex.compile(string.split(ac)[0] + ' {\(.*\)} {\(.*\)}')
    # I wrote this part before I knew how to do backreferences in python
    if action_regex.match(ac) != -1:
        ac_trigger = ac[action_regex.regs[1][0]:action_regex.regs[1][1]]
        ac_response = ac[action_regex.regs[2][0]:action_regex.regs[2][1]]
        return (ac_trigger, ac_response)

    # not defining an action, must be querying
    temp = string.split(ac)
    if len(temp) > 1:
        ac_trigger = string.join(temp[1:])

    # strip '{' and '}'
    if len(ac_trigger):
        if ac_trigger[0] == '{' and ac_trigger[-1] == '}':
            ac_trigger = ac_trigger[1:-1]

    return (ac_trigger, ac_response)
