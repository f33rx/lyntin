##################################################################
# This file is part of Lyntin
# copyright (c) Lyn Headley 1996-1998
#
# Lyntin is distributed under the GNU General Public License.  See
# the file COPYING for details.
#
# module exported
# contains a programmatic layer meant as a user interface to
# the internals of Lyntin.  I am much more committed to maintaining
# backwards compatibility for the code in this module than I am for
# that of the Lyntin core.
##################################################################

import data, mud, app, hooks, scheduler

##################################################################
# The preferred way of interacting with lyntin.
# Treat `str' as either a lyntin command (if it begins with a "#")
# or as input to a mud
def lyntin_command(str):
    data.theapp.PreHandleUserInput(str)


##################################################################
# return the session named sesname
def get_session(sesname):
    return data.GetSes(sesname)[0]


##################################################################
# return a list of all active sessions
def get_active_sessions():
    return data.GetSes('all')


##################################################################
# get the current session
def get_current_session():
    return data.currsession


##################################################################
# set the current session
def set_current_session(ses):
    data.currsession = ses


##################################################################
# return the number of encountered errors
def get_num_errors():
    return data.theapp.numerrors


##################################################################
# set the number of encountered errors
def set_num_errors(num):
    data.theapp.numerrors = num


##################################################################
# return a reference to the history list
def get_history():
    return data.history


##################################################################
# set the history list to a supplied list
def set_history(lst):
    data.history = lst


##################################################################
# return a list of entries from ses's databuffer which match str
def grep_databuffer(str, ses):
    return ses.databuf.grep(str)

    
##################################################################
# return a list of lines from ses's databuffer which match str
def grep_databuffer_lines(str, ses):
    return ses.databuf.greplines(str)


##################################################################
# use the scheduler to run functions at predetermined intervals
time_scheduler = scheduler.Scheduler()
hooks.internal_tick_hook.add(time_scheduler)
