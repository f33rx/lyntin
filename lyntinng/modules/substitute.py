#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: substitute.py,v 1.4 2002/07/07 04:53:45 willhelm Exp $
#######################################################################
"""
This module defines the SubstituteManager which handles substitutes.
"""
import string
import manager, utils, lyntin, hooks, exported, modutils

class SubstituteData:
  def __init__(self):
    self._substitutes = {}

  def addSubstitute(self, item, substitute):
    """ Adds a substitute to the dict."""
    self._substitutes[item] = substitute 

  def clear(self):
    """ Removes all the substitutes."""
    self._substitutes.clear()

  def removeSubstitutes(self, text):
    """ Removes substitutes from the list.

    Returns a list of tuples of substitute item/substitute that
    were removed.
    """
    badsubstitutes = utils.expand_text(text, self._substitutes.keys())

    ret = []
    for mem in badsubstitutes:
      ret.append((mem, self._substitutes[mem]))
      del self._substitutes[mem]

    return ret

  def getSubstitutes(self):
    """ Returns the keys of the substitute dict."""
    list = self._substitutes.keys()
    list.sort()
    return list

  def expand(self, text):
    """ Looks at mud data and performs any substitutes.

    It returns the final text--even if there were no substitutes.
    # FIXME -- this isn't done correctly.
    """
    if len(text) > 0:
      for mem in self._substitutes.keys():
        # note: this . thing is done on purpose because that's a tintin
        # feature
        if self._substitutes[mem] == ".":
          if text.find(mem) > -1:
            text = ''
        else:
          if self._substitutes[mem] == r"\.":
            text = text.replace(mem, ".")
          else:
            text = text.replace(mem, self._substitutes[mem])

    return text 

  def getInfo(self, text=''):
    """ Returns information about the substitutes in here.

    This is used by #substitute to tell all the substitutes involved
    as well as #write which takes this information and dumps
    it to the file.
    """
    if len(self._substitutes.keys()) == 0:
      return ''

    if text=='':
      list = self._substitutes.keys()
    else:
      list = utils.expand_text(text, self._substitutes.keys())

    data = []
    for mem in list:
      data.append("%ssubstitute {%s} {%s}" % 
                  (lyntin.commandchar, mem, self._substitutes[mem]))

    return string.join(data, "\n")

  def getStatus(self):
    """ Returns the number of substitutes we're managing."""
    return "%d substitute(s)." % len(self._substitutes.keys())


class SubstituteManager(manager.Manager):
  def __init__(self):
    self._subs = {}

  def addSubstitute(self, ses, item, sub):
    if not self._subs.has_key(ses):
      self._subs[ses] = SubstituteData()
    self._subs[ses].addSubstitute(item, sub)

  def clear(self, ses):
    if self._subs.has_key(ses):
      self._subs[ses].clear()

  def removeSubstitutes(self, ses, text):
    if self._subs.has_key(ses):
      return self._subs[ses].removeSubstitutes(text)
    return []

  def getSubstitutes(self, ses):
    if self._subs.has_key(ses):
      return self._subs[ses].getSubstitutes()
    return []

  def getInfo(self, ses, text=''):
    if self._subs.has_key(ses):
      return self._subs[ses].getInfo(text)
    return ""

  def getStatus(self, ses):
    if self._subs.has_key(ses):
      return self._subs[ses].getStatus()
    return "0 substitute(s)."

  def addSession(self, newsession, basesession=None):
    """ over-ridden from manager.Manager."""
    if basesession:
      if self._subs.has_key(basesession):
        sdata = self._subs[basesession]
        for mem in sdata._substitutes.keys():
          self.addSubstitute(newsession, mem, sdata._substitutes[mem])

  def removeSession(self, ses):
    """ over-ridden from manager.Manager."""
    if self._subs.has_key(ses):
      del self._subs[ses]

  def expand(self, ses, text):
    if self._subs.has_key(ses):
      return self._subs[ses].expand(text)
    return text

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
    Mud_filter_hook function to perform substitutions on data 
    that comes from the mud.
    """
    ses = args[0]
    text = args[-1]

    if not ses._ignoresubs:
      text = self.expand(ses, text)
    return text


commands_dict = {}

def substitute_cmd(ses, args, input):
  """
  With no arguments, prints all substitutes.
  With one argument, prints all substitutes which match the argument.
  Otherwise creates a substitution.

  Braces are advised around both 'name' and 'substitution'.

  category: commands
  """
  item = args["item"]
  substitution = args["substitution"]
  quiet = args["quiet"]

  sm = exported.get_manager("substitute")

  if not item and not substitution:
    data = sm.getInfo(ses)
    if data == '':
      data = "substitute: no substitutes defined."

    exported.write_message(data)
    return

  if not substitution:
    data = sm.getInfo(ses, item)
    if data == '':
      data = "substitute: no substitutes defined."

    exported.write_message(data)
    return 

  exported.sm.addSubstitute(ses, item, substitution)
  if not quiet:
    exported.write_message("substitute: {%s} {%s} added." % (item, substitution))

commands_dict["substitute"] = (substitute_cmd, "item= substitution= quiet:boolean=false")


def unsubstitute_cmd(ses, args, input):
  """
  Allows you to remove substitutes.

  category: commands
  """
  func = exported.get_manager("substitute").removeSubstitutes
  modutils.unsomething_helper(args, func, ses, "substitute", "substitutes")

commands_dict["unsubstitute"] = (unsubstitute_cmd, "str= quiet:boolean=false")

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

  sm = exported.get_manager("substitute")

  if not gaggedtext:
    data = sm.getInfo(ses)
    if data == '':
      data = "gag: no gags defined."

    exported.write_message(data)
    return

  for togag in gaggedtext:
    sm.addSubstitute(ses, togag, ".")
    if not quiet:
      exported.write_message("gag: {%s} added." % togag)

commands_dict["gag"] = (gag_cmd, "text* quiet:boolean=false")


def ungag_cmd(ses, args, input):
  """
  Allows you to remove gags.

  category: commands
  """
  sm = exported.get_manager("substitute")

  func = sm.removeSubstitutes
  modutils.unsomething_helper(args, func, ses, "gag", "gags")

commands_dict["ungag"] = (ungag_cmd, "str= quiet:boolean=false")


sm = None

def load():
  """ Initializes the module by binding all the commands."""
  global sm
  modutils.load_commands(commands_dict)
  sm = SubstituteManager()
  exported.add_manager("substitute", sm)

  # FIXME - the number controls the order this gets called in the grand
  # scheme of things.  we should probably do something to make this
  # more obvious.
  hooks.mud_filter_hook.register(sm.filter, 50)
  hooks.write_hook.register(sm.persist)

def unload():
  """ Unloads the module by calling any unload/unbind functions."""
  global sm
  modutils.unload_commands(commands_dict.keys())
  exported.remove_manager("substitute")
  hooks.mud_filter_hook.unregister(sm.filter)
  hooks.write_hook.unregister(sm.persist)

# Local variables:
# mode:python
# py-indent-offset:2
# tab-width:2
# End:
