#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: __init__.py,v 1.4 2002/05/14 22:46:26 willhelm Exp $
#######################################################################
import glob, os

def get_ui(uiname):
  """
  Attempts to retrieve the ui by that name.

  arguments:

    'uiname' -- (string) the name of the ui passed in by the
                command line

  returns:

    a ui.BaseUI subclass instance, or None if it could not
    be instantiated
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
