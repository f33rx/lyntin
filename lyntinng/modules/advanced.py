#######################################################################
# This file is part of Lyntin
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: advanced.py,v 1.27 2002/11/06 01:56:51 willhelm Exp $
#######################################################################
"""
This module holds the magical python_cmd code.  It takes in code,
and attempts to execute it in the lyntinuser.py module.  If no such
module exists, it executes it in this module.

It also holds import_cmd which does a lot of other magic stuff.
"""
import os, sys, string
import exported, engine, ui.ui, utils, lyntin

usermodule = None
onetime = 0

def _get_user_module():
  """
  Imports and returns the nicest user module it can find.  If we've
  already imported a usermodule, then we use the cached one we
  imported before so we're not doing this over and over again.

  @returns: the user module we just imported or None
  @rtype: module
  """
  global usermodule
  if usermodule:
    return usermodule

  # this probably isn't exactly right since it'll look for the
  # first "lyntinuser" it finds and use that one.  i'm not sure how
  # we could implement a priority.
  for mem in sys.modules.keys():
    modname = "lyntinuser"
    if mem == modname or (len(mem) > len(modname) and mem[-1 * (len(modname) + 1):] == "." + modname):
      usermodule = sys.modules[mem]
      return usermodule

  return None


def python_cmd(session, words, input):
  """
  #@ allows you to execute arbitrary Python code inside of Lyntin.
  It will first look for a module named "lyntinuser" and execute
  the code inside that module's __dict__ environment.  If no
  such module exists, it will execute the code inside 
  modules.advanced .

  examples:
    #@ print "hello"
    #@ print string.join(exported.get_commands(), "\\n")

  category: commands
  """
  global onetime
  # NOTE: if we ever get to handling multiple-lines, we'll need
  # to change this function completely.
  try:
    my_usermodule = _get_user_module() 
    if my_usermodule == None:
      if onetime == 0:
        exported.write_error("No lyntinuser module imported--executing in advanced.py.")
        onetime = 1
      exec input[1:].lstrip()
    else:
      exec input[1:].lstrip() in usermodule.__dict__
  except:
    exported.write_traceback("@: error in raw python stuff.")
    exported.tally_error()


def import_cmd(session, args, input):
  """
  Imports/reloads a module.

  When reloading, it looks for an "unload" function and executes it
  prior to reloading the module.

  After reloading/importing, it looks for a "load" function and
  executes it.

  Lyntin modules located in the modules package are safe to reload 
  in-game.  Lyntin core modules (engine, helpmanager, event...) are
  NOT safe to import in-game.

  examples:
    #import modules.action
    #import exportuser

  #import will look for the module on the sys.path.  So if your module
  is not on the sys.path, you should first add the directory using #@:

    #@ import sys
    #@ sys.path.append("/directory/where/my/module/exists")

  Directories specified by the moduledir command-line argument are
  added to the sys.path upon Lyntin startup.

  category: commands
  """
  import sys

  mod = args["modulename"]

  if sys.modules.has_key(mod):
    # if this module has previously been loaded, we try to reload it.

    _module = sys.modules[mod]
    try:
      if ((_module.__dict__.has_key("unload") and 
          _module.__dict__.has_key("lyntin_import"))):
        try:
          _module.unload()
        except:
          exported.write_traceback("import: module %s didn't unload properly." % mod)

      reload(_module)

      if (_module.__dict__.has_key("load")):
        _module = sys.modules[mod]
        _module.load()
      _module.__dict__["lyntin_import"] = 1

      if mod not in lyntin.lyntinmodules:
        lyntin.lyntinmodules.append(mod)

      exported.write_message("import: module %s reloaded." % mod)
    except:
      exported.write_traceback("import: had problems with %s." % mod)
      return

  else:
    try:
      _module = __import__( mod )

      _module = sys.modules[mod]
      if (_module.__dict__.has_key("load")):
        _module.load()

      _module.__dict__["lyntin_import"] = 1
      exported.write_message("import successful.")
      if mod not in lyntin.lyntinmodules:
        lyntin.lyntinmodules.append(mod)

    except:
      exported.write_traceback("import: had problems with %s." % mod)


def load():
  """ Initializes the module by binding all the commands."""
  exported.add_command("@", python_cmd)
  exported.add_command("^import", import_cmd, "modulename")

def unload():
  pass

# Local variables:
# mode:python
# py-indent-offset:2
# tab-width:2
# End:
