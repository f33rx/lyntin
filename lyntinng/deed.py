#######################################################################
# This file is part of Lyntin.
# copyright (c) Sebastian John 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id$
#######################################################################
"""
This module defines the DeedManager which handles deeds (user events).
"""

import string
import manager, utils, lyntin

class DeedManager(manager.Manager):
  """ Manages deeds."""
  
  def __init__(self):
    self._deeds = []
  
  def addDeed(self, deed):
    """ Adds a deed to the list.
    
    arguments:
    
      'deed' -- (string) the deed
    
    """
    self._deeds.append(deed)
    return 1
  
  def clear(self):
    """ Removes all the deeds."""
    self._deeds = []
  
  def removeDeeds(self, text):
    """ Removes deeds from the list.
    
    Returns a list of the gags that were removed.
    
    arguments:
    
      'text' -- (string) deeds will be removed that match the text
    
    returns:
    
      list of strings of removed deeds
    
    """
    baddeeds = utils.expand(text, self._deeds)
    for mem in baddeeds:
      self._deeds.remove(mem)
    return baddeeds
  
  def getDeeds(self):
    """ Returns all deeds stored.
    
    returns:
    
      list of deed strings
    
    """
    return self._deeds
  
  def getInfo(self, num=""):
    """ Returns information about the deeds in here.
    
    This is used only by #deed to show all the deeds stored.
    
    arguments:
    
      'num=""' -- (string) if a number, only the last num deeds will be
                  returned
    
    returns:
    
      (string) one big string with all the deeds in it
    
    """
    if not self._deeds:
      return ""
    
    if text.isdigit():
      count = int(text)
      list = self._deeds[-count:]
    else:
      list = self._deeds
    
    data = string.join(list, "\n")
    return data
  
  def getCount(self):
    """ Returns the number of deeds actually stored.

    returns:

      (int) count of deeds.
    """
    return len(self._deeds)
