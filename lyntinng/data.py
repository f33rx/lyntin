#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: data.py,v 1.1 2002/03/29 23:47:05 willhelm Exp $
#######################################################################
"""
This module defines the databuffer for grepping data.  It keeps 
the last x lines of mud data so you can see lines in context.  This 
is useful for modules.
"""

import string, re

class DataBuffer:
  """
  Databuffer class to hold a certain amount of data from
  the mud for the purposes of context grepping.
  """
  
  def __init__(self):
    # buffer is organized oldest to newest.  so _buffer[0] is
    # the most stale and _buffer[-1] is the most new.
    self._buffer = []
    self._size = 50
  
  def addData(self, text):
    """
    Adds data to the buffer by thinking about everything
    in terms of lines.
    
    arguments:
    
      'text' -- (string) the text to add to the buffer
    """
    lines = text.splitlines(1)
    for mem in lines:
      if len(self._buffer) == 0 or self._buffer[-1][-1] == '\n':
        self._buffer.append(mem)
      else:
        self._buffer[-1] += mem

    while (len(self._buffer) > self._size):
      del self._buffer[0]
  
  def clear(self):
    """ Removes all the deeds."""
    self._buffer = []
  
  def resize(self, newsize=50):
    """ Changes the buffer max.

    arguments:

      'newsize=50' -- (int) the new buffer max size
    """
    self._size = newsize

  def greplines(self, pattern):
    """
    Returns a list of all the lines in the databuffer that
    match the given pattern.

    arguments:

      'pattern' -- (string) the match pattern
 
    returns:

      (list of strings) a list of the lines that matched the
      pattern
    """
    ret = []
    cpattern = re.compile(pattern)

    for mem in self._buffer:
      if cpattern.search(mem):
        ret.append(mem)
    return ret

  def grepbuffer(self, pattern):
    """
    Similar to greplines, except this greps the buffer
    as a whole allowing you to match across multiple lines.

    arguments:

      'pattern' -- (string) the match pattern

    returns:

      (list of strings) all the matches from the buffer
    """
    buffer = string.join(self._buffer, "")

    ret = []
    cpattern = re.compile(pattern)

    match = cpattern.search(buffer)
    while match:
      s, e = match.span()
      ret.append(buffer[s:e])

      match = cpattern.search(buffer, e)

    return ret
