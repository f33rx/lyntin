##################################################################
# This file is part of Lyntin
# copyright (c) Lyn Headley 1996-2001
#
# Lyntin is distributed under the GNU General Public License.  See
# the file LICENSE in the distribution for details.
# $Id: hooks.py,v 1.6 2001/08/06 02:00:19 willhelm Exp $
##################################################################
"""
Contains the hook class, which is a sequence of user
defined functions, called at certain times during lyntin's 
execution

contains all of lyntin's hooks
"""



class Hook:
   """
   Represents a (possibly empty) sequence of user-defined
   functions.  provides user with the opportunity of reacting
   to events internal to lyntin.  All functions take a single
   argument which is a tuple.  see the specific hooks below for
   more info.
   """
   def __init__(self, funclist = []):
      self.funclist = funclist

   # execute all the functions in the funclist
   def run(self, arg=()):
      for func in self.funclist:
         func(arg)

   # add a function to the funclist
   def add(self, func):
      self.funclist = self.funclist + [func]
        
   # clear the funclist
   def clear(self):
      self.funclist = []



##################################################################
# the hooks available in Lyntin
# (if you think of a hook you would like me to add, by all means
# do a feature request at http://lyntin.sourceforge.net)
##################################################################


##################################################################
# Hooks corresponding to events within lyntin
##################################################################

"""when a session dies. arg tuple contains a session instance."""
death_hook = Hook()

"""when actions are triggered. arg tuple contains a session instance, 
the action triggered (a string) the line it matched (a string) , 
and the response sent to the mud (a string)."""
action_hook = Hook()

"""when the databuffer grows, i.e. when any output is received
from the mud. arg tuple contains a databuffer instance."""
data_hook = Hook()

"""when the active session is changed.  arg tuple contains the old 
session instance, and the new one."""
set_session_hook = Hook()

"""when lyntin shuts down.  arg tuple is empty."""
shut_down_lyntin_hook = Hook()

"""when the user types something.  arg tuple contains the string 
received from the user."""
received_user_input_hook = Hook()

"""when a connection is made successfully.  arg tuple contains the 
session name (a string) the host (string) and port (int)."""
connect_succeeded_hook = Hook()

"""when creating a new connection fails.  arg tuple contains the 
session name (a string) the host (string) and port (int)."""
connect_failed_hook = Hook()

"""invoked every nth iteration through lyntin's main loop.
(currently n is 5) arg tuple is empty."""
internal_tick_hook = Hook()

"""when a session is warned of an upcoming tick.  arg tuple contains 
the session."""
ticker_warn_hook = Hook()

"""when a session is informed of a mud-level tick.  arg tuple contains 
the session."""
ticker_pass_hook = Hook()

"""when an error occurs in user code.  arg tuple is empty (check 
sys.exc_traceback)."""
error_occurred_hook = Hook()

"""when the user_custom variable too_many_errors is exceeded.
arg tuple is empty."""
too_many_errors_hook = Hook()



##################################################################
# Hooks triggered by invoking lyntin commands
# almost all take 2 arguments: the string typed by the user,
# minus the first '#', and a list of applicable session.
##################################################################

"""when the #@ command is executed.  arg tuple contains the string 
typed by the user, minus the first '#'."""
exec_user_code_hook = Hook()

"""arg tuple contains the string typed by the user, minus the first 
'#', and a list of applicable sessions."""
action_command_hook = Hook()

"""arg tuple contains the string typed by the user, minus the first
'#' and a list of applicable sessions."""
alias_command_hook = Hook()

"""arg tuple contains a list of applicable sessions."""
clear_command_hook = Hook()

"""arg tuple contains the string typed by the user,
minus the first '#', and a list of applicable sessions."""
char_command_hook = Hook()

"""arg tuple contains a list of applicable sessions."""
cr_command_hook = Hook()

"""arg tuple contains the string typed by the user,
minus the first '#', and a list of applicable sessions."""
databuffer_command_hook = Hook()

"""arg tuple contains the string typed by the user,
minus the first '#', and a list of applicable sessions."""
datagrep_command_hook = Hook()

"""arg tuple contains the string typed by the user,
minus the first '#', and a list of applicable sessions."""
datagreplines_command_hook = Hook()    

"""arg tuple contains the string typed by the user,
minus the first '#', and a list of applicable sessions."""
gag_command_hook = Hook()

"""arg tuple contains the string typed by the user,
minus the first '#', and a list of applicable sessions."""
history_command_hook = Hook()

"""arg tuple contains the string typed by the user,
minus the first '#', and a list of applicable sessions."""
killall_command_hook = Hook()

"""arg tuple contains the string typed by the user,
minus the first '#', and a list of applicable sessions."""
log_command_hook = Hook()

"""arg tuple contains the string typed by the user,
minus the first '#', and a list of applicable sessions."""
read_command_hook = Hook()

"""arg tuple contains the string typed by the user,
minus the first '#', and a list of applicable sessions."""
report_command_hook = Hook()

"""arg tuple contains the string typed by the user,
minus the first '#', and a list of applicable sessions."""
session_command_hook = Hook()

"""arg tuple contains the string typed by the user,
minus the first '#', and a list of applicable sessions."""
showme_command_hook = Hook()

"""arg tuple contains the string typed by the user,
minus the first '#', and a list of applicable sessions."""
substitute_command_hook = Hook()

"""arg tuple contains a list of applicable sessions.
check the instance variable 'speedwalk' of each session.
a one means speedwalking is on, and will become off.
a zero's meaning should now be obvious."""
speedwalk_command_hook = Hook()

"""arg tuple contains the string typed by the user,
minus the first '#', and a list of applicable sessions."""
unaction_command_hook = Hook()

"""arg tuple contains the string typed by the user,
minus the first '#', and a list of applicable sessions."""
textin_command_hook = Hook()

"""arg tuple contains the string typed by the user,
minus the first '#', and a list of applicable sessions."""
unalias_command_hook = Hook()

"""arg tuple contains the string typed by the user,
minus the first '#', and a list of applicable sessions."""
ungag_command_hook = Hook()

"""arg tuple contains the string typed by the user,
minus the first '#', and a list of applicable sessions."""
unsubstitute_command_hook = Hook()

"""arg tuple contains the string typed by the user,
minus the first '#', and a list of applicable sessions."""
variable_command_hook = Hook()

"""arg tuple contains the string typed by the user,
minus the first '#', and a list of applicable sessions."""
write_command_hook = Hook()

"""arg tuple contains the string typed by the user,
minus the first '#', and a list of applicable sessions."""
tickset_command_hook = Hook()

"""arg tuple contains a list of sessions."""
tick_command_hook = Hook()



# Local variables:
# mode:python
# py-indent-offset:3
# tab-width:3
# End:
