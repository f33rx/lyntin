#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: data.py,v 1.8 2002/04/29 23:14:13 willhelm Exp $
#######################################################################
"""
This module defines the databuffer for grepping data.  It keeps 
the last x lines of mud data so you can see lines in context.  This 
is useful for modules.
"""

import string, re
import utils

class DataBuffer:
  """
  Databuffer class to hold a certain amount of data from
  the mud for the purposes of context grepping.
  """
  
  def __init__(self):

    # buffer is organized oldest to newest.  so _buffer[0] is
    # the most stale and _buffer[-1] is the most new.
    self._buffer = []
    self._size = 10000
  
  def addData(self, text):
    """
    Adds data to the buffer by thinking about everything
    in terms of lines.
    
    arguments:
    
      'text' -- (string) the text to add to the buffer
    """
    text = utils.filter_ansi(utils.filter_cm(text))
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

  def greplines(self, pattern, numlines=300):
    """
    Returns a list of all the lines in the databuffer that
    match the given pattern.

    arguments:

      'pattern' -- (string) the match pattern
 
      'numlines' -- (int) number of lines to search back through.  0
                    will get all lines in buffer 

    returns:

      (list of strings) a list of the lines that matched the
      pattern
    """
    ret = []
    cpattern = re.compile(pattern)

    for mem in self._buffer[-numlines:]:
      if cpattern.search(mem):
        ret.append(mem)
    return ret

  def fetchbuffer(self):
    """
    Grabs the whole buffer.

    returns:

      string
    """
    return string.join(self._buffer, "")

  def grepbuffer(self, pattern, numlines=300):
    """
    Similar to greplines, except this greps the buffer
    as a whole allowing you to match across multiple lines.

    arguments:

      'pattern' -- (string) the match pattern

      'numlines' -- (int) number of lines to search back through.  0
                    will get all lines in buffer 

    returns:

      (list of strings) all the matches from the buffer
    """
    buffer = string.join(self._buffer[-numlines:], "")

    ret = []
    cpattern = re.compile(pattern)

    matches = cpattern.findall(buffer)
    for match in matches:
      ret.append(match)

    return ret

# Local variables:
# mode:python
# py-indent-offset:2
# tab-width:2
# End:
