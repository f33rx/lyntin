#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: ansi.py,v 1.5 2002/10/26 04:32:39 willhelm Exp $
#######################################################################
"""
This holds a series of classes and functions for helping to manipulate
ANSI color codes.

In general, Lyntin keeps the data from the mud intact without doing any
transformations on it letting the ui do the transformations it needs to
do to display the mud data.  The exception to this is when the user has
shut off mudansi using the #config command.  Then we'll whack any incoming
ANSI color stuff before moving it around.
"""
import re

# for finding ANSI color sequences
ANSI_COLOR_REGEXP = re.compile(chr(27) + '\[[0-9;]*[m]')

# these are bits for bitmasks
NORMAL = 0
BOLD = 1
UNDERLINE = 2
BLINK = 4
REVERSE = 8
NONDISPLAYED = 16


class Color:
  def __init__(self, fg=-1, bg=-1, options=0):
    self._fg = fg
    self._bg = bg
    self._options = options

  def getFG(self):
    """
    Returns the foreground color or -1 if no color is set.

    @returns: the foreground color which is 30 through 37 or -1 if
        it's not set
    @rtype: int
    """
    return self._fg

  def setFG(self, fg):
    """
    Sets the foreground color.

    @param fg: the new foreground color (30 through 37) or -1 to
        unset
    @type  fg: int

    @raises ValueError: if the foreground color isn't valid
    """
    if (fg >= 30 and fg <= 37) or fg == -1:
      self._fg = fg
    else:
      raise ValueError, "Not a valid foreground color: '%i'" % fg

  def getBG(self):
    """
    Returns the background color or -1 if no color is set.

    @returns: the background color which is 40 through 47 or -1 if
        it's not set
    @rtype: int
    """
    return self._bg

  def setBG(self, bg):
    """
    Sets the background color.

    @param bg: the new background color (40 through 47) or -1 to
        unset
    @type  bg: int

    @raises ValueError: if the background color isn't valid
    """
    if (bg >= 40 and bg <= 47) or bg == -1:
      self._bg = bg
    else:
      raise ValueError, "Not a valid background color: '%i'" % bg

  def setOption(self, item):
    """
    Sets an option.

    @param item: the flag to check--see flag constants in ansi.py
    @type  item: int
    """
    self._options = self._options | item

  def unsetOption(self, item):
    """
    Unsets an option.

    @param item: the flag to check--see flag constants in ansi.py
    @type  item: int
    """
    self._options = self._options ^ item

  def checkOption(self, item):
    """
    Checks whether an option is set.

    @param item: the flag to check--see flag constants in ansi.py
    @type  item: int

    @returns: 0 if it's not set, 1 if it is.
    @rtype: boolean
    """
    return self._options & item


def filter_ansi(text):
  """
  Takes in text and filters out the ANSI color codes.

  @returns: text without ANSI color codes
  @rtype: string
  """
  return ANSI_COLOR_REGEXP.sub('', text)


def is_color_token(token):
  """
  Returns whether or not this is a color token.

  @param token: the token in question
  @type  token: string

  @return: 1 if it's color, 0 if not
  @rtype: boolean
  """
  if len(token) == 0:
    return 0

  return ANSI_COLOR_REGEXP.match(token)


def fix_color(color):
  """
  Helper function for debugging--it'll fix a color token
  so it's readable in ascii.

  @param color: the color token
  @type  color: string

  @return: the pretty string
  @rtype: string
  """
  return color.replace(chr(27), "ESC")


def split_ansi_from_text(text):
  """
  Takes in a string and returns a list of text and ansi tokens.

  @param text: the full string to split up
  @type  text: string

  @return: list of text and ansi color tokens
  @rtype: list of strings
  """
  global ANSI_COLOR_REGEXP

  matchob = ANSI_COLOR_REGEXP.search(text)
  if matchob:
    textlist = []
    marker = 0
    while matchob:
      (b, e) = matchob.span()

      if marker == b:
        textlist.append(text[b:e])
      else:
        textlist.append(text[marker:b])
        textlist.append(text[b:e])

      marker = e
      matchob = ANSI_COLOR_REGEXP.search(text, marker)

    # we do this to handle ansi color sequences which are broken
    # between two network chunks
    if marker < len(text):
      esc = text.rfind('\33', marker)
      if esc != -1:
        for i in range(esc, len(text)):
          c = text[i]

          if c.isdigit() or c == ";" or c == "[":
            continue
          else:
            esc = -1

      if esc == -1:
        textlist.append(text[marker:])
      else:
        textlist.append(text[marker:esc])
        textlist.append(text[esc:])

    return textlist
  return [text]


def figure_color(textlist, currentcolor, leftover=""):
  """ 
  Takes a textlist of text and color tokens and figures out
  the latest current color.

  @param textlist: the list of string and ansi color code tokens
  @type  textlist: list of strings

  @param currentcolor: a tuple of (options, foreground, background) 
      that represent the current color
  @type  currentcolor: (int, int, int)

  @param leftover: if we encounter a half done color code, we throw
      it in the leftover string.  the leftover gets prepended
      to the textlist element on the next run of figure_color
  @type  leftover: string

  @return: the new currentcolor and leftover as a tuple
  @rtype: ((int, int, int), string)
  """
  if type(textlist) == type(''):
    textlist = split_ansi_from_text(textlist)

  if leftover:
    first = leftover + textlist[0]
    matchob = ANSI_COLOR_REGEXP.search(first)
    if matchob:
      (b, e) = matchob.span()
      textlist.insert(0, first[:e])
      textlist[1] = first[e:]
    leftover = ''

  for color in textlist:
    if is_color_token(color):
      color = color[2:-1]

      # handles the case where it's ESC[m
      if color == "":
        currentcolor = [-1, -1, -1]

      # handles other cases!
      else:
        color = color.split(";")
        for i in color:
          if not i.isdigit():
            continue

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

  # we're looking for leftover pieces here
  if len(textlist) > 0:
    mem = textlist[-1]
    esc = mem.find('\33')
    if esc != -1:
      for i in range(esc, len(mem)):
        c = mem[i]

        if c.isdigit() or c == ";" or c == "[":
          continue
        else:
          esc = -1

      if esc != -1:
        leftover = mem
      
  return currentcolor, leftover


def convert_tuple_to_ansi(token):
  """
  Takes in a color tuple like what figure_color creates
  and converts it into an ANSI color sequence.

  @param token: the color tuple (option, fg, bg)
  @type  token: (int, int, int)

  @return: the ANSI color string
  @rtype: string
  """
  options = token[0]
  fg = token[1]
  bg = token[2]

  color = []

  if options == 1:
    color.append("1")

  if fg != -1:
    color.append(str(fg))

  if bg != -1:
    color.append(str(bg))

  if len(color) == 0:
    return chr(27) + "[0m"

  return chr(27) + "[" + ";".join(color) + "m"

# Local variables:
# mode:python
# py-indent-offset:2
# tab-width:2
# End:
