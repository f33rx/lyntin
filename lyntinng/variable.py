#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: variable.py,v 1.14 2002/05/05 16:34:51 willhelm Exp $
#######################################################################
"""
This module defines the VariableManager which handles variables.
It also defines some builtin variables like $TIMESTAMP.
"""
import re
import manager, utils, lyntin, engine

localvarchar = lyntin.variablechar
VARIABLE_REGEXP = re.compile("\\" + lyntin.variablechar)

def _fixvariableregexp():
  VARIABLE_REGEXP = re.compile("\\" + lyntin.variablechar)

class VariableManager(manager.Manager):
  """ Manages variables."""
  def __init__(self):
    self._variables = {}
    self._setBuiltinVars()

  def addVariable(self, var, expansion):
    """ Adds a variable to the dict.

    arguments:

      'var' -- the variable name

      'expansion' -- the variable value

    returns:

      (int) we always return 1.  we might at some point return 
      0 if we don't like the the value or something like that.
    """
    self._variables[var] = expansion
    return 1

  def clear(self):
    """ Removes all the variables."""
    self._variables.clear()

  def removeVariables(self, text):
    """ Removes variables from the list.

    Returns a list of tuples of variable var/expansion that
    were removed.

    arguments:

      'text' -- variables will be removed that match the text

    returns:

      list of (name, value) tuples of removed variables

    """
    badvariables = utils.expand(text, self._variables.keys())

    ret = []
    for mem in badvariables:
      ret.append((mem, self._variables[mem]))
      del self._variables[mem]

    return ret

  def getVariables(self):
    """ Returns the keys of the variables dict.

    returns:

      list of strings of variable names

    """
    list = self._variables.keys()
    list.sort()
    return list

  def getVariable(self, name, default=None):
    """ Returns the value for a given variable.

    arguments:

      'name' -- (string) the name of the variable.

      'default=None' -- the default value to return if
                        the variable doesn't exist

    returns:

      the variable value or the default
    """
    if self._variables.has_key(name):
      return self._variables[name]
    else:
      return default

  def _setBuiltinVars(self):
    """ Adds a series of built-in variables."""
    import time
    self.addVariable("TIMESTAMP", time.asctime(time.localtime()))

  def expand(self, text):
    """ Looks at user input and expands any variables involved.

    It'll return the expansion if there is one.  Otherwise
    it returns None.
    """
    self._setBuiltinVars()
    replacedvars = 0
    if len(text) > 0:
      marker = 0

      if localvarchar != lyntin.variablechar:
        _fixvariableregexp()

      matchob = VARIABLE_REGEXP.search(text)
      if matchob:
        while (matchob):
          (b, e) = matchob.span()
          if text[b-1] == "\\":
            matchob = VARIABLE_REGEXP.search(text, e)
            continue

          count = text[marker:b].count('{') - text[marker:b].count('}')

          if count == 0:
            for mem in self._variables.keys():
              if text[b:].find(lyntin.variablechar + mem) == 0:
                repl = self._variables[mem]
                replacedvars = 1
                text = text[:b] + repl + text[b+len(mem)+1:]
                break
            marker = e

          matchob = VARIABLE_REGEXP.search(text, e)

    if replacedvars == 0:
      return None
    else:
      return text

  def unescapeVariables(self, input):
    """ Changes \$ into $.

    Accounts for the fact that the user can change the variable
    character.

    aguments:

      'input' == (tuple) mud_filter_hook hook tuple.

    returns:

      the unescaped string

    """
    text = input[-1]
    return text.replace("\\" + lyntin.variablechar, 
                        lyntin.variablechar)

  def getInfo(self, text=""):
    """ Returns information about the variables in here.

    This is used by #variable to tell all the variables involved
    as well as #write which takes this information and dumps
    it to the file.

    arguments:

      'text=""' -- (string) variables matching this string will be 
                   returned

    returns:

      (string) one big string with all the information in it

    """
    if len(self._variables.keys()) == 0:
      return ''

    if text=='':
      list = self._variables.keys()
    else:
      list = utils.expand(text, self._variables.keys())

    data = []
    for mem in list:
      if mem != "TIMESTAMP":
        data.append("%svariable {%s} {%s}" % 
                    (lyntin.commandchar, mem, self._variables[mem]))

    return string.join(data, "\n")

  def getCount(self):
    """ Returns a count of all the variables."""
    return len(self._variables.keys()) - 1

  def filter(self, args):
    """ Handle the filtering of input through the current variables.
        If input gets changed then we pass it back to
        engine.myengine.HandleUserData and return None to stop this
        chain of filtering.

    arguments:

      'args' -- user_filter_hook arg tuple (session, internal, input,
                filtered)

    returns:

      filtered text or None if any changes took place.
    """
    session = args[0]
    internal = args[1]
    text = args[-1]
    varexpansion = self.expand(text)
    if varexpansion:
      engine.myengine.handleUserData(varexpansion, internal, session)
      return None
    else:
      return text
