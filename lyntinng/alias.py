#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2001
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id$
#######################################################################
"""
This module defines the AliasManager which handles aliases,
compiling, and checking and such.
"""
import utils

class AliasManager:
   """ Manages aliases."""
   def __init__(self):
      self._aliases = {}

   def addAlias(self, name, expansion):
      """ Adds an alias to the dict."""
      self._aliases[name] = expansion
      return 1

   def clearAliases(self):
      """ Removes all the aliases."""
      for mem in self._aliases.keys():
         del self._aliases[mem]

   def removeAliases(self, text):
      """ Removes aliases from the list.

      Returns a list of tuples of alias name/expansion that
      were removed.
      """
      badaliases = utils.expand(text, self._aliases.keys())

      ret = []
      for mem in badaliases:
         ret.append((mem, self._aliases[mem]))
         del self._aliases[mem]

      return ret

   def getAliases(self):
      """ Returns the keys of the alias dict."""
      list = self._aliases.keys()
      list.sort()
      return list

   def getAlias(self, alias):
      """ Does an alias lookup and returns the alias in question or
      an empty string."""
      if self._aliases.has_key(alias):
         return self._aliases[alias]
      else:
         return ""

   def expand(self, input):
      """ Looks at user input and expands any aliases involved.

      It'll return the expansion if there is one.  Otherwise
      it returns None.
      """
      if len(input) > 0:
         # pull out the first word of the input
         firstword = input.split(' ', 1)[0]

         # if we match an alias, we return the expansion
         if firstword in self._aliases.keys():
            return self._aliases[firstword]            

      return None

   def getAliasInfo(self, text=''):
      """ Returns information about the aliases in here.

      This is used by #alias to tell all the aliases involved
      as well as #write which takes this information and dumps
      it to the file.
      """
      if self._aliases.keys() == []:
         return ''

      list = []
      if text=='':
         list = self._aliases.keys()
      else:
         list = utils.expand(text, self._aliases.keys())

      data = ''
      for mem in list:
         data = data + "#alias {" + mem + "} {" + self._aliases[mem] + "}\n"

      return data[:-1]
