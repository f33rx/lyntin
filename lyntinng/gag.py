#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: gag.py,v 1.11 2002/04/29 01:06:46 jmberne Exp $
#######################################################################
"""
This module defines the GagManager which handles gags in Lyntin.
"""
import re, string
import manager, utils, lyntin

class GagManager(manager.Manager):
  """ Manages gags."""
  def __init__(self):
    self._gags = []
    self._gagregexp = None

  def addGag(self, gag):
    """ Adds a gag to the list.

    arguments:

      'gag' -- (string) the gag pattern to add

    """
    if gag not in self._gags:
      self._gags.append(gag)
      self.compileGagRegexp()
    return 1

  def compileGagRegexp(self):
    """ Creates a regexp object of the list of gags."""
    if len(self._gags) > 0:
      gags = []
      # we have to handle special character which could
      # make the regular expression unhappy--so we do
      # this double loop thing--which should be pretty
      # quick....
      for mem in self._gags:
        for c in mem:
          if c in string.punctuation:
            mem.replace(c, "\\" + c)
        gags.append(mem)
         
      # join all the gags into a string separated by |
      # so it's a this or this or this or this...  regexp.
      str = "(" + string.join(gags, '|') + ")"
      self._gagregexp = re.compile(str)
    else:
      self._gagregexp = None

  def clear(self):
    """ Removes all the gags."""
    self._gags = []
    self.compileGagRegexp()
         
  def removeGags(self, text):
    """ Removes a specific gag from the list.

    Returns a list of the gags that were removed.
    """
    badgags = utils.expand(text, self._gags)

    for mem in badgags: 
      self._gags.remove(mem)

    self.compileGagRegexp()

    return badgags
    
  def getGags(self):
    """ Returns the list of gags."""
    self._gags.sort()
    return self._gags

  def removeGaggedText(self, text):
    """ Takes text in if it's to be gagged, returns an empty string

    arguments:
      
      'text' -- (string) input string

    """
    if text and self._gagregexp:
      if self._gagregexp.search(text):
        text = ''

    return text

  def getInfo(self):
    """ Returns information about the gags in here.

    This is used by #gag to tell all the gags involved
    as well as #write which takes this information and dumps
    it to the file.
    """
    if len(self._gags) == 0:
      return ''

    data = ''
    self._gags.sort()
    for mem in self._gags:
      data = data + lyntin.commandchar + "gag " + mem + "\n"

    return data[:-1]

  def getCount(self):
    """ Returns the number of gags we're managing."""
    return len(self._gags)


  def filter(self, args):
    """
    Mud_filger_hook function to remove gagged text that
    comes from the mud.
    """
    text = args[-1]
    return self.removeGaggedText(text)
