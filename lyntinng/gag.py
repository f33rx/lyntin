#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: gag.py,v 1.4 2002/02/03 04:27:50 willhelm Exp $
#######################################################################
"""
This module defines the GagManager which handles gags in Lyntin.
"""
import re, string
import utils, lyntin

class GagManager:
  """ Manages gags."""
  def __init__(self):
    self._gags = []
    self._gagregexp = None

  def addGag(self, gag):
    """ Adds a gag to the list.

    arguments:

      'gag' -- (string) the gag pattern to add

    """
    self._gags.append(gag)
    self.compileGagRegexp()
    return 1

  def compileGagRegexp(self):
    """ Creates a regexp object of the list of gags."""
    if self._gags != []:
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
    """ Takes text in and removes anything that is gagged."""
    if text and self._gagregexp:
      lines = text.split('\r\n')
      ret = []

      # shoot through looking for matches of the regexp
      for line in lines:
        # if we find one--we WHACK it!
        if not self._gagregexp.search(line):
          ret.append(line)

      text = string.join(ret, '\r\n')

    return text

  def getInfo(self):
    """ Returns information about the gags in here.

    This is used by #gag to tell all the gags involved
    as well as #write which takes this information and dumps
    it to the file.
    """
    if self._gags == []:
      return ''

    data = ''
    self._gags.sort()
    for mem in self._gags:
      data = data + lyntin.commandchar + "gag " + mem + "\n"

    return data[:-1]
