#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2001
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id$
#######################################################################
"""
This module defines the ActionManager which handles managing actions 
(triggers) and expansion of actions.
"""
import re
import utils, event

# FIXME - should this be here?
VARREGEXP = re.compile('%(\d+)')

class ActionManager:
   """ Manages actions."""
   def __init__(self):
      self._actions = {}

   def _compileAction(self, trigger):
      """ Converts a trigger with pattern variables into a compiled
      regular expression and returns the regular expression."""
      regexp = re.sub('%[0-9]+', '(.*)', trigger)
      return re.compile(regexp)

   def addAction(self, trigger, response):
      """ Adds an alias to the dict."""
      compiled = self._compileAction(trigger)
      self._actions[trigger] = (trigger, compiled, response)
      return 1

   def clearActions(self):
      """ Removes all the actions."""
      for mem in self._actions.keys():
         del self._actions[mem]

   def removeActions(self, text):
      """ Removes actions from the list.

      Returns a list of tuples of action trigger/response that
      were removed.
      """
      badactions = utils.expand(text, self._actions.keys())

      ret = []
      for mem in badactions:
         ret.append((self._actions[mem][0], self._actions[mem][2]))
         del self._actions[mem]

      return ret

   def getActions(self):
      """ Returns the keys of the actions dict."""
      list = self._actions.keys()
      list.sort()
      return list

   def _getOrderedVars(self, instr):
      """
      Takes in a string and removes any ordered variables
      from it.  Returns a list of the variables.
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

         match = var_regex.search(str)

      return keylist


   def checkActions(self, muddata):
      """ Checks to see if muddata triggered any actions.

      Any resulting actions will get added as an InputEvent
      to the queue.
      FIXME - make sure this works even when lines are broken 
      up.
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


   def getActionInfo(self, text=''):
      """ Returns information about the actions in here.

      This is used by #action to tell all the actions involved
      as well as #write which takes this information and dumps
      it to the file.
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
         data = data + "#action {" + mem + "} {" + self._actions[mem][2] + "}\n"

      return data[:-1]
