#######################################################################
# This file is part of Lyntin
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: __init__.py,v 1.10 2002/05/14 22:46:26 willhelm Exp $
#######################################################################

import glob, os, sys, traceback
import exported

def load_modules():
  """
  Magically dynamically loads all the modules in the modules
  package.  This is truly a semi-magic function.
  """
  index = __file__.rfind(os.sep)
  if index == -1:
    path = "." + os.sep
  else:
    path = __file__[:index]

  _module_list = glob.glob( os.path.join(path, "*.py"))
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
        if _module.__dict__.has_key("load"):
          _module.load()

        _module.__dict__["lyntin_import"] = 1
      except:
        exported.write_error("Module '" + name + "' refuses to load.")
        traceback.print_exc()

# Local variables:
# mode:python
# py-indent-offset:2
# tab-width:2
# End:
