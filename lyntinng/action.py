#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: action.py,v 1.29 2002/05/27 23:12:59 jmberne Exp $
#######################################################################
"""
This module defines the ActionManager which handles managing actions 
(triggers) and expansion of actions.
"""
import re, string, copy
import manager, utils, event, lyntin

# the placement variable regular expression
VARREGEXP = re.compile('%_?(\d+)')

class ActionManager(manager.Manager):
  """ Extends the base manager class to manages actions."""
  def __init__(self):
    self._actions = {}

  def __copy__(self):
    ac = ActionManager()
    for mem in self._actions.keys():
      ac.addAction(mem, self._actions[mem][2], self._actions[mem][3])
    return ac

  def _compileAction(self, trigger):
    """
    Converts a trigger with pattern variables into a compiled
    regular expression and returns the regular expression.

    arguments:

      'trigger' -- (string) the trigger string to compile into
                   a regexp

    returns:

      (SRE_Pattern) returns a compiled regexp pattern ob

    """
    regexp = re.sub('%[0-9]+', '(.+?)', trigger)
    regexp = re.sub('%_[0-9]+', '(\S+?)', regexp)
    return re.compile(regexp)

  def addAction(self, trigger, response, onetime=0):
    """
    Compiles a trigger pattern and adds the entire action to the
    hash.

    arguments:

      'trigger' -- (string) the trigger pattern

      'response' -- (string) what to do when the trigger pattern
                    is found

      'onetime' -- (boolean) whethere this should be an auto-removing action

    returns:

      (int) always returns a 1

    """
    compiled = self._compileAction(trigger)
    self._actions[trigger] = (trigger, compiled, response, onetime)
    return 1

  def clear(self):
    """
    Clears all the stored actions from the action manager.
    """
    self._actions.clear()

  def removeActions(self, text):
    """
    Removes actions that match the given text from the list and
    returns the list of actions that were removed so the calling
    function knows what actually happened.

    arguments:

      'text' -- (string) all actions that match this text pattern
                will be removed.  the text pattern is "expanded" by
                'utils.expand'

    returns:

      list of tuples (trigger, response) of the action.  both
      trigger and response are strings--the same strings used when
      calling 'addAction'.

    """
    badactions = utils.expand(text, self._actions.keys())

    ret = []
    for mem in badactions:
      ret.append((self._actions[mem][0], self._actions[mem][2]))
      del self._actions[mem]

    return ret

  def getActions(self):
    """
    Returns a list of all the actions this actionmanager is currently
    managing.

    returns:

      list of triggers for the actions we're managing.  the trigger
      is a string.

    """
    list = self._actions.keys()
    list.sort()
    return list

  def _getOrderedVars(self, instr):
    """
    Takes in a string and removes any ordered variables
    from it.  Returns a list of the variables.

    arguments:

      'instr' -- (string) the incoming string which may have
                 ordered variables in it.

    returns:

      list of strings of the form '%[0-9]+' for ordered variable
      substitution.

    """
    str = instr[:]
    keylist = []
    specialkeylist = []
    match = VARREGEXP.search(str)
    while match:
      var = match.group(1)
      keylist.append('%' + var)

      # this is not a gsub!
      str = re.sub('%_?\d+', '', str, 1)

      match = VARREGEXP.search(str)

    return keylist

  def checkActions(self, text):
    """
    Checks to see if text triggered any actions.  Any resulting 
    actions will get added as an InputEvent to the queue.

    arguments:

      'text' -- (string) the data coming from the mud to check
                for triggers on

    """
    # FIXME - make sure this works even when lines are broken up.

    matched = []

    # go through all the lines in the data and see if we have
    # any matches
    for (action, actioncompiled, response, onetime) in self._actions.values():
      line = utils.filter_cm(utils.filter_ansi(text))
      match = actioncompiled.search(line)
      if match:
        matched.append((line, action, actioncompiled, response))
        if onetime:
          del self._actions[action]

    # for every match we figure out what the expanded response
    # is and add it as an InputEvent in the queue.  the reason
    # we do a series of separate events rather than one big
    # event with ; separators is due to possible issues with 
    # braces and such in malformed responses.
    for (line, action, actioncompiled, response) in matched:
      match = actioncompiled.search(line)

      # get variables from the action
      actionvars = self._getOrderedVars(action)
      varvals = {}
      # fill in values for all the variables in the match
      for i in xrange(len(actionvars)):
        varvals[actionvars[i]] = match.group(i+1)

      # add special variables
      varvals['%a'] = line.replace(';','_')
            
      # fill in response variables from those that
      # matched on the trigger
      for var in varvals.keys():
        # replace occurrences of '%i' with val
        if response.find(var) > -1:
          response = re.sub(var, varvals[var], response)

        # replace occurrances of '$i' with val replacing ; with \;
        if ("$" + var[1:]).find(response) != -1:
          response = re.sub("$" + var[1:],
                     varvals[var].replace(";", "\;"), 
                     response, 
                     1)

      event.InputEvent(response, internal=1).enqueue()


  def getInfo(self, text=""):
    """ Returns information about the actions in here.

    This is used by #action to tell all the actions involved
    as well as #write which takes this information and dumps
    it to the file.

    arguments:

         'text=""' -- (string) the text to expand on to find
                      actions that the user is interested in

    returns:

      a string of all the action information

    """
    if len(self._actions.keys()) == 0:
      return ''

    if text=='':
      list = self._actions.keys()
    else:
      list = utils.expand(text, self._actions.keys())

    data = []
    for mem in list:
      data.append("%saction {%s} {%s} onetime=%s" % 
              (lyntin.commandchar, mem, self._actions[mem][2], self._actions[mem][3]))

    return string.join(data, "\n")

  def getCount(self):
    """ Returns how many aliases we're managing.

    returns:

      (int) the number of aliases being managed.
    """
    return len(self._actions.keys())

  def filter(self, args):
    """
    Mud_filter_hook function to check for actions when data
    comes from the mud.
    """
    session = args[0]
    text = args[-1]
    if not session._ignoreactions:
      self.checkActions(text)
    return text
