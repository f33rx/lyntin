#######################################################################
# This file is part of Lyntin
# copyright (c) Will Guaraldi 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id$
#######################################################################
import traceback, sys, string
import exported, engine

"""
This module holds the magical python_cmd code.  It takes in code,
and attempts to execute it in the user.py module.  If no such
module exists, it executes it in this module.
"""

def python_cmd(session, words, input):
  """#@ arbitrary python code

  This function is different from all the rest because this one does
  some incredibly magic stuff because it requires an environment
  to execute the arbitrary python code in.
  """
  usermoduleexists = 1
  try:
    import modules.user
  except:
    exported.write_error("No 'user.py' in the modules directory.  Executing locally.")
    usermoduleexists = 0

  try:
    if usermoduleexists == 1:
      exec input[1:] in modules.user.__dict__
    else:
      exec input[1:]
  except:
    exported.write_error("Error in raw python stuff.")
    exported.write_error(string.join(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1])))


def load():
  """ Initializes the module by binding all the commands."""
  engine.myengine.addCommand("@", python_cmd)
