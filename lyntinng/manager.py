#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: manager.py,v 1.6 2002/06/18 04:01:12 willhelm Exp $
#######################################################################
"""
This module defines the basic manager which handles various things
in the system.

To build a new manager, you need to 

1. extend the manager.Manager class below

2. create a load() method which adds the manager to the engine
   via exported.add_manager(...)

3. implement all the methods herein that you need to implement

"""
class Manager:
  """ Base manager class for managing things in Lyntin."""
  def __init__(self):
    pass

  def clear(self, ses=None):
    """
    Removes everything the manager was managing--essentially reinitializes it.

    arguments:

      'ses' -- (session instance) the session this applies to.  None
               if it's non applicable.
    """
    pass

  def getInfo(self, ses, text=''):
    """ Returns information managed by this class.

    This is mostly for display to the user--we shouldn't be using this
    method for Lyntin examining Lyntin.

    arguments:

      'text' -- (string) allows us to filter which information we're
                looking for based on names of things

    returns:

      a string of everything involved.
    """
    return ''

  def addSession(self, newsession, basesession=None):
    """
    Tells the manager to create a new session based on another session.
    For example, when we connected to the 3k mud, we would tell all
    the managers to clone the common session to the new session created
    thus populating the new session.

    arguments:

      'newsession' -- (session instance) the new session just created.

      'basesession=None' -- (session instance) the session to clone from.
                            Use None if you don't want to clone from 
                            anything.
    """
    pass

  def removeSession(self, ses):
    """
    Tells the manager to remove information regarding the session.

    arguments:

      'ses' -- (session instance) the session to remove.
    """
    pass

  def getState(self, ses):
    """
    Returns the state of something as a list of command strings
    without the command char (which is added by #write).

    For example, getState on the AliasManager might return:

      ["alias {t3k} {#ses a localhost 3000}",
      "alias {toch} {nwnnen;vortex}"]
      
    arguments:

      'ses' -- (session instance) the ses to persist

    returns:

      list of command strings
    """
    
  def getStatus(self, ses):
    """
    Returns a one-liner status of the state of this manager for
    a given session.  If this manager does not apply to sessions
    (i.e. it's a global manager like ThreadManager), then it
    should return an empty string.

    arguments:

      'ses' -- (session instance) the session to look at

    returns:

      a one-liner string of the status or an empty string
    """
    return ''
