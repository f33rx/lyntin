#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: substitute.py,v 1.15 2002/05/25 18:40:40 jmberne Exp $
#######################################################################
"""
This module defines the SubstituteManager which handles substitutes.
"""
import string
import manager, utils, lyntin

class SubstituteManager(manager.Manager):
  """ Manages substitutes."""
  def __init__(self):
    self._substitutes = {}

  def __copy__(self):
    sm = SubstituteManager()
    for mem in self._substitutes.keys():
      sm.addSubstitute(mem, self._substitutes[mem])
    return sm

  def addSubstitute(self, item, substitute):
    """ Adds a substitute to the dict."""
    self._substitutes[item] = substitute 
    return 1

  def clear(self):
    """ Removes all the substitutes."""
    self._substitutes.clear()

  def removeSubstitutes(self, text):
    """ Removes substitutes from the list.

    Returns a list of tuples of substitute item/substitute that
    were removed.
    """
    badsubstitutes = utils.expand(text, self._substitutes.keys())

    ret = []
    for mem in badsubstitutes:
      ret.append((mem, self._substitutes[mem]))
      del self._substitutes[mem]

    return ret

  def getSubstitutes(self):
    """ Returns the keys of the substitute dict."""
    list = self._substitutes.keys()
    list.sort()
    return list

  def expand(self, text):
    """ Looks at mud data and performs any substitutes.

    It returns the final text--even if there were no substitutes.
    # FIXME -- this isn't done correctly.
    """
    if len(text) > 0:
      for mem in self._substitutes.keys():
        if self._substitutes[mem] == ".":
          if text.find(mem) > -1:
            text = ''
        else:
          text = text.replace(mem, self._substitutes[mem])

    return text 

  def getInfo(self, text=''):
    """ Returns information about the substitutes in here.

    This is used by #substitute to tell all the substitutes involved
    as well as #write which takes this information and dumps
    it to the file.
    """
    if len(self._substitutes.keys()) == 0:
      return ''

    if text=='':
      list = self._substitutes.keys()
    else:
      list = utils.expand(text, self._substitutes.keys())

    data = []
    for mem in list:
      data.append("%ssubstitute {%s} {%s}" % 
                  (lyntin.commandchar, mem, self._substitutes[mem]))

    return string.join(data, "\n")

  def getCount(self):
    """ Returns the number of substitutes we're managing."""
    return len(self._substitutes.keys())

  def filter(self, args):
    """
    Mud_filter_hook function to perform substitutions on data 
    that comes from the mud.
    """
    session = args[0]
    text = args[-1]
    if not session._ignoresubs:
      text = self.expand(text)
    return text
