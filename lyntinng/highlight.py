#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: highlight.py,v 1.18 2002/05/05 16:34:51 willhelm Exp $
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
    """ Adds a highlight to the dict.

    arguments:
      
      'style' -- (string) the style to highlight the text as

      'text' -- (string) the text to highlight
    """
    self._highlights[text] = (style, self._getMarkup(style))
    return 1

  def _getMarkup(self, style):
    """
    Looks at the style (which is a comma separated list of 
    styles) and figures out the markup string and returns it.

    arguments:

      'style' -- (string) the style to retrieve markup for

    returns:

      (string) the ansi code markup for the given style
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
    self._highlights.clear()

  def removeHighlights(self, text):
    """ Removes highlights from the list.

    Returns a list of tuples of highlight item/highlight that
    were removed.

    arguments:

      'text' -- (string) the text to match on

    returns:

      list of tuples of (text, style)
    """
    badhighlights = utils.expand(text, self._highlights.keys())

    ret = []
    for mem in badhighlights:
      ret.append((mem, self._highlights[mem][0]))
      del self._highlights[mem]

    return ret

  def getHighlights(self):
    """ Returns the keys of the highlight dict.

    returns:
      
      sorted list of strings
    """
    list = self._highlights.keys()
    list.sort()
    return list

  def expand(self, text):
    """ Looks at mud data and performs any highlights.

    It returns the final text--even if there were no highlights.

    arguments:

      'text' -- (string) input text

    returns:

      (string) the finalized text
    """
    if text:
      for mem in self._highlights.keys():
        if mem[0] == "*" and mem[-1] == "*":
          if text.find(mem[1:-1]) > -1:
            text = (self._highlights[mem][1] + utils.filter_ansi(text) + 
                                     chr(27) + "[0m")

        elif mem[0] == "*":
          end = text.find(mem[1:])
          while (end > -1):
            end = end + len(mem[1:])
            text = (self._highlights[mem][1] + utils.filter_ansi(text[:end]) + 
                                     chr(27) + "[0m" + text[end:])
            end = text.find(mem[1:], end + len(self._highlights[mem][1]) + 1)

        elif mem[-1] == "*":
          begin = text.find(mem[:-1])
          while (begin > -1):
            text = (text[:begin] + self._highlights[mem][1] + 
                          utils.filter_ansi(text[begin:]) + chr(27) + "[0m")
            begin = text.find(mem[:-1], begin + len(self._highlights[mem][1]) + 1)
                                   
        else:
          text = text.replace(mem, self._highlights[mem][1] + mem + 
                                     chr(27) + "[0m")

    return text

  def getInfo(self, text=""):
    """ Returns information about the highlights in here.

    This is used by #highlight to tell all the highlights involved
    as well as #write which takes this information and dumps
    it to the file.

    arguments:

      'text=""' -- (string) the text to match on

    returns:

      one big string of things.
    """
    if len(self._highlights.keys()) == 0:
      return ''

    if text=='':
      list = self._highlights.keys()
    else:
      list = utils.expand(text, self._highlights.keys())

    data = []
    for mem in list:
      data.append("%shighlight {%s} {%s}" % 
                  (lyntin.commandchar, self._highlights[mem][0], mem))

    return string.join(data, "\n")

  def getCount(self):
    """ Returns the total number of highlights we're managing.

    returns:
      
      (int) the number of highlights we're managing
    """
    return len(self._highlights.keys())


  def filter(self, args):
    text = args[-1]
    if lyntin.ansicolor == 0:
      return utils.filter_ansi(text)
    else:
      return self.expand(text)
