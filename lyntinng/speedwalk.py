#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: speedwalk.py,v 1.4 2002/04/29 23:14:13 willhelm Exp $
#######################################################################
"""
This module defines the SpeedwalkManager which handles speedwalking
substitution.
"""
import re, string
import manager, utils, lyntin, engine

SPEEDWALK_REGEXP = re.compile('^\d*[udnsew][udnsew\d]*$')
exclusion_list = ["news", "sense", "ed", "sew", "new"]

class SpeedwalkManager(manager.Manager):
  """ Manages Speedwalking."""
  def __init__(self):
    pass

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
      if SPEEDWALK_REGEXP.search(text) and text not in exclusion_list:
        return self.expand_speedwalk(text)
    return text


  def expand_speedwalk(self, input):
    """
    Expands speedwalk shorthand into the full-blown exciting
    thrill of mud-input.

    arguments:

     'input' -- (string) the input string
  
    returns:

      (string) the expanded speedwalk input

    """

    # FIXME - this might be better written

    output = []
    c = ''
    for mem in input:
      if mem in '0123456789':
        c += mem
      elif len(c) > 0:
        for i in range(int(c)):
          output.append(mem)
        # output = output + ((mem + '\n') * int(c))
        c = '' 
      else:
        output.append(mem)
        # output = output + mem + '\n'
    return string.join(output, "\n")
