##################################################################
# This file is part of Lyntin
# copyright (c) Lyn Headley 1996-2001
#
# Lyntin is distributed under the GNU General Public License.  See
# the file LICENSE in the distribution for details.
# $Id$
##################################################################
"""
Contains a programmatic layer meant as a user interface to
the internals of Lyntin.  We are much more committed to maintaining
backwards compatibility for the code in this module than I am for
that of the Lyntin core.
"""

import data, mud, app, hooks, scheduler

def lyntin_command(str):
    """
    The preferred way of interacting with lyntin.
    Treat 'str' as either a lyntin command (begins with a '#'
    just like you would type at the prompt) or a mud command.
    """
    data.theapp.PreHandleUserInput(str)

def lyntin_add_command(str, func):
    """
    Takes in a string and a function and adds the str -> func
    binding to the command hash.
    """
    data.theapp.AddCommand(str, func)

def lyntin_get_commands():
    """
    Returns the hash of all the commands available.  This
    was tossed in so i could do some testing and may be
    changed in the future.
    """
    return data.theapp.ReturnCommandHash()

def get_session(sesname):
    """
    Takes in a session name (string) and returns a session object.
    """
    return data.GetSes(sesname)[0]


def get_active_sessions():
    """
    Returns a list of active sessions.
    """
    return data.GetSes('all')


def get_current_session():
    """
    Gets the current session ob.
    """
    return data.currsession


def set_current_session(ses):
    """
    Sets the current session.
    """
    data.currsession = ses


def get_num_errors():
    """
    Returns the number of encountered errors.
    """
    return data.theapp.numerrors


def set_num_errors(num):
    """
    Sets the number of encountered errors.  Be careful using this
    as Lyntin keeps track of the number of errors for a reason.
    """
    data.theapp.numerrors = num


def get_history():
    """
    Returns a reference to the history list.
    """
    return data.history


def set_history(lst):
    """
    Sets the history list to the supplied list.
    """
    data.history = lst


def grep_databuffer(str, ses):
    """
    Returns a list of entries from the ses's databuffer which
    match the str.
    """
    return ses.databuf.grep(str)

    
def grep_databuffer_lines(str, ses):
    """
    Returns a list of lines from the ses's databuffer which
    match the string.
    """
    return ses.databuf.greplines(str)

def print_line(str):
    """
    here for backwards-compatibility reasons
    """
    put_message("use 'put_message' exported function instead.")
    put_message(str)

def put_message(str):
    """
    Prints a line to the screen with an added \n.
    """
    data.player.PutMessage(str)

def put_error(str):
    """
    Prints an error to the screen.
    """
    data.player.PutError(str)


##################################################################
# use the scheduler to run functions at predetermined intervals
time_scheduler = scheduler.Scheduler()
hooks.internal_tick_hook.add(time_scheduler)
