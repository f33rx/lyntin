#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2001
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: action.py,v 1.4 2002/01/25 20:18:13 willhelm Exp $
#######################################################################
"""
This module defines the ActionManager which handles managing actions 
(triggers) and expansion of actions.
"""
import re
import utils, event, lyntin

# FIXME - should this be here?
VARREGEXP = re.compile('%(\d+)')

class ActionManager:
  """ Manages actions."""
  def __init__(self):
    self._actions = {}

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
    regexp = re.sub('%[0-9]+', '(.*)', trigger)
    return re.compile(regexp)

  def addAction(self, trigger, response):
    """
    Compiles a trigger pattern and adds the entire action to the
    hash.

    arguments:

      'trigger' -- (string) the trigger pattern

      'response' -- (string) what to do when the trigger pattern
                    is found

    returns:

      (int) always returns a 1

    """
    compiled = self._compileAction(trigger)
    self._actions[trigger] = (trigger, compiled, response)
    return 1

  def clear(self):
    """
    Clears all the stored actions from the action manager.
    """
    for mem in self._actions.keys():
      del self._actions[mem]

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
      str = re.sub('%[0-9]+', '', str, 1)

      match = VARREGEXP.search(str)

    return keylist

  def checkActions(self, muddata):
    """
    Checks to see if muddata triggered any actions.  Any resulting 
    actions will get added as an InputEvent to the queue.

    arguments:

      'muddata' -- (string) the data coming from the mud to check
                   for triggers on

    FIXME - make sure this works even when lines are broken up.
    """
    matched = []

    # go through all the lines in the data and see if we have
    # any matches
    for line in muddata.splitlines():
      for (action, actioncompiled, response) in self._actions.values():
        match = actioncompiled.search(line)
        if match:
          line = utils.filter_cm(utils.filter_ansi(line))
          matched.append((line, action, actioncompiled, response))

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
        # varvals[actionvars[i]]=string.replace(regac.group(i+1),';','_')
        varvals[actionvars[i]] = match.group(i+1)

      # add special variables
      varvals['%a'] = line.replace(';','_')
            
      # fill in response variables from those that
      # matched on the trigger
      for var in varvals.keys():
        # replace occurrences of '%i' with val
        if var.find(response):
          response = re.sub(var, varvals[var], response)

      # replace occurrances of '$i' with val up to the ;
      if ("$" + var[1:]).find(response) != -1:
        response = re.sub("$" + var[1:],
                   varvals[var].replace(";", "\;"), 
                   response, 
                   1)

      event.InputEvent(response).enqueue()


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
    if self._actions.keys() == []:
      return ''

    list = []
    if text=='':
      list = self._actions.keys()
    else:
      list = utils.expand(text, self._actions.keys())

    data = ''
    for mem in list:
      data = (data + lyntin.commandchar + 
              "action {" + mem + "} {" + self._actions[mem][2] + "}\n")

    return data[:-1]
