#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: alias.py,v 1.9 2002/04/11 03:58:22 willhelm Exp $
#######################################################################
"""
This module defines the SpeedwalkManager which handles speedwalking
substitution
"""

import re

import manager, utils, lyntin, engine

class SpeedwalkManager(manager.Manager):
  """ Manages Speedwalking."""
  def __init__(self):
    self.SPEEDWALK_REGEXP = re.compile('^\d*[udnsew][udnsew\d]*$')

  def filter(self, tuple):
    """ Handle the filtering of input into speedwalking expansions
        if speedwalking is enabled. 
        If input gets changed then we pass it back to
        engine.myengine.HandleUserData and return None to stop this
        chain of filtering.

    arguments:

      tuple: user_filter_hook arg tuple (session, internal, input,
      filtered)

    returns:

      filtered text or None if any changes took place.
    """
    text = tuple[-1]
    if lyntin.speedwalk == 1:
      if self.SPEEDWALK_REGEXP.search(text) and text != "news":
        return utils.expand_speedwalk(text)
    return text
    


  
  
