#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: variable.py,v 1.3 2002/06/21 02:27:17 willhelm Exp $
#######################################################################
"""
This module defines the VariableManager which handles variables.
It also defines global variables like $TIMESTAMP.
"""
import re, string, time
import manager, utils, lyntin, engine, hooks, exported, modutils

"""
This hook will get called every time a variable is changed.  arg tuple
is (session, varname, varoldvalue, varnewvalue).
"""
variable_change_hook = hooks.Hook()

class TimeStampBuiltin:
  """
  Allows us to do dynamic TIMESTAMPs as a global variable.
  """
  def __init__(self): pass
  def __str__(self): return time.asctime()


class VariableData:
  def __init__(self):
    self._variables = {}

  def addVariable(self, var, expansion):
    """ Adds a variable to the dict.

    arguments:

      'var' -- the variable name

      'expansion' -- the variable value
    """
    self._variables[var] = expansion

  def clear(self):
    """ Removes all the variables."""
    list = self._variables.keys()
    for mem in list:
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
    badvariables = utils.expand_text(text, self._variables.keys())

    ret = []
    for mem in badvariables:
      ret.append((mem, self._variables[mem]))
      del self._variables[mem]

    return ret

  def expand(self, text):
    """ Expands variables in the text.

    arguments:

      'text' -- (string) the text to expand variables in

    returns:

      the text with variables expanded
    """
    text = utils.expand_vars(text, self._variables)
    return text

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

  def getStatus(self):
    """ Returns a one-liner as to the status of this data class.

    returns:

      (string) the one-line status
    """
    return "%d variable(s)." % len(self._variables)

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
      list = utils.expand_text(text, self._variables.keys())

    data = []
    for mem in list:
      data.append("%svariable {%s} {%s}" % (lyntin.commandchar, mem, self._variables[mem]))

    return string.join(data, "\n")


class VariableManager(manager.Manager):
  def __init__(self):
    self._variables = {}

    # this handles builtins even when we don't have a VariableData
    # instance for that session
    self._global = VariableData()

    # add built-in variables
    self._global.addVariable("TIMESTAMP", TimeStampBuiltin())
    self._global.addVariable("DATADIR", lyntin.options["datadir"])

    import os
    if os.environ.has_key("HOME"):
      self._global.addVariable("HOME", os.environ["HOME"])


  def addVariable(self, ses, var, expansion):
    if not self._variables.has_key(ses):
      self._variables[ses] = VariableData()

    # check to see if it's a global variable
    if var[0] == "_":
      vdata = self._global
    else:
      vdata = self._variables[ses]

    # save the old value (if any)
    oldvalue = vdata.getVariable(var)

    # set the variable
    vdata.addVariable(var, expansion)

    # spam the hook
    variable_change_hook.spamhook((ses, var, oldvalue, expansion))

  def clear(self, ses):
    if self._variables.has_key(ses):
      self._variables[ses].clear()

  def removeVariables(self, ses, text):
    vars = []
    if self._variables.has_key(ses):
      vars = self._variables[ses].removeVariables(text)
      for mem in vars:
        variable_change_hook.spamhook((ses, mem[0], mem[1], None))
    return vars

  def getVariables(self, ses):
    if self._variables.has_key(ses):
      return self._variables[ses].getVariables()
    return []

  def getVariable(self, ses, name, default=None):
    if self._variables.has_key(ses):
      return self._variables[ses].getVariable(name, default)
    return default

  def expand(self, ses, text):
    text = self._global.expand(text)
    if self._variables.has_key(ses):
      return self._variables[ses].expand(text)
    return text

  def getInfo(self, ses, text=""):
    if self._variables.has_key(ses):
      return self._variables[ses].getInfo(text)
    return ""

  def getStatus(self, ses):
    if self._variables.has_key(ses):
      return self._variables[ses].getStatus()
    return "0 variable(s)."

  def addSession(self, newsession, basesession=None):
    """ over-ridden from manager.Manager."""
    if basesession:
      if self._variables.has_key(basesession):
        varhash = self._variables[basesession]._variables
        for mem in varhash.keys():
          self.addVariable(newsession, mem, varhash[mem])

  def removeSession(self, ses):
    """ over-ridden from manager.Manager."""
    if self._variables.has_key(ses):
      del self._variables[ses]

  def persist(self, args):
    """
    write_hook function for persisting the state of our session.
    """
    ses = args[0]
    file = args[1]
    data = self.getInfo(ses)
    if data:
      file.write(data + "\n")

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
    ses = args[0]
    internal = args[1]
    text = args[-1]

    varexpansion = self.expand(ses, text)
    if varexpansion == text:
      return text
    else:
      engine.myengine.handleUserData(varexpansion, 1, ses)
      return None


commands_dict = {}

def variable_cmd(ses, args, input):
  """
  Creates a variable for that session of said name with said value.
  Variables can then pretty much be used anywhere.

  ex:
     #variable {hps} {100}
     #action {HP: %0/%1 } {#variable {hps} {%0}}

  Variables can later be accessed via the variable character
  (which defaults to $) and the variable name.  In the case of the
  above, the variable name would be $hps.

  There are also system variables ($HOME, $TIMESTAMP, $DATADIR) and
  global variables.  To set a global variable, it must be preceded
  by a _.

  ex:
    #variable {_fun} {happy fun ball}

  Global variables can be accessed by any session.

  category: commands
  """
  var = args["var"]
  expansion = args["expansion"]
  quiet = args["quiet"]

  vm = exported.get_manager("variable")

  if not var and not expansion:
    data = vm.getInfo(ses)
    if data == '':
      data = "variable: no variables defined."

    exported.write_message("variables:\n" + data)
    return

  if not expansion:
    data = vm.getInfo(ses, var)
    if data == '':
      data = "variable: no variables defined."

    exported.write_message("variables:\n" + data)
    return 

  # need to expand the var
  varexpansion = vm.expand(ses, var)
  if varexpansion:
    var = varexpansion

  try:
    vm.addVariable(ses, var, expansion)
    if not quiet:
      exported.write_message("variable: {%s}={%s} added." % (var, expansion))

  except Exception, e:
    exported.write_error("variable: cannot be set. %s", e)

commands_dict["variable"] = (variable_cmd, "var= expansion= quiet:boolean=false")


def unvariable_cmd(ses, args, input):
  """
  Allows you to remove variables.

  category: commands
  """
  func = exported.get_manager("variable").removeVariables
  modutils.unsomething_helper(args, func, ses, "variable", "variables")

commands_dict["unvariable"] = (unvariable_cmd, "str= quiet:boolean=false")

vm = None

def load():
  """ Initializes the module by binding all the commands."""
  global vm
  modutils.load_commands(commands_dict)
  vm = VariableManager()
  exported.add_manager("variable", vm)

  # FIXME - the number controls the order this gets called in the grand
  # scheme of things.  we should probably do something to make this
  # more obvious.
  hooks.user_filter_hook.register(vm.filter, 0)
  # hooks.user_filter_hook.register(unescape_variables, 90)
  hooks.write_hook.register(vm.persist)

def unload():
  """ Unloads the module by calling any unload/unbind functions."""
  global vm
  modutils.unload_commands(commands_dict.keys())
  exported.remove_manager("variable")
  hooks.user_filter_hook.unregister(vm.filter)
  # hooks.user_filter_hook.unregister(unescape_variables)
  hooks.write_hook.unregister(vm.persist)

