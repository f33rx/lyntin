#######################################################################
# This file is part of Lyntin
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: __init__.py,v 1.13 2002/10/16 23:59:07 willhelm Exp $
#######################################################################
"""
The modules package holds all of the dynamically loaded Lyntin modules.
Modules get loaded when Lyntin starts up unless:

1. the module throws an exception when getting imported
2. the module's name starts with an _
"""

import glob, os, sys, traceback
import exported, lyntin

def load_modules():
  """
  Magically dynamically loads all the modules in the modules
  package.  This is truly a semi-magic function.
  """
  # handle modules found in the moduledir
  moduledirlist = lyntin.options["moduledir"]
  if moduledirlist:
    for moduledir in moduledirlist:
      # grab the contents of the moduledir directory
      _module_list = glob.glob( os.path.join( moduledir, "*.py"))

      # toss the moduledir in the sys.path
      sys.path.insert(0, moduledir)

      # and toss all the contents of the directory in our _module_list
      for mem in _module_list:
        mem2 = mem[mem.rfind(os.sep)+1:mem.rfind(".")]
        if mem2[0] == "_":
          continue

        try:
          exported.write_message("Loading '%s'..." % mem2)
          _module = __import__(mem2)

          if _module.__dict__.has_key("load"):
            _module.load()

          _module.__dict__["lyntin_import"] = 1
          lyntin.lyntinmodules.append(mem)
          exported.write_message("Loaded: '%s'" % mem)
        except:
          exported.write_error("Module '%s' refuses to load." % name)
          # FIXME - need to print this to the ui
          traceback.print_exc()


  # handle modules.*
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
    mem2 = mem[mem.rfind(os.sep)+1:mem.rfind(".")]
    if mem2[0] == "_":
      continue

    try:
      name = "modules." + mem2
      exported.write_message("Loading '%s'..." % name)
      _module = getattr(__import__( name ), mem2)

      if _module.__dict__.has_key("load"):
        _module.load()

      _module.__dict__["lyntin_import"] = 1
      lyntin.lyntinmodules.append(mem)
      exported.write_message("Loaded: '%s'" % mem)
    except:
      exported.write_error("Module '%s' refuses to load." % name)
      # FIXME - need to print this to the ui
      traceback.print_exc()

# Local variables:
# mode:python
# py-indent-offset:2
# tab-width:2
# End:
