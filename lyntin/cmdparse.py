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

import string, re
import data, app

var_char = '$'

def initialize():
    """initialize() -> None

    Initializes the variable character.
    """
    global var_char
    var_char = app.get_user_custom('lyntin_variable_char')
    

def substitute_vars(input):
    """substitute_vars(input) -> #, str

    Substitutes variables found in the input with
    their values unless they're braced.
    """
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
                parsed = parsed + v + c
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
    


"""regex for history substitutions
looks like '!4 joe=john' or '! I like=I hate'"""
sub_regex = re.compile('^![0-9]* (.*)=(.*)')


def do_history_subs(hist, input):
    """do_history_subs(hist, input) -> str

    when requesting a redo from the history list, the user 
    has the option of substituting for some of the text in the 
    command, along the lines of !3 jay=joe.
    here's where we do that.
    """
    match = sub_regex.search(hist)
    if match:
        # user wants to substitute something in this command
        pat = match.group(1)
        repl = match.group(2)
        input = re.sub(pat, repl, input)
    return input


def work_over(input, ses):
    """work_over(input, ses) -> 1|0, str

    search input for speedwalking/aliases
    return a 2 elt tuple, of whether an alias was found,
    and what it expanded to
    """
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
                varlist, ret = app.strip_vars(ret)
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
                    ret = re.sub(pat, vars[var], ret)

    # check for a speedwalking string, like 3n5wsse
    # we do this so here so that aliases will always
    # have precedence over speedwalks
    # note: wbg 12/6/1999 -- added second regex check to make sure that 
    # plain numbers don't kick off the speedwalk code.  there's prob a 
    # better way to do it though.
    match1 = re.compile('^[udnswe0-9][udnswe0-9]+$').search(input)
    match2 = re.compile('[udnswe]').search(input)
    if match1 and match2:
        if not whether:
            whether = 'speed'
            ret = input

    return whether, ret



def split_action(ac): 
    """split_action(ac) -> (ac_trigger, ac_response)

    return (trigger, response) from action string 
    input looks like '#ac {you see a dog} {kill dog}'
    """
    ac_trigger = ''
    ac_response = ''
    
    # regex to match an action command
    action_regex = re.compile(string.split(ac)[0] + ' \{(.*)\} \{(.*)\}')
    match = action_regex.match(ac)
    if match:
        ac_trigger = match.group(1)
        ac_response = match.group(2)
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
