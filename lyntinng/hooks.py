#######################################################################
# This file is part of Lyntin.
# copyright (c) Lyn Headley 1996-2000
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: hooks.py,v 1.2 2002/04/11 03:58:22 willhelm Exp $
##################################################################
"""
Holds all the hook constants for all the hooks that Lyntin has.
Also contains the Hook class which encapsulates hook functionality.
"""

import traceback

FIRST = 0
LAST = 99

class Hook:
  """
  Represents a (possibly empty) sequence of user-defined
  functions.  provides user with the opportunity of reacting
  to events internal to lyntin.  All functions take a single
  argument which is a tuple.  see the specific hooks below for
  more info.
  """
  def __init__(self):
    self.functionlist = []

  def spamhook(self, arglist=()):
    """ Sends out input to all the registrants of a hook.

    arguments:

      'arglist' -- (list of arguments--depends on hook)
                   the list of arguments that gets passed to
                   each function in the hook 
    """
    for mem in self.functionlist:
      mem(arglist)


  def unregister(self, func):
    """
    Tries to remove a registrant from a hook--does pretty well.

    arguments:

      'func' -- (function) the function to unregister

    """
    if func in self.functionlist:
      self.functionlist.remove(func)


  def register(self, func, place=LAST):
    """ Registers a function with a hook.

    hook should be one of the hook constants.  func 
    should be a callable function.  place is optional--it allows 
    you to put yourself earlier in the hook lineup.

    arguments:

      'func' -- (function) the function to call

      'place=LAST' -- (int) the function will get this place in 
                      the call order

    """
    if not callable(func):
      exported.write_error("Function %s not callable." % repr(func))
      return

    if place == LAST or place > len(self.functionlist):
      self.functionlist.append(func)
    else:
      self.functionlist.insert(place, func)

  def clear(self):
    """ Clears the functionlist."""
    self.functionlist = []



##################################################################
# the hooks available in Lyntin
# (if you think of a hook you would like me to add, by all means
# do a feature request at http://lyntin.sourceforge.net)
##################################################################


##################################################################
# Hooks corresponding to events within lyntin
##################################################################

"""
When lyntin starts up.  arg tuple is empty.
"""
startup_hook = Hook()

"""
When lyntin shuts down.  arg tuple is empty.
"""
shutdown_hook = Hook()

"""
When the mud sends an echo on or an echo off.  arg tuple is
the new echo state (1 if on, 0 if off).
"""
echo_hook = Hook()

"""
When a session dies or ends.  arg tuple contains the session instance.
"""
death_hook = Hook()

"""
When a session connects to a mud.  arg tuple contains the session instance,
the hostname of the mud it connected to, and the port.
"""
connect_hook = Hook()

"""
When a user types a command, this will trigger the user_data_hook.
The arg tuple contains the data they entered.
"""
user_data_hook = Hook()

"""
When the mud sends data, this will trigger the mud_data_hook.
The arg tuple contains the session and the raw mud data.

If you're looking for a line by line idea of things, use the
databuffer hook.
"""
mud_data_hook = Hook()

"""
The timer hook runs every second.  The tickers for the various sessions
use this hook to figure out when to tick.

arg tuple contains the current tick.
"""
timer_hook = Hook()

"""
When an error is kicked up via the event loop.

arg tuple is empty (check sys.exc_traceback).
"""
error_occurred_hook = Hook()

"""
When the user_custom variable too_many_errors is exceeded.
arg tuple is empty.
"""
too_many_errors_hook = Hook()
