#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: highlight.py,v 1.3 2002/07/07 04:53:45 willhelm Exp $
#######################################################################
"""
This module defines the HighlightManager which handles highlights.
"""
import string
import manager, utils, lyntin, hooks, exported, modutils

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

class HighlightData:
  def __init__(self):
    self._highlights = {}
    self._currcolor = [-1,-1,-1]
    self._colorleftover = ''

  def __copy__(self):
    hm = HighlightManager()
    for mem in self._highlights.keys():
      hm.addHighlight(self._highlights[mem][0], mem)
    return hm

  def addHighlight(self, style, text):
    """ Adds a highlight to the dict.

    arguments:
      
      'style' -- (string) the style to highlight the text as

      'text' -- (string) the text to highlight
    """
    style = style.lower()
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
    badhighlights = utils.expand_text(text, self._highlights.keys())

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
      self._currcolor, self._colorleftover = utils.figure_color(textlist, self._currcolor, self._colorleftover)

      text = string.join(textlist, "")

    return text

  def highlight(self, textlist, place, memlength, hl):
    """
    Takes a bunch of stuff and applies the highlight involved.  
    It's messy.

    arguments:

      'textlist' -- a list of strings

      'place' -- if the textlist were concatenated without
                 ansi color codes, place would be the index
                 of where the highlight should start

      'memlength' -- the length of the string to be highlighted

      'hl' -- the highlight to apply

    returns:

      the new textlist

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
    newcolor = utils.figure_color(newlist, self._currcolor)[0]
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
        newcolor = utils.figure_color([textlist[j]], newcolor, '')[0]

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

    list = self._highlights.keys()

    if text:
      list = utils.expand_text(text, list)

    data = []
    for mem in list:
      data.append("%shighlight {%s} {%s}" % 
                  (lyntin.commandchar, self._highlights[mem][0], mem))

    return string.join(data, "\n")

  def getStatus(self):
    """ Returns a one-liner describing this data object

    returns:
      
      (string) a one liner describing this object
    """
    return "%d highlight(s)." % len(self._highlights.keys())


class HighlightManager(manager.Manager):
  def __init__(self):
    self._highlights = {}

  def addHighlight(self, ses, style, text):
    if not self._highlights.has_key(ses):
      self._highlights[ses] = HighlightData()
    self._highlights[ses].addHighlight(style, text)

  def clear(self, ses):
    if self._highlights.has_key(ses):
      self._highlights[ses].clear()

  def removeHighlights(self, ses, text):
    if self._highlights.has_key(ses):
      return self._highlights[ses].removeHighlights(text)
    return []

  def getHighlights(self, ses):
    if self._highlights.has_key(ses):
      return self._highlights[ses].getHighlights()
    return []

  def getInfo(self, ses, text=""):
    if self._highlights.has_key(ses):
      return self._highlights[ses].getInfo(text)
    return ""

  def getStatus(self, ses):
    if self._highlights.has_key(ses):
      return self._highlights[ses].getStatus()
    return "0 highlight(s)."

  def addSession(self, newsession, basesession=None):
    """ over-ridden from manager.Manager."""
    if basesession:
      if self._highlights.has_key(basesession):
        hdata = self._highlights[basesession]
        for mem in hdata._highlights.keys():
          self.addHighlight(newsession, hdata._highlights[mem][0], mem)

  def removeSession(self, ses):
    """ over-ridden from manager.Manager."""
    if self._highlights.has_key(ses):
      del self._highlights[ses]

  def persist(self, args):
    """
    write_hook function for persisting the state of our session.
    """
    ses = args[0]
    file = args[1]
    data = self.getInfo(ses)
    if data:
      file.write(data + "\n")

  def filter(self, args):
    ses = args[0]
    text = args[-1]

    if lyntin.ansicolor == 0:
      return utils.filter_ansi(text)
    else:
      if self._highlights.has_key(ses):
        return self._highlights[ses].expand(text)

    return text


commands_dict = {}

def highlight_cmd(ses, args, input):
  """
  With no arguments, prints all highlights.
  With one argument, prints all highlights which match the arg.
  With multiple arguments, creates a highlight.

  Highlights enable you to colorfully "tag" text that's of interest
  to you with the given style.  This may not work or fully work in
  all ui's.

  Styles available are:
     bold     black    grey           b black
     blink    red      light red      b red
     reverse  green    light green    b green
              yellow   light yellow   b yellow
              blue     light blue     b blue
              magenta  light magenta  b magenta
              cyan     light cyan     b cyan
              white    light white    b white

  Highlights also handle *.  So '*word*' will highlight an entire line
  with "word" in it.  '*word' will highlight the line up to "word".  
  'word*' will highlight the line from "word" to the end.

  ex:
     #highlight {green} {Sven arrives.}
     #highlight {reverse,green} {Sven arrives.}

  category: commands
  """
  style = args["style"]
  text = args["text"]
  quiet = args["quiet"]

  if not text and not style:
    data = exported.get_manager("highlight").getInfo(ses)
    if data == '':
      data = "highlight: no highlights defined."

    exported.write_message(data)
    return

  if text and style:
    exported.get_manager("highlight").addHighlight(ses, style, text)
    if not quiet:
      exported.write_message("highlight: {%s} {%s} added." % (style, text))

commands_dict["highlight"] = (highlight_cmd, "style= text= quiet:boolean=false")


def unhighlight_cmd(ses, args, input):
  """
  Allows you to remove highlights.

  category: commands
  """
  func = exported.get_manager("highlight").removeHighlights
  modutils.unsomething_helper(args, func, ses, "highlight", "highlights")

commands_dict["unhighlight"] = (unhighlight_cmd, "str= quiet:boolean=false")


hm = None

def load():
  """ Initializes the module by binding all the commands."""
  global hm
  modutils.load_commands(commands_dict)
  hm = HighlightManager()
  exported.add_manager("highlight", hm)

  # FIXME - the number controls the order this gets called in the grand
  # scheme of things.  we should probably do something to make this
  # more obvious.
  hooks.mud_filter_hook.register(hm.filter, 90)
  hooks.write_hook.register(hm.persist)

def unload():
  """ Unloads the module by calling any unload/unbind functions."""
  global hm
  modutils.unload_commands(commands_dict.keys())
  exported.remove_manager("highlight")
  hooks.mud_filter_hook.unregister(hm.filter)
  hooks.write_hook.unregister(hm.persist)

# Local variables:
# mode:python
# py-indent-offset:2
# tab-width:2
# End:
