#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: __init__.py,v 1.5 2002/07/21 04:14:48 willhelm Exp $
#######################################################################
import glob, os

def get_ui(uiname):
  """
  Attempts to retrieve the ui by that name.

  @param uiname: the name of the ui passed in by the command line
  @type  uiname: string

  @return: a BaseUI subclass instance corresponding to the name
      of the ui the user wants to instantiate.  or None if the ui
      could not be found or instantiated.
  @rtype: BaseUI subclass
  """
  index = __file__.rfind(os.sep)
  if index == -1:
    path = "." + os.sep
  else:
    path = __file__[:index]

  if not glob.glob(os.path.join(path, uiname + ".py")):
    return None

  try:
    ui_module = getattr(__import__("ui.%s" % uiname), uiname)
    return ui_module.get_ui_instance()

  except Exception, e:
    print "get_ui: %s" % e
    return None

# Local variables:
# mode:python
# py-indent-offset:2
# tab-width:2
# End:
