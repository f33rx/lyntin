#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2001
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: highlight.py,v 1.1.1.1 2001/12/01 04:27:46 willhelm Exp $
#######################################################################
"""
This module defines the HighlightManager which handles highlights.
"""
import utils

COLORMAP = {
             "black": chr(27) + "[40m",
             "red": chr(27) + "[41m", 
             "green": chr(27) + "[42m",
             "yellow": chr(27) + "[43m",
             "blue": chr(27) + "[44m",
             "magenta": chr(27) + "[45m",
             "cyan": chr(27) + "[46m"
           }

class HighlightManager:
   """ Manages highlights."""
   def __init__(self):
      self._highlights = {}

   def addHighlight(self, item, color):
      """ Adds a highlight to the dict."""
      self._highlights[item] = color
      return 1

   def clearHighlights(self):
      """ Removes all the highlights."""
      for mem in self._highlights.keys():
         del self._highlights[mem]

   def removeHighlights(self, text):
      """ Removes highlights from the list.

      Returns a list of tuples of highlight item/highlight that
      were removed.
      """
      badhighlights = utils.expand(text, self._highlights.keys())

      ret = []
      for mem in badhighlights:
         ret.append((mem, self._highlights[mem]))
         del self._highlights[mem]

      return ret

   def getHighlights(self):
      """ Returns the keys of the highlight dict."""
      list = self._highlights.keys()
      list.sort()
      return list

   def expand(self, input):
      """ Looks at mud data and performs any highlights.

      It returns the final text--even if there were no highlights.
      # FIXME -- this isn't done correctly.
      """
      if len(input) > 0:
         for mem in self._highlights.keys():
            input = input.replace(mem, COLORMAP[self._highlights[mem]] + 
                                       mem + 
                                       chr(27) + "[40m")

      return input

   def getHighlightInfo(self, text=''):
      """ Returns information about the highlights in here.

      This is used by #highlight to tell all the highlights involved
      as well as #write which takes this information and dumps
      it to the file.
      """
      if self._highlights.keys() == []:
         return ''

      list = []
      if text=='':
         list = self._highlights.keys()
      else:
         list = utils.expand(text, self._highlights.keys())

      data = ''
      for mem in list:
         data = (data + "#highlight {" + mem + "} {" + 
                        self._highlights[mem] + "}\n")

      return data[:-1]
