#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 1996 - 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: hooks.py,v 1.12 2002/04/29 00:31:42 jmberne Exp $
##################################################################
"""
Holds all the hook constants for all the hooks that Lyntin has.
Also contains the Hook class which encapsulates hook functionality.
"""

import traceback

import session, variable

"""
These are priority constants.  They should rarely be used.
"""
FIRST = 0
LAST = 99

class StopSpammingException(Exception):
  def __init__(self, value=""):
    self.value = value

  def __str__(self):
    return `self.value`


class Hook:
  """
  Represents a (possibly empty) sequence of user-defined
  functions.  Provides users with the opportunity of reacting
  to events internal to Lyntin.  All functions take a single
  argument which is a tuple.  see the specific hooks below for
  more info.
  """
  def __init__(self,mapper= lambda x,y:x):
    # this is the master priority list
    self.functionlist = {}

    # this gets recomputed everytime someone registers or
    # unregisters a hook
    self.orderedlist = []

    self.mapper = mapper

  def createOrderedList(self):
    """
    Goes through the functionlist and generates the
    orderedlist.  This helps save some cycles every time
    we spam the hook.
    """
    priorities = self.functionlist.keys();
    priorities.sort()

    self.orderedlist = []

    for priority in priorities:
      for mem in self.functionlist[priority]:
        self.orderedlist.append(mem)
    
    
  def spamhook(self, arglist=(), mappingFunction=None):
    """ Sends out input to all the registrants of a hook.

    arguments:

      'arglist' -- (list of arguments--depends on hook)
                   the list of arguments that gets passed to
                   each function in the hook 

      'mappingFunction' -- function whose output will be passed to the next
                           function in the hook.  Must take two arguments, 
                           the previous arglist and the return from the 
                           previous function
    """
    mappingFunction = mappingFunction or self.mapper

    try:
      for mem in self.orderedlist:
        output = mem(arglist)
        arglist = mappingFunction(arglist,output)
    except StopSpammingException, e:
      return None

    return arglist

  def unregister(self, func):
    """
    Tries to remove a registrant from a hook--does pretty well.

    arguments:

      'func' -- (function) the function to unregister

    """
    for priority in self.functionlist.keys():
      if func in self.functionlist[priority]:
        self.functionlist[priority].remove(func)
        if len(self.functionlist[priority]) == 0:
          del self.functionlist[priority]

    self.createOrderedList()
        

  def register(self, func, place=LAST):
    """ Registers a function with a hook.

    hook should be one of the hook constants.  func 
    should be a callable function.  place is optional--it allows 
    you to put yourself earlier in the hook lineup.

    arguments:

      'func' -- (function) the function to call

      'place=LAST' -- (int) the function will get this place in 
                      the call order  functions with the same place
                      specified will get arbitray ordering

    """
    if not callable(func):
      exported.write_error("Function %s not callable." % repr(func))
      return


    if self.functionlist.has_key(place):
      self.functionlist[place].append(func)
    else:
      self.functionlist[place] = [func]

    self.createOrderedList()

  def clear(self):
    """ Clears the functionlist."""
    self.functionlist = {}
    self.orderedlist = []



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
Everything the user types gets sent on the from_user_hook.
The arg tuple contains the data they entered.
"""
from_user_hook = Hook()

"""
When the mud sends data, this will trigger the from_mud_hook.
The arg tuple contains the session and the raw mud data.

If you're looking for a line by line idea of things, use the
databuffer hook.
"""
from_mud_hook = Hook()

"""
This differs slightly from the from_user_hook in that this is everything
we send on the socket to the mud where the from_user_hook is everything
the user types--much of it goes to the mud.  The arg tuple is the session
instance, then the string being sent to the mud, then the tag used in
the session.writeSocket method (usually none).
"""
to_mud_hook = Hook()

"""
The ui's listen on this hook to display stuff.  The arg tuple is
either a string or a ui.ui.Message instance.
"""
to_user_hook = Hook()

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

"""
This is the mapping function to use for filter-style hooks.  
Spamhook should be called as 

  spamtuple = hook.spamhook( (session,flags,original,original) )
  output = spamtuple[-1]

Each filter function will get (session,flags,original,filteredoriginal) 
when it is called.
"""
def filter_mapper(x,y):
  if y != None:
    return x[:-1] + (y,)
  else:
    raise StopSpammingException

"""
Whenever data comes back from the mud it will first be passed through
all filter functions.

These should return the text that should be processed as if it came from 
the mud.

arg tuple will contain the session, the internal flag, the original text
and the currently filtered text.
"""
mud_filter_hook = Hook(filter_mapper)

"""
Whenever data comes from the user it will first be passed through
all filter functions.

These should return the text that should be sent to the mud.

arg tuple will contain the session, the original text and the currently 
filtered text.
"""
user_filter_hook = Hook(filter_mapper)
