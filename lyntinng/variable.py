#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: variable.py,v 1.4 2002/02/03 04:27:50 willhelm Exp $
#######################################################################
"""
This module defines the VariableManager which handles variables.
"""
import re
import utils, lyntin

localvarchar = lyntin.variablechar
VARIABLE_REGEXP = re.compile("\\" + lyntin.variablechar)

def _fixvariableregexp():
  VARIABLE_REGEXP = re.compile("\\" + lyntin.variablechar)

class VariableManager:
  """ Manages variables."""

  def __init__(self):
    self._variables = {}

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
    for mem in self._variables.keys():
      del self._variables[mem]

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

  def expand(self, text):
    """ Looks at user input and expands any variables involved.

    It'll return the expansion if there is one.  Otherwise
    it returns None.
    """
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

          count = (text[marker:b].count('{') -
                   text[marker:b].count('}'))

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

  def unescapeVariables(self, text):
    """ Changes \$ into $.

    Accounts for the fact that the user can change the variable
    character.

    aguments:

      'text' -- (string) string to unescape variable characters

    returns:

      the unescaped string

    """
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
    if self._variables.keys() == []:
      return ''

    if text=='':
      list = self._variables.keys()
    else:
      list = utils.expand(text, self._variables.keys())

    data = ''
    for mem in list:
      data = (data + lyntin.commandchar + 
              "variable {" + mem + "} {" + self._variables[mem] + "}\n")

    return data[:-1]
