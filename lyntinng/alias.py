#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: alias.py,v 1.11 2002/05/02 23:39:07 willhelm Exp $
#######################################################################
"""
This module defines the AliasManager which handles aliases,
compiling, and checking and such.
"""
import manager, utils, lyntin, engine

class AliasManager(manager.Manager):
  """ Manages aliases."""
  def __init__(self):
    self._aliases = {}

  def addAlias(self, name, expansion):
    """ Adds an alias to the dict.

    arguments:

      'name' -- (string) the alias name

      'expansion' -- (string) the alias expansion
    """
    self._aliases[name] = expansion

  def clear(self):
    """ Removes all the aliases."""
    self._aliases.clear()

  def removeAliases(self, text):
    """ Removes aliases from the list.

    Returns a list of tuples of alias name/expansion that
    were removed.

    arguments:

      'text' -- (string) the text which when run through
                util.expand gives us the aliases to remove

    returns:

      list of (name, expansion) tuples
    
    """
    badaliases = utils.expand(text, self._aliases.keys())

    ret = []
    for mem in badaliases:
      ret.append((mem, self._aliases[mem]))
      del self._aliases[mem]

    return ret

  def getAliases(self):
    """ Returns the keys of the alias dict.

    returns:

      list of strings

    """
    list = self._aliases.keys()
    list.sort()
    return list

  def getAlias(self, alias):
    """ Does an alias lookup and returns the alias in question or
    an empty string.

    returns:

      (string) empty string or the alias expansion

    """
    if self._aliases.has_key(alias):
      return self._aliases[alias]
    else:
      return ""

  def expand(self, input):
    """ Looks at user input and expands any aliases involved.

    It'll return the expansion if there is one.  Otherwise
    it returns None.

    arguments:

      'input' -- the user input

    returns:

      the alias expansion for the given input if it's an
      alias, or None if it is not.

    """
    if len(input) > 0:
      # pull out the first word of the input
      firstword = input.split(' ', 1)[0]

      # if we match an alias, we return the expansion
      if firstword in self._aliases.keys():
        return self._aliases[firstword]            

    return None

  def getInfo(self, text=""):
    """ Returns information about the aliases in here.

    This is used by #alias to tell all the aliases involved
    as well as #write which takes this information and dumps
    it to the file.

    arguments:

      'text=""' -- (string) the text to match

    arguments:

      a string telling about all the aliases and expansions
      in this manager.
    """
    if len(self._aliases.keys()) == 0:
      return ''

    if text=='':
      list = self._aliases.keys()
    else:
      list = utils.expand(text, self._aliases.keys())

    data = ''
    for mem in list:
      data = (data + lyntin.commandchar + 
              "alias {" + mem + "} {" + self._aliases[mem] + "}\n")

    return data[:-1]

  def getCount(self):
    """ Returns the alias count.

    returns:

      (int) the number of aliases managed
    """
    return len(self._aliases.keys())

  def filter(self, tuple):
    """ Handle the filtering of input through the current aliases.
        If input gets changed then we pass it back to
        engine.myengine.HandleUserData and return None to stop this
        chain of filtering.

    arguments:

      tuple: user_filter_hook arg tuple (session, internal, input,
      filtered)

    returns:

      filtered text or None if any changes took place.
    """
    # we check for aliases here--and if we find some, we
    # do the variable expansion and then recurse over the result
    session = tuple[0]
    internal = tuple[1]
    text = tuple[-1]
    aliasexpansion = self.expand(text)

    if aliasexpansion:
      aliasexpansion = utils.replace_vars(text,aliasexpansion)
      engine.myengine.handleUserData(aliasexpansion, internal, session)
      return None
    else:
      return text
