#######################################################################
# This file is part of Lyntin
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: __init__.py,v 1.2 2002/05/09 23:20:12 willhelm Exp $
#######################################################################

import glob, os, string
import exported

def load_help():
  """
  This loads all the help topics in this directory.
  """
  index = __file__.rfind(os.sep)
  if index == -1:
    path = "." + os.sep
  else:
    path = __file__[:index]

  ospathjoin = apply( os.path.join, (path, "*.tpc",))

  _help_list = glob.glob( ospathjoin )
  _help_list.sort()

  for mem in _help_list:
    try:
      file = open(mem, "r")
      memtext = string.join(file.readlines(), "")
      file.close()
    except Exception, e:
      exported.write_error("help: file %s cannot be read.\n%s" % (mem, e))
      continue

    memname = mem[mem.rfind(os.sep)+1:mem.rfind(".")]
    exported.add_help(memname, memtext)

# Local variables:
# mode:python
# py-indent-offset:2
# tab-width:2
# End:
