#######################################################################
# This file is part of Lyntin
# copyright (c) Will Guaraldi 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: __init__.py,v 1.3 2002/02/23 21:10:32 willhelm Exp $
#######################################################################

import glob, os, sys, traceback
import exported, modules.__init__

def load_modules():
  """
  Magically dynamically loads all the modules in the modules
  package.  This is truly a semi-magic function.
  """
  index = modules.__init__.__file__.rfind(os.sep)
  if index == -1:
    path = "." + os.sep
  else:
    path = modules.__init__.__file__[:index]

  ospathjoin = apply( os.path.join, (path, "*py",))

  _module_list = glob.glob( ospathjoin )
  _module_list.sort()

  for mem in _module_list:
    # we skip over all files that start with a _
    # this allows hackers to be working on a module and not have
    # it die every time.
    mem = mem[mem.rfind(os.sep)+1:mem.rfind(".")]
    if mem[0] != "_":
      try:
        name = "modules." + mem
        exported.write_message("Loading '" + name + "'")
        _module = getattr(__import__( name ), mem)
        _module.load()
      except:
        exported.write_error("Module '" + name + "' refuses to load.")
        traceback.print_exc()

