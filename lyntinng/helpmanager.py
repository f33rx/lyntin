#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: helpmanager.py,v 1.3 2002/05/09 23:20:12 willhelm Exp $
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

  def addHelp(self, fqn, helptext):
    """
    Adds a help text to the hierarchy.

    arguments:
      
      'fqn' -- (string) a . delimited string of categories
               and finally a helpname

      'helptext' -- (string) the help data in raw text format

    """

    categorylist, helpname = self.splitName(fqn)

    if not helptext or not helpname:
      raise ValueError, "Help name and text are required."

    # If we want to add other directives, we should build in a
    # "readDirectives" method which sets various variables.
    # The categorylist argumnet, however, should always override
    # the directive (if there is one).
    if not categorylist:
      lines = helptext.strip().splitlines()
      if lines[-1].find("category: ") == 0:
        categorylist = lines[-1][lines[-1].find(" ")+1:]
        categorylist = categorylist.split(".")
        helptext = string.join(lines[:-1], "\n")

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
    category, name = self.splitName(fqn)

    place = self._help_tree
    for mem in fqn:
      if place.has_key(mem):
        place = place[mem]
      else:
        raise ValueError, "That topic does not exist."

    if place.has_key(name):
      del place[name]
    else:
      raise ValueError, "That topic does not exist."


  def getHelp(self, fqn):
    """ Retrieves the help topic requested.

    arguments:

      'fqn' -- (string) a . delimited string of categories
               and finally a helpname

    returns:

      A tuple composed of three strings.  The first string is
      error text (if any or empty string if none).  The second
      string is the breadcrumbs trail.  The third string is the
      help text found or a columnized text of what tree elements
      exist at that level.
    """
    
    categorylist, name = self.splitName(fqn)

    categorylist.append(name)

    tree = self._help_tree
    breadcrumbs = "root"
    found = 1

    for mem in categorylist:
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
      # first find all instances of categorylist[0] in the help tree.
      potentialroots = []
      start = categorylist[0]

      tosearch = [ ("root",self._help_tree) ]
      while tosearch:
        nextbreadcrumbs, nextnode = tosearch[0]
        tosearch = tosearch[1:]
        for key in nextnode.keys():
          currentbreadcrumbs = nextbreadcrumbs + "." + key
          if key == categorylist[0]:
            potentialroots.append( (currentbreadcrumbs,nextnode[key]) )
          if type(nextnode[key]) == type({}):
            tosearch.append( (currentbreadcrumbs,nextnode[key]) )

      foundnodes = []

      # Now walk through all of the nodes named categorylist[0] and see if
      # they have they have categorylist[1:] under them.
      for bc,node in potentialroots:
        for key in categorylist[1:]:
          if type(node) != type({}) or not node.has_key(key):
            bc=None
            node=None
          else:
            bc = bc+"."+key
            node = node[key]
        if node:
          foundnodes.append( (bc,node) )


      # If we only found one thing then run the rest of the function
      # as though that was what was entered.  Otherwise build the
      # The error text to state the nodes that were found.
      if len(foundnodes) == 1:
        breadcrumbs,tree = foundnodes[0]
        error = ""
      elif len(foundnodes) == 0:
        error = "Cannot find '%s'.  We did find this:" % fqn
      else:
        error = "Could not find exact match for '%s'.  We did find these matches:" % fqn
        list = map(lambda x:x[0],foundnodes)
        return (error, "", utils.columnize(textlist=list,indent=3))
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

  def splitName(self, fqn):
    """ Splits an fqn into a category list and a help text name.

      'fqn' -- (string) a . delimited string of categories
               and finally a helpname
    """
    if not fqn:
      fqn = ""

    keys = fqn.split(".")
    if len(keys) > 1 and keys[0] == "root":
      keys = keys[1:]

    if len(keys) > 0:
      return (keys[:-1], keys[-1])
    else:
      return ([], "")
