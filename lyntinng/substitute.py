#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2001
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id$
#######################################################################
"""
This module defines the SubstituteManager which handles substitutes.
"""
import utils

class SubstituteManager:
   """ Manages substitutes."""
   def __init__(self):
      self._substitutes = {}

   def addSubstitute(self, item, substitute):
      """ Adds a substitute to the dict."""
      self._substitutes[item] = substitute 
      return 1

   def clearSubstitutes(self):
      """ Removes all the substitutes."""
      for mem in self._substitutes.keys():
         del self._substitutes[mem]

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

   def expand(self, input):
      """ Looks at mud data and performs any substitutes.

      It returns the final text--even if there were no substitutes.
      # FIXME -- this isn't done correctly.
      """
      if len(input) > 0:
         for mem in self._substitutes.keys():
            input = input.replace(mem, self._substitutes[mem])

      return input

   def getSubstituteInfo(self, text=''):
      """ Returns information about the substitutes in here.

      This is used by #substitute to tell all the substitutes involved
      as well as #write which takes this information and dumps
      it to the file.
      """
      if self._substitutes.keys() == []:
         return ''

      list = []
      if text=='':
         list = self._substitutes.keys()
      else:
         list = utils.expand(text, self._substitutes.keys())

      data = ''
      for mem in list:
         data = data + "#substitute {" + mem + "} {" + self._substitutes[mem] + "}\n"

      return data[:-1]
