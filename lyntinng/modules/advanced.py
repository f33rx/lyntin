#######################################################################
# This file is part of Lyntin
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: advanced.py,v 1.23 2002/10/26 04:32:40 willhelm Exp $
#######################################################################
"""
This module holds the magical python_cmd code.  It takes in code,
and attempts to execute it in the lyntinuser.py module.  If no such
module exists, it executes it in this module.
"""
import traceback, os, sys, string
import exported, engine, ui.ui, utils, lyntin

usermodule = None
onetime = 0

def _get_user_module():
  """
  Imports and returns the nicest user module it can find.
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
  #@ is different from all the rest because this one does some 
  incredibly magic stuff because it requires an environment to 
  execute the arbitrary python code in.  It allows you to execute
  arbitrary python code inside Lyntin.
  
  ex:
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
    exported.write_error("Error in raw python stuff.")
    exported.write_error(string.join(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1])))
    exported.tally_error()


def import_cmd(session, args, input):
  """
  Imports/reloads a module.  In the case of a Lyntin module, it also
  executes the load and unload functions where appropriate.
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
        except Exception, e:
          exported.write_error("import: module %s didn't unload properly. %s" % (mod, e))
          exported.write_error(string.join(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1])))

      reload(_module)

      if (_module.__dict__.has_key("load")):
        _module = sys.modules[mod]
        _module.load()
      _module.__dict__["lyntin_import"] = 1

      if mod not in lyntin.lyntinmodules:
        lyntin.lyntinmodules.append(mod)

      exported.write_message("import: module %s reloaded." % mod)
    except Exception, e:
      exported.write_error("import: had problems with %s. %s" % (mod, e))
      exported.write_error(string.join(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1])))
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

    except Exception, e:
      exported.write_error("import: had problems with %s. %s" % (mod, e))
      exported.write_error(string.join(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1])))



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
