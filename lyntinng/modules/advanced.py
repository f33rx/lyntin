#######################################################################
# This file is part of Lyntin
# copyright (c) Will Guaraldi 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: advanced.py,v 1.5 2002/04/04 01:04:31 willhelm Exp $
#######################################################################
import traceback, os, sys, string
import exported, engine, ui.ui, utils

"""
This module holds the magical python_cmd code.  It takes in code,
and attempts to execute it in the user.py module.  If no such
module exists, it executes it in this module.
"""

usermodule = None

def python_cmd(session, words, input):
  """#@ arbitrary python code

  This function is different from all the rest because this one does
  some incredibly magic stuff because it requires an environment
  to execute the arbitrary python code in.
  """
  try:
    if usermodule == None:
      exported.write_error("modules.user is either bad or non-existent.  Executing in advanced.py..")
      exec input[1:]
    else:
      exec input[1:] in usermodule.__dict__
  except:
    exported.write_error("Error in raw python stuff.")
    exported.write_error(string.join(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1])))
    exported.tally_error()


def import_cmd(session, words, input):
  """#import <modulename>

  Imports/reloads a module.  In the case of a Lyntin module, it also
  executes the load and unload functions where appropriate.
  """
  import sys

  if len(words) == 0:
    exported.write_error("syntax: #import <modulename>")
    return

  mod = utils.strip_braces(words[1])

  if mod.find("modules.") == 0:
    if sys.modules.has_key(mod):
      _module = sys.modules[mod]
      try:
        _module.unload()
        reload(_module)
        _module = sys.modules[mod]
        _module.load()
        exported.write_message("import (reload) successful.")
      except Exception, e:
        exported.write_error("import: had problems with %s. %s" % (mod, e))
    else:
      try:
        name = mod[mod.find(".")+1:]
        _module = getattr(__import__( mod ), name)
        _module.load()
        exported.write_message("import successful.")
      except Exception, e:
        exported.write_error("import: had problems with %s. %s" % (mod, e))

  else:
    if sys.modules.has_key(mod):
      try:
        reload(sys.modules[mod])
        exported.write_message("import (reload) successful.")
      except Exception, e:
        exported.write_error("import: had problems with %s. %s" % (mod, e))
    else:
      try:
        _module = __import__( mod )
        exported.write_message("import successful.")
      except Exception, e:
        exported.write_error("import: had problems with %s. %s" % (mod, e))


def _import_user_module():
  """ Imports and returns the modules.user module."""
  try:
    import modules.user
    return modules.user
  except:
    return None


def load():
  """ Initializes the module by binding all the commands."""
  import modules.advanced
  modules.advanced.usermodule = _import_user_module()
  exported.add_command("@", python_cmd)
  exported.add_command("^import", import_cmd)

def unload():
  pass
