#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: ansi.py,v 1.6 2002/10/27 20:41:32 willhelm Exp $
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


def filter_ansi(text):
  """
  Takes in text and filters out the ANSI color codes.

  @returns: text without ANSI color codes
  @rtype: string
  """
  return ANSI_COLOR_REGEXP.sub('', text)


def is_color_token(token):
  """
  Returns whether or not this is a color token.  It figures this out
  by checking to see if the token matches this regexp: 
  chr(27) + '\[[0-9;]*[m]'

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
  Helper function for debugging--it'll fix a color token so it's 
  readable in ascii.  It just replaces instances of chr(27) with 
  "ESC".

  @param color: the color token
  @type  color: string

  @return: the pretty string
  @rtype: string
  """
  return color.replace(chr(27), "ESC")


def split_ansi_from_text(text):
  """
  Takes in a string and separates it into a list of strings and ansi
  color strings.

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
