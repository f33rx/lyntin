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

def lyntin_command(str):
    """lyntin_command(str) -> none

    The preferred way of interacting with lyntin.
    Treat 'str' as either a lyntin command (begins with a '#'
    just like you would type at the prompt) or a mud command.
    """
    data.theapp.PreHandleUserInput(str)

def lyntin_add_command(str, func):
    """lyntin_add_command(str, func) -> none

    Takes in a string and a function and adds the str -> func
    binding to the command hash.
    """
    data.theapp.AddCommand(str, func)

def lyntin_get_commands():
    """lyntin_get_commands() -> command hash

    Returns the hash of all the commands available.  This
    was tossed in so i could do some testing and may be
    changed in the future.
    """
    return data.theapp.ReturnCommandHash()

def get_session(sesname):
    """get_session(sesname) -> session ob

    Takes in a session name (string) and returns a session object.
    """
    return data.GetSes(sesname)[0]


def get_active_sessions():
    """get_active_sessions() -> session ob list

    Returns a list of active sessions.
    """
    return data.GetSes('all')


def get_current_session():
    """get_current_session() -> session ob

    Gets the current session ob.
    """
    return data.currsession


def set_current_session(ses):
    """set_current_session(ses) -> none

    Sets the current session.
    """
    data.currsession = ses


def get_num_errors():
    """get_num_errors() -> int

    Returns the number of encountered errors.
    """
    return data.theapp.numerrors


def set_num_errors(num):
    """set_num_errors(num) -> none

    Sets the number of encountered errors.  Be careful using this
    as Lyntin keeps track of the number of errors for a reason.
    """
    data.theapp.numerrors = num


def get_history():
    """get_history() -> history list

    Returns a reference to the history list.
    """
    return data.history


def set_history(lst):
    """set_history(lst) -> none

    Sets the history list to the supplied list.
    """
    data.history = lst


def grep_databuffer(str, ses):
    """grep_databuffer(str, ses) -> list of entries

    Returns a list of entries from the ses's databuffer which
    match the str.
    """
    return ses.databuf.grep(str)

    
def grep_databuffer_lines(str, ses):
    """grep_databuffer_lines(str, ses) -> list of lines

    Returns a list of lines from the ses's databuffer which
    match the string.
    """
    return ses.databuf.greplines(str)

def print_line(str):
    """print_line(str) -> none

    Prints a line to the screen with an added \n.
    """
    data.player.PutUntouchedLine(str)

##################################################################
# use the scheduler to run functions at predetermined intervals
time_scheduler = scheduler.Scheduler()
hooks.internal_tick_hook.add(time_scheduler)
