#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: history.py,v 1.4 2002/04/05 23:55:46 willhelm Exp $
#######################################################################
"""
The history manager keeps track of the last 30 commands entered
by the user in Lyntin.  It is on a global scoping--we don't keep
track of a history per session.
"""

class HistoryManager:
  """ Manages user data history.

  The user enters commands--this is how they interact with Lyntin.
  We keep track of the last 30 of those commands in this module.
  We also give the user the ability to recall and edit those
  commands--allowing them to fix mistakes they may have typed
  and things of that nature.
  """
  def __init__(self):
    self._history = []

  def getHistoryItem(self, userinput, calledbyuser=1):
    """
    This retrieves the item (if it exists) and performs the 
    substitutions (if we need to).

    arguments:

      'userinput' -- what the user typed--we'll use this to figure
                     out which item they're referring to and
                     whether to apply a substitution

    """
    tokens = userinput.split(" ", 1)

    # grab the first (and possibly only) token and remove the !
    index = tokens[0][1:]

    # if it's very short, we're looking at the last thing typed
    # (prior to this thing they typed)
    if len(index) == 0:
      returninput = self._history[1]
    else:
      try:
        returninput = self._history[int(index)+1]
      except:
        return -1

    # check to see if they want to do a substitution
    if len(tokens) > 1:
      # this is kind of sketchy--we do a substitution but
      # split the thing based on the first = sign
      try:
        i = tokens[1].find("=")
        returninput = returninput.replace(tokens[1][:i], tokens[1][i+1:])
      except:
        # something's wrong with what they typed, so we don't
        # do a substitution
        # FIXME - we should probably error out...  need to think about this
        pass

    # this is a side-effect of this function--if we were called
    # by the user, it means that the item in position 0 of
    # self._history is actually a history command--so we replace
    # it with the something nice we just discovered.
    if calledbyuser:
      self._history[0] = returninput

    return returninput

  def getHistory(self):
    """ Returns everything in the history buffer as a list.

    returns:

      list of strings

    """
    return self._history[:]

  def recordHistory(self, input):
    """ Records an item in the history (which is a queue).

    arguments:

      'input' -- the line to record

    """
    # we don't record nothings
    if len(input) == 0:
      return

    self._history.insert(0, input)
    if len(self._history) > 30:
      del self._history[-1]
