#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: manager.py,v 1.1 2002/02/27 02:25:22 willhelm Exp $
#######################################################################
"""
This module defines the basic manager which handles various things
in the system.  All simple managers on a session scoping should extend 
this class--this class is not meant to be instantiated on its own.

To build a new manager on a session scoping, you need to 

1. extend the manager.Manager class below

2. add a manager instantiation line to engine.initialize to instantiate
that manager.

"""
import utils, lyntin

class Manager:
  """ Base manager class for managing things in Lyntin."""
  def __init__(self):
    pass

  def clear(self):
    """
    Removes everything the manager was managing--essentially reinitializes it.
    """
    pass

  def getInfo(self, text=''):
    """ Returns information managed by this class.

    This is mostly for display to the user--we shouldn't be using this
    method for Lyntin examining Lyntin.

    arguments:

      'text' -- allows us to filter which information we're looking for
                based on names of things

    returns:

      a string of everything involved.
    """
    pass

  def getCount(self):
    """ 
    Similar to getInfo, except this just returns a count of how
    many things we're managing in this manager.
    """
    pass
