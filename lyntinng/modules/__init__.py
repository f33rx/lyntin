#######################################################################
# This file is part of Lyntin
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: __init__.py,v 1.11 2002/07/21 04:14:48 willhelm Exp $
#######################################################################

import glob, os, sys, traceback
import exported
"""
The modules package holds all of the dynamically loaded Lyntin modules.
Modules get loaded when Lyntin starts up unless:

1. the module throws an exception when getting imported
2. the module's name starts with an _
"""

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
        exported.write_message("Loading '%s'..." % name)
        _module = getattr(__import__( name ), mem)
        if _module.__dict__.has_key("load"):
          _module.load()

        _module.__dict__["lyntin_import"] = 1
      except:
        exported.write_error("Module '%s' refuses to load." % name)
        traceback.print_exc()

# Local variables:
# mode:python
# py-indent-offset:2
# tab-width:2
# End:
