#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: gag.py,v 1.16 2002/05/28 03:42:40 willhelm Exp $
#######################################################################
"""
This module defines the GagManager which handles gags in Lyntin.
"""
import re, string, copy
import manager, utils, lyntin, hooks, exported, modutils

class GagData:
  def __init__(self):
    self._gags = []
    self._gagregexp = None

  def addGag(self, gag):
    """ Adds a gag to the list.

    arguments:

      'gag' -- (string) the gag pattern to add

    """
    if gag not in self._gags:
      self._gags.append(gag)
      self.compileGagRegexp()
    return 1

  def compileGagRegexp(self):
    """ Creates a regexp object of the list of gags."""
    if len(self._gags) > 0:
      gags = []
      # we have to handle special character which could
      # make the regular expression unhappy--so we do
      # this double loop thing--which should be pretty
      # quick....
      for mem in self._gags:
        for c in mem:
          if c in string.punctuation:
            mem.replace(c, "\\" + c)
        gags.append(mem)
         
      # join all the gags into a string separated by |
      # so it's a this or this or this or this...  regexp.
      str = "(" + string.join(gags, '|') + ")"
      self._gagregexp = re.compile(str)
    else:
      self._gagregexp = None

  def clear(self):
    """ Removes all the gags."""
    self._gags = []
    self.compileGagRegexp()
         
  def removeGags(self, text):
    """ Removes a specific gag from the list.

    Returns a list of the gags that were removed.
    """
    badgags = utils.expand(text, self._gags)

    for mem in badgags: 
      self._gags.remove(mem)

    self.compileGagRegexp()

    return badgags
    
  def getGags(self):
    """ Returns the list of gags."""
    self._gags.sort()
    return self._gags

  def removeGaggedText(self, text):
    """ Takes text in if it's to be gagged, returns an empty string

    arguments:
      
      'text' -- (string) input string

    """
    if text and self._gagregexp:
      if self._gagregexp.search(utils.filter_ansi(text)):
        text = ''

    return text

  def getStatus(self):
    """ Returns a one-liner describing the status of this dataclass.

    returns:

      (string) the one-liner status
    """
    return "%d gag(s)." % len(self._gags)

  def getInfo(self):
    """ Returns information about the gags in here.

    This is used by #gag to tell all the gags involved
    as well as #write which takes this information and dumps
    it to the file.
    """
    if len(self._gags) == 0:
      return ''

    data = []
    self._gags.sort()
    for mem in self._gags:
      data.append("%sgag {%s}" % (lyntin.commandchar, mem))

    return string.join(data, "\n")

  def getCount(self):
    """ Returns the number of gags we're managing."""
    return len(self._gags)


class GagManager(manager.Manager):
  def __init__(self):
    self._gags = {}

  def addGag(self, ses, gag):
    if not self._gags.has_key(ses):
      self._gags[ses] = GagData()

    self._gags[ses].addGag(gag)

  def clear(self, ses):
    if self._gags.has_key(ses):
      self._gags[ses].clear()

  def removeGags(self, ses, text):
    if self._gags.has_key(ses):
      return self._gags[ses].removeGags(text)
    return []

  def getGags(self, ses):
    if self._gags.has_key(ses):
      return self._gags[ses].getGags()
    return []

  def getInfo(self, ses):
    if self._gags.has_key(ses):
      return self._gags[ses].getInfo()
    return ""

  def addSession(self, newsession, basesession=None):
    """ over-ridden from manager.Manager."""
    if basesession:
      if self._gags.has_key(basesession):
        gdata = self._gags[basesession]
        for mem in gdata._gags:
          self.addGag(newsession, mem)

  def removeSession(self, ses):
    """ over-ridden from manager.Manager."""
    if ses and self._gags.has_key(ses):
      del self._gags[ses]

  def getStatus(self, ses):
    if self._gags.has_key(ses):
      return self._gags[ses].getStatus()
    return "0 gag(s)."

  def persist(self, args):
    """
    write_hook function for persisting the state of our session.
    """
    ses = args[0]
    file = args[1]
    data = self.getInfo(ses)
    if data:
      file.write(data + "\n")

  def filter(self, args):
    """
    Mud_filger_hook function to remove gagged text that
    comes from the mud.
    """
    ses = args[0]
    text = args[-1]
    if self._gags.has_key(ses):
      return self._gags[ses].removeGaggedText(text)
    return text


commands_dict = {}

def gag_cmd(ses, args, input):
  """
  With no arguments, prints out all gags.
  With arguments, creates a gag.

  Incoming lines from the mud which contain gagged text will
  be removed and not shown on the ui.

  Gags get converted to regular expressions.  Feel free to use
  regular expression matching syntax as you see fit.

  As with all commands, braces get stripped off and each complete
  argument creates a gag.  gag accepts multiple gags at once, and
  accepts a quiet argument to supress reporting of what has been
  gagged.  

  ex:
     #gag {has missed you.}    <-- will prevent any incoming line
                                   with "has missed you" to be shown.
  ex:
     #gag has missed you       <-- will gag any text with "has",
                                   "missed", or "you"

  category: commands
  """
  gaggedtext = args["text"]
  quiet = args["quiet"]

  gm = exported.get_manager("gag")

  if not gaggedtext:
    data = gm.getInfo(ses)
    if data == '':
      data = "gag: no gags defined."

    exported.write_message(data)
    return

  for togag in gaggedtext:
    gm.addGag(ses, togag)
    if not quiet:
      exported.write_message("gag: {%s} added." % togag)

commands_dict["gag"] = (gag_cmd, "text* quiet:boolean=false")


def ungag_cmd(ses, args, input):
  """
  Allows you to remove gags.

  category: commands
  """
  gm = exported.get_manager("gag")

  func = gm.removeGags
  modutils.unsomething_helper(args, func, ses, "gag", "gags")

commands_dict["ungag"] = (ungag_cmd, "str= quiet:boolean=false")


gm = None

def load():
  """ Initializes the module by binding all the commands."""
  global gm
  modutils.load_commands(commands_dict)
  gm = GagManager()
  exported.add_manager("gag", gm)

  # FIXME - the number controls the order this gets called in the grand
  # scheme of things.  we should probably do something to make this
  # more obvious.
  hooks.mud_filter_hook.register(gm.filter, 20)
  hooks.write_hook.register(gm.persist)

def unload():
  """ Unloads the module by calling any unload/unbind functions."""
  global gm
  modutils.unload_commands(commands_dict.keys())
  exported.remove_manager("gag")
  hooks.mud_filter_hook.unregister(gm.filter)
  hooks.write_hook.unregister(gm.persist)
