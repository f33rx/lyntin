#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: highlight.py,v 1.21 2002/05/18 03:45:59 willhelm Exp $
#######################################################################
"""
This module defines the HighlightManager which handles highlights.
"""
import string
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
    self._currcolor = [-1,-1,-1]
    self._colorleftover = ''

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
      faketext = utils.filter_ansi(text)
      textlist = utils.split_ansi_from_text(text)
      for mem in self._highlights.keys():

        # first we deal with those silly stars....
        hltext = mem
        if mem[0] == "*":
          hltext = hltext[1:]
        if mem[-1] == "*":
          hltext = hltext[:-1]
        i = faketext.find(hltext)

        # then we go hunting for the unstarred text
        while i != -1:
          begin = i
          end = len(hltext)
          if mem[0] == "*":
            begin = 0
            end = i + len(hltext)
          if mem[-1] == "*":
            end = len(faketext) - begin

          hl = self._highlights[mem][1]
          textlist = self.highlight(textlist, begin, end, hl)
          i = faketext.find(hltext, i + 1)

      # here we sweep through the text string to update our current
      # color and leftover color attributes
      self._currcolor, self._colorleftover = self.figureColor(textlist, self._currcolor)

      text = string.join(textlist, "")

    return text

  def highlight(self, textlist, place, memlength, hl):
    """
    Takes a bunch of stuff and applies the highlight involved.  
    It's messy.
    """
    # first we find the place to stick the highlight thingy.
    i = 0
    for i in range(0, len(textlist)):
      if not utils.is_color_token(textlist[i]):
        if place > len(textlist[i]):
          place -= len(textlist[i])
        else:
          break

    newlist = []
    for mem in textlist[:i]:
      newlist.append(mem)
    newlist.append(textlist[i][:place])
    newcolor = self.figureColor(newlist, self._currcolor)[0]
    newlist.append(hl)

    # if the string to highlight begins and ends in the
    # same token we deal with that and eject
    if len(textlist[i][place:]) >= memlength:
      newlist.append(textlist[i][place:place + memlength])
      newlist.append(chr(27) + "[0m")
      color = self.convertColor(newcolor)
      if color:
        newlist.append(color)
      newlist.append(textlist[i][place + memlength:])
      for mem in textlist[i+1:]:
        newlist.append(mem)

      return newlist


    newlist.append(textlist[i][place:])

    # now we have to find the end of the highlight
    memlength -= len(textlist[i][place:])
    j = i+1
    for j in range(i+1, len(textlist)):
      if not utils.is_color_token(textlist[j]):
        if memlength > len(textlist[j]):
          memlength -= len(textlist[j])
          newlist.append(textlist[j])
        else:
          break
      else:
        newcolor = self.figureColor([textlist[j]], newcolor, '')[0]

    newlist.append(textlist[j][:memlength])
    newlist.append(chr(27) + "[0m")
    color = self.convertColor(newcolor)
    if color:
      newlist.append(color)
    newlist.append(textlist[j][memlength:])

    for mem in textlist[j+1:]:
      newlist.append(mem)

    return newlist

  def convertColor(self, color):
    c = []
    if color[0] != -1:
      c.append(str(color[0]))
    if color[1] != -1:
      c.append(str(color[1]))
    if color[2] != -1:
      c.append(str(color[2]))

    if len(c) == 0:
      c = ''
    else:
      c = chr(27) + "[" + string.join(c, ";") + "m"
    return c

  def figureColor(self, textlist, currentcolor, leftover=-1):
    """ 
    Takes a textlist of text and color tokens and figures out
    the latest current color.
    """
    if leftover == -1:
      leftover = self._colorleftover

    if leftover:
      textlist[0] = leftover + textlist[0]
      leftover = ''

    for mem in textlist:
      if utils.is_color_token(mem):
        color = mem[2:-1]
        color = color.split(";")
        for i in color:
          i = int(i)

          if i == 0:
            # 0 is a reset
            currentcolor = [-1, -1, -1]
      
          elif 0 < i and i < 10:
            # these are ansi color attributes
            currentcolor[0] = i

          elif 30 <= i and i < 40:
            # these are foreground attributes
            currentcolor[1] = i

          elif 40 <= i and i < 50:
            # these are background attributes
            currentcolor[2] = i

    if len(textlist) > 0:
      mem = textlist[-1]
      if len(mem) > 0 and mem[0] == chr(27) and mem[-1] != "m":
        leftover = mem

    return currentcolor, leftover

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
