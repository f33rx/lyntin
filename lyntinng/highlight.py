#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: highlight.py,v 1.11 2002/03/19 23:05:44 willhelm Exp $
#######################################################################
"""
This module defines the HighlightManager which handles highlights.
"""
import manager, utils, lyntin

STYLEMAP = {
             "bold": "1",
             "blink": "5",
             "reverse": "7",
             "black": "30",
             "red": "31",
             "green": "32",
             "yellow": "33",
             "blue": "34",
             "magenta": "35",
             "cyan": "36",
             "white": "37",
             "grey": "1;30",
             "light red": "1;31",
             "light green": "1;32",
             "light yellow": "1;33",
             "light blue": "1;34",
             "light magenta": "1;35",
             "light cyan": "1;36",
             "light white": "1;37",
             "b black": "40",
             "b red": "41", 
             "b green": "42",
             "b yellow": "43",
             "b blue": "44",
             "b magenta": "45",
             "b cyan": "46",
             "b white": "47"
           }

class HighlightManager(manager.Manager):
  """ Manages highlights."""
  def __init__(self):
    self._highlights = {}

  def addHighlight(self, style, text):
    """ Adds a highlight to the dict."""
    self._highlights[text] = (style, self._getMarkup(style))
    return 1

  def _getMarkup(self, style):
    """
    Looks at the style (which is a comma separated list of 
    styles) and figures out the markup string and returns it.
    """
    styles = style.split(",")
    markup = ""
    for mem in styles:
      mem = mem.strip()
      if STYLEMAP.has_key(mem):
        markup = markup + STYLEMAP[mem] + ";"
    return chr(27) + "[" + markup[:-1] + "m"

  def clear(self):
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
      ret.append((mem, self._highlights[mem][0]))
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
    """
    if len(input) > 0:
      for text in self._highlights.keys():
        if text[0] == "*" and text[-1] == "*":
          input = self._highlights[text][1] + input + "[0m"
        elif text[1] == "*":
          input = input.replace(text, self._highlights[text][1] +
                                      text + chr(27) + "[0m")
        elif text[-1] == "*":
          input = input.replace(text, self._highlights[text][1] +
                                      text + chr(27) + "[0m")
        else:
          input = input.replace(text, self._highlights[text][1] +
                                      text + chr(27) + "[0m")

    return input

  def getInfo(self, text=''):
    """ Returns information about the highlights in here.

    This is used by #highlight to tell all the highlights involved
    as well as #write which takes this information and dumps
    it to the file.
    """
    if len(self._highlights.keys()) == 0:
      return ''

    list = []
    if text=='':
      list = self._highlights.keys()
    else:
      list = utils.expand(text, self._highlights.keys())

    data = ''
    for mem in list:
      data = (data + lyntin.commandchar + 
              "highlight {" + self._highlights[mem][0] + "} {" + mem + "}\n")

    return data[:-1]

  def getCount(self):
    """ Returns the total number of highlights we're managing."""
    return len(self._highlights.keys())
