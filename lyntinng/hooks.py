#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 1996 - 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: hooks.py,v 1.25 2002/10/20 16:09:57 willhelm Exp $
##################################################################
"""
The engine is augmented by a series of X{hooks} which allow modules to
execute functions without having to change Lyntin's internals.  
Examples of this would be the "startup_hook" and "shutdown_hook".  
Any functions that hook into these hooks will be executed upon 
startup or shutdown of Lyntin.  Lyntin also uses these hooks to 
implement its functionality.

For example, the Tk ui uses the "startup_hook" to register with
the "to_user_hook", add the tkui help topic, and start the ui
user listener thread.

Hooks and the Hook class are defined in the "hooks" module as is
a whole lot of documentation on which hooks exist, and what is
passed to them.
"""

import session

# These are priority constants.  They should rarely be used.
FIRST = 0
LAST = 99

class StopSpammingException(Exception):
  pass

class Hook:
  """
  Represents a (possibly empty) sequence of user-defined
  functions.  Provides users with the opportunity of reacting
  to events internal to Lyntin.  All functions take a single
  argument which is a tuple.

  Read through the hooks.py file for more information on the 
  hooks that come with Lyntin as well as which arguments they 
  take in the arg tuple.
  """
  def __init__(self,mapper= lambda x,y:x):
    """
    Initializes.

    @param mapper: function whose output will be passed to the next
        function in the hook.  Must take two arguments, the previous 
        arglist and the return from the previous function.
    @type  mapper: function
    """
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

    @param arglist: the list of arguments that gets passed to
        each function in the hook.  the actual arguments differs
        from hook to hook.
    @type  arglist: tuple of arguments

    @param mappingFunction: function whose output will be passed to the next
        function in the hook.  Must take two arguments, the previous 
        arglist and the return from the previous function.
    @type  mappingFunction: function

    @return: arglist
    @rtype:  tuple of arguments
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

    @param func: the function to unregister
    @type  func: function
    """
    for priority in self.functionlist.keys():
      if func in self.functionlist[priority]:
        self.functionlist[priority].remove(func)
        if len(self.functionlist[priority]) == 0:
          del self.functionlist[priority]

    self.createOrderedList()
        

  def register(self, func, place=LAST):
    """
    Registers a function with a hook.

    hook should be one of the hook constants.  func 
    should be a callable function.  place is optional--it allows 
    you to put yourself earlier in the hook lineup.

    @param func: the function to call when the hook is spammed
    @type  func: function

    @param place: the function will get this place in the call
        order.  functions with the same place specified will get
        arbitrary ordering.  defaults to LAST.
    @type  place: int
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

# When lyntin starts up.  This is a good time to initialize things
# like ui's and other things that need a critical mass of things
# to have been imported and instantiated before doing initialization.
# 
# arg tuple: ()
startup_hook = Hook()

# When lyntin shuts down.
# 
# arg tuple: (boolean)
#  - 0 if we don't have to be quiet, 1 if we should be quiet
shutdown_hook = Hook()

# When the mud sends an echo on or an echo off.
# 
# arg tuple: (int)
#  - new echo state: 1 if on, 0 if off
mudecho_hook = Hook()

# Whenever we switch evalmodes, we call everything on this hook.
# 
# arg tuple will contain the old value and the new value.  Values will be
# the constants in the lyntin module (lyntin.TINTIN and lyntin.LYNTIN).
# When Lyntin first starts up, it passes a -1 as the old value.
#
# arg tuple: (int, int)
#  - old evalmode (or -1 if we just started up)
#  - new evalmode
evalmode_change_hook = Hook()

# This hook will get called every time a variable is changed.
#
# arg tuple: (session, string, string, string)
#  - session instance
#  - the variable name
#  - the old value
#  - the new value
variable_change_hook = Hook()

# When a session dies or ends.
#
# arg tuple: (session)
#  - the session that died
death_hook = Hook()

# When a session connects to a mud.
#
# arg tuple: (session, string, int)
#  - session instance
#  - hostname
#  - port
connect_hook = Hook()

# When a session disconnects from a mud.
#
# arg tuple: (session, string, int)
#  - the session instance that just disconnected
#  - the hostname of where it was connected to
#  - the port at which it was connected
disconnect_hook = Hook()

# Everything the user types gets sent on the from_user_hook.
#
# arg tuple: (string)
#  - the data the user just entered
from_user_hook = Hook()

# When the mud sends data, this will trigger the from_mud_hook.
# 
# If you're looking for a line by line idea of things, use the
# databuffer hook.
#
# arg tuple: (string)
#  - the raw data we just got from the mud
from_mud_hook = Hook()

# This differs from the from_user_hook in that this is everything
# we send on the socket to the mud where the from_user_hook is everything
# the user types--much of it goes to the mud.
#
# arg tuple: (session, string, tag)
#  - the session instance we're sending this data to
#  - the string being sent
#  - the tag used in session.writeSocket (usually None)
to_mud_hook = Hook()

# The ui's listen on this hook to display stuff.  Data on this hook
# is meant for the user to see as Lyntin output or mud output.
#
# arg tuple: (string | ui.ui.Message)
#  - either a string or a ui.ui.Message instance--this is the data
to_user_hook = Hook()

# The timer hook runs every second.  The tickers for the various sessions
# use this hook to figure out when to tick.
# 
# arg tuple: (int)
#  - the current tick since Lyntin started
timer_hook = Hook()

# The write hook runs whenever someone does "#write <filename>".
# This is primarily for session persistence.  Everything registered
# to this hook gets the file object and writes stuff to the file
# object.  Do NOT save the file object or the session object
# for later use!  They may not be there!
# 
# The third argument "quiet" is a flag (0 is no, 1 is yes) indicating 
# whether the user wants the information persisted so that when 
# it's read in with #read it's quiet as to its verbostiy.  For example,
# the AliasManager would persist non-quiet things as:
#
#   #alias {g} {get all}
#
# and quiet things as:
#
#   #alias {g} {get all} quiet={true}
# 
# arg tuple: (session, file object, int)
#  - the session instance
#  - the file object we're writing to
#  - 0 or 1 as to whether or not we should be persisting things
#    quietly
write_hook = Hook()

# When an error is kicked up via the event loop.  The arg tuple
# is empty--you should check sys.exc_traceback if you're interested
# in what just happened.
# 
# arg tuple: ()
error_occurred_hook = Hook()

# When the user_custom variable too_many_errors is exceeded.
#
# arg tuple: ()
too_many_errors_hook = Hook()


##################################################################
# Filtered hooks
##################################################################

def filter_mapper(x,y):
  """
  This is the mapping function to use for filter-style hooks.  
  Spamhook should be called as:

  1. spamtuple = hook.spamhook( (session, flags, original, original) )
  2. output = spamtuple[-1]

  Each filter function will get (session, flags, original, filteredoriginal) 
  when it is called.
  """
  if y != None:
    return x[:-1] + (y,)
  else:
    raise StopSpammingException

# Whenever data comes back from the mud it will first be passed through
# all filter functions.
# 
# These should return the text that should be processed as if it came from 
# the mud.
# 
# arg tuple: (session, boolean, string, string)
#  - the session the mud data came from
#  - 0 or 1: whether or not the data is internal
#  - the original text the mud sent
#  - the filtered text (this allows people to adjust it as they go along)
# 
# Functions that register with this hook should return the adjusted text.
# For example, the SubstituteManager returns text with substitutions
# expanded.
mud_filter_hook = Hook(filter_mapper)

# Whenever data comes from the user it will first be passed through
# all filter functions.
# 
# These should return the text that should be sent to the mud.
# 
# arg tuple: (session, boolean, boolean, string, string)
#  - the session instance
#  - 0 or 1: whether or not the data is internal
#  - 0 or 1: whether or not we're in verbatim mode where we don't adjust
#    the user data at all (from the session)
#  - the original text the user typed
#  - the adjusted text
#
# Functions that register with this hook should return the adjusted text.
# For example, the AliasManager returns text with aliases expanded.
user_filter_hook = Hook(filter_mapper)


# Local variables:
# mode:python
# py-indent-offset:2
# tab-width:2
# End:
