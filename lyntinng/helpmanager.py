#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id$
#######################################################################
"""
The help manager holds a hierarchy of help files indexed by category.
It also houses a series of methods for adding new help text, parsing
help file text, and also exporting help content into some format
which then can be converted to a variety of other formats (probably
either AFT or reStructuredText).
"""
import string
import utils

class HelpManager:
  """ Manages the help text hierarchy.

  The HelpManager exists on the engine scoping--there is only one
  per Lyntin instance.  It holds a hierarchy of help texts which
  can be retrieved and perused through via the #help user command.
  """
  def __init__(self):
    self._help_tree = {}

  def addHelp(self, helpname, helptext, categorylist=[]):
    """
    Adds a help text to the hierarchy.

    arguments:
      
      'helpname' -- (string) the name of the help text

      'helptext' -- (string) the help data in raw text format

      'categorylist=[]' -- (list of strings) the category hierarchy
                           (in order!) of where this text resides.
                           If it's not specified, we'll try to
                           figure it out from the first line of the
                           text. 

    """
    # If we want to add other directives, we should build in a
    # "readDirectives" method which sets various variables.
    # The categorylist argumnet, however, should always override
    # the directive (if there is one).
    if not helpname or not helptext:
      return

    if not categorylist:
      lines = helptext.splitlines()
      if lines[0].find("category: ") == 0:
        categorylist = lines[0][lines[0].find(" ")+1:]
        categorylist = categorylist.split(".")
        helptext = string.join(lines[1:], "\n")

    place = self._help_tree
    for mem in categorylist:
      if place.has_key(mem):
        place = place[mem]
      else:
        place[mem] = {}
        place = place[mem]

    place[helpname] = helptext

  def removeHelp(self, fqn):
    """
    Takes in a fully-qualified name and attempts to remove it
    from the structure.

    arguments:

      'fqn' -- (string) a . delimited string of categories
               and finally a helpname
    """
    fqn = fqn.split(".")
    # FIXME - finish this
    
  def getHelp(self, fqn):
    """ Retrieves the help topic requested."""
    if not fqn:
      fqn = ""

    keys = fqn.split(".")
    if keys[0] == "root":
      keys = keys[1:]
    tree = self._help_tree
    breadcrumbs = "root"
    found = 1

    for mem in keys:
      if type(tree) == type({}):
        if tree.has_key(mem):
          tree = tree[mem]
          breadcrumbs += "." + mem
        else:
          found = 0
          break
      else:
        found = 0
        break

    if found == 0 and fqn != "":
      error = "Cannot find '%s'.  We did find this:" % fqn
    else:
      error = ""

    if type(tree) == type({}):
      list = tree.keys()
      list.sort()
      return (error, breadcrumbs, utils.columnize(textlist=list, indent=3))
    return (error, breadcrumbs, tree)
    
  def printTree(self, tree=None, tab=""):
    """ Prints out the hierarchy."""
    if tree == None:
      tree = self._help_tree
      print tab + "Root:"

    for mem in tree.keys():
      if type(tree[mem]) == type({}):
        print tab + "  " + mem + ":"
        self.printTree(tree[mem], tab + "  ")
      else:
        print tab + "  " + "node: " + mem
