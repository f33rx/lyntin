######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: speedwalk.py,v 1.10 2002/08/20 02:39:04 willhelm Exp $
#######################################################################
"""
This module defines the speedwalking code.
"""

# Originally written 2002 by Sebastian John

import re, string
import manager, utils, lyntin, modutils, hooks, exported

class SpeedwalkHash:
  def __init__(self):
    self._dirs = {}
    self.compileRegexp()
    self._excludes = []
  
  def __copy__(self):
    sm = SpeedwalkManager()
    for mem in self._dirs.keys():
      sm.addDir(mem, self._dirs[mem])

    for mem in self._excludes:
      sm.addExclude(mem)
    return sm

  def clearDirs(self):
    """
    Clears all stored speedwalking dirs from the manager.
    """
    self._dirs = {}
    self.compileRegexp()
  
  def addDir(self, alias, dir):
    """
    Adds a speedwalking direction alias to the manager.
    
    arguments:
    
      'alias' -- (string) the speedwalking alias
      
      'dir' -- (string) the actual direction
    
    """
    for mem in self._dirs.keys():
      if mem.find(alias) != -1 or mem.find(dir) != -1:
        raise ValueError, "possible ambiguity"
    self._dirs[alias] = dir
    self.compileRegexp()
  
  def removeDirs(self, alias):
    """
    Removes the speedwalking alias and only this one (no wildcard patterns
    are possible).
    
    arguments:
    
      'alias' -- (string) the speedwalking alias to be removed
    
    returns:
    
      list with the (alias, dir) tuple of the removed speedwalking alias
    
    """
    try:
      dir = self._dirs[alias]
      del self._dirs[alias]
    except KeyError:
      return []
    else:
      self.compileRegexp()
      return [(alias, dir)]
  
  def getDirs(self):
    """
    Returns a list of all the speedwalking aliases currently defined.
    
    returns:
    
      sorted list of (alias, dir) tuples of the speedwalking aliases we are
      managing
    
    """
    dirs = self._dirs.items()
    dirs.sort()
    return dirs
  
  def getDirsInfo(self, text=""):
    """
    Returns information about the speedwalking aliases in here.
    
    This is used by #swdir to tell all the speedwalking aliases involved as
    well as #write which takes this information and dumps it to the file.
    
    arguments:
    
      'text=""' -- (string) the text to expand on to find aliases that the
                   user is interested in
    
    returns:
    
      a string of all the speedwalking alias information
    
    """
    if len(self._dirs) == 0:
      return ""
    
    if text == "":
      list = self._dirs.keys()
    else:
      list = utils.expand_text(text, self._dirs.keys())
    
    cmdchar = lyntin.commandchar
    
    data = []
    for mem in list:
      data.append("%sswdir {%s} {%s}" % (cmdchar, mem, self._dirs[mem]))
    
    return string.join(data, "\n")
  
  def getDirStatus(self):
    """ Returns a one liner about dirs.

    returns:

      (string) one-liner about dirs managed.
    """
    return "%d dir(s)." % len(self._dirs)
  
  def compileRegexp(self):
    """
    Compiles the actual speedwalking pattern.
    Also maintains self._aliases the default excludes.
    """
    if self._dirs:
      keys = "|".join(self._dirs.keys())
      regexp = "^(\\d*(%s))+$" % (keys)
      self._regexp = re.compile(regexp)
      self._aliases = self._dirs.values()
      self._dirs_available = self._dirs.keys()
    else:
      self._regexp = None
      self._aliases = []
      self._dirs_available = []
  
  def clearExcludes(self):
    """
    Clears the list of excludes (things we don't want to expand speedwalking
    on).
    """
    self._excludes = []
  
  def addExclude(self, exclude):
    """
    Adds a speedwalking exclude to the manager.
    
    arguments:
    
      'exclude' -- (string) the exclude to add
    
    """
    if exclude not in self._excludes:
      self._excludes.append(exclude)
  
  def removeExcludes(self, exclude):
    """
    Removes a speedwalking exclude (and only one, no wildcards or the like)
    from the manager.
    
    arguments:
    
      'exclude' -- (string) the exclude to remove
    
    returns:
    
      list with the exclude removed
    """
    badexcludes = utils.expand_text(exclude, self._excludes)

    for mem in badexcludes:
      self._excludes.remove(mem)

    return badexcludes
  
  def getExcludes(self):
    """
    Returns the exclude list we are managing.
    
    returns:
    
      the sorted list of excludes being managed
    
    """
    self._excludes.sort()
    return self._excludes
  
  def getExcludesInfo(self, text=""):
    """
    Returns information about the speedwalking excludes in here.
    
    This is used by #swexcl to tell all the excludes involved as well as
    #write which takes this information and dumps it to the file.
    
    arguments:
    
      'text=""' -- (string) the text to expand on to find excludes that the
                   user is interested in
    
    returns:
    
      a string of all the speedwalking exclude list information
    
    """
    if len(self._excludes) == 0:
      return ""
    
    if text == "":
      list = self._excludes
    else:
      list = utils.expand_text(text, self._excludes)
    
    cmdchar = lyntin.commandchar
    
    data = []
    for mem in list:
      data.append("%sswexclude {%s}" % (cmdchar, mem))
    
    return string.join(data, "\n")
  
  def getExcludeStatus(self):
    """ Returns a one-line string describing how many excludes we have.

    returns:

      (string) one liner describing how many excludes we have
    """
    return "%d exclude(s)." % len(self._excludes)

  def clear(self):
    """
    Clears both speedwalking dir aliases and excludes.
    """
    self.clearDirs()
    self.clearExcludes()
  

class SpeedwalkManager(manager.Manager):
  def __init__(self):
    self._hashes = {}

  def clearDirs(self, ses):
    if self._hashes.has_key(ses):
      self._hashes[ses].clearDirs()

  def addDir(self, ses, alias, dir):
    if not self._hashes.has_key(ses):
      self._hashes[ses] = SpeedwalkHash()
    self._hashes[ses].addDir(alias, dir)

  def removeDirs(self, ses, alias):
    if self._hashes.has_key(ses):
      return self._hashes[ses].removeDirs(alias)
    return []

  def getDirs(self, ses):
    if self._hashes.has_key(ses):
      return self._hashes[ses].getDirs()
    return []

  def getDirsInfo(self, ses, text=""):
    if self._hashes.has_key(ses):
      return self._hashes[ses].getDirsInfo(text)
    return ""

  def getStatus(self, ses):
    if self._hashes.has_key(ses):
      sdata = self._hashes[ses]
      return "%s %s" % (sdata.getDirStatus(), sdata.getExcludeStatus())
    return "0 dir(s). 0 exclude(s)."

  def addExclude(self, ses, exclude):
    if not self._hashes.has_key(ses):
      self._hashes[ses] = SpeedwalkHash()
    self._hashes[ses].addExclude(exclude)

  def removeExcludes(self, ses, exclude):
    if self._hashes.has_key(ses):
      return self._hashes[ses].removeExcludes(exclude)
    return []

  def getExcludesInfo(self, ses):
    if self._hashes.has_key(ses):
      return self._hashes[ses].getExcludesInfo()
    return ""

  def getInfo(self, ses):
    if self._hashes.has_key(ses):
      myhash = self._hashes[ses]
      return myhash.getDirsInfo() + "\n" + myhash.getExcludesInfo() 
    return ""

  def clear(self, ses):
    if self._hashes.has_key(ses):
      self._hashes[ses].clear()
  
  def addSession(self, newsession, basesession=None):
    """ over-ridden from manager.Manager."""
    if basesession:
      if self._hashes.has_key(basesession):
        sdata = self._hashes[basesession]
        for mem in sdata._dirs.keys():
          self.addDir(newsession, mem, sdata._dirs[mem])

        for mem in sdata._excludes:
          self.addExclude(newsession, mem)

  def removeSession(self, ses):
    """ over-ridden from manager.Manager."""
    if self._hashes.has_key(ses):
      del self._hashes[ses]

  def persist(self, args):
    """
    write_hook function for persisting the state of our session.
    """
    ses = args[0]
    file = args[1]
    quiet = args[2]

    data = self.getInfo(ses)
    if data:
      if quiet == 1:
        data = data.replace("\n", " quiet={true}\n")
        file.write(data + " quiet={true}\n")
      else:
        file.write(data + "\n")

  def userfilter(self, args):
    """
    user_filter_hook function to check for speedwalking expansion.
    """
    ses = args[0]
    internal = args[1]
    verbatim = args[2]
    text = args[-1]
    
    if not self._hashes.has_key(ses) or lyntin.speedwalk == 0 or verbatim == 1:
      return text

    sdata = self._hashes[ses]

    if not sdata._dirs or not sdata._regexp or text in sdata._excludes \
        or text in sdata._aliases or not sdata._regexp.match(text):
      return text
    
    swdirs = []
    dir = num = ""
    for char in text:
      if char.isdigit():
        num = num + char
      else:
        dir = dir + char
        if dir in sdata._dirs_available:
          if num: count = int(num)
          else: count = 1
          for i in range(count):
            swdirs.append(sdata._dirs[dir])
          dir = num = ""
    
    output = ";".join(swdirs)
    if output == text:
      return text
    else:
      # anything that gets recursed on should be recursed internally
      exported.get_engine().handleUserData(output, 1, ses)
      return None


commands_dict = {}

def swdir_cmd(ses, args, input):
  """
  This adds speedwalking aliases and tells you the current speedwalking dirs
  already registered.

  ex:

     #swdir {n} {north}
     #swdir {s} {south}
     #swdir {e} {east}
     #swdir {w} {west}
     #swdir {NE} {northeast}
     #swdir {l} {look}
     ...

  see also: swexclude

  category: commands
  """
  # originally written by Sebastian John
  alias = args["alias"]
  dir = args["dir"]
  quiet = args["quiet"]

  # they typed '#swdir'--print out all the current speedwalking dirs
  if not alias and not dir:
    data = exported.get_manager("speedwalk").getDirsInfo(ses)
    if data == '':
      data = "swdir: no speedwalking dirs defined."

    exported.write_message(data)
    return

  # they typed '#swdir dd*' and are looking for matching speedwalking dirs
  if not dir:
    data = exported.get_manager("speedwalk").getDirsInfo(ses, alias)
    if data == '':
      data = "swdir: no speedwalking dirs defined."

    exported.write_message(data)
    return

  try:
    exported.get_manager("speedwalk").addDir(ses, alias, dir)
    if not quiet:
      exported.write_message("swdir: {%s} {%s} added." % (alias, dir))
  except ValueError, e:
    exported.write_error("swdir: cannot add alias '%s': %s." % (alias, e))

commands_dict["swdir"] = (swdir_cmd, "alias= dir= quiet:boolean=false")


def swexclude_cmd(ses, args, input):
  """
  Adds words that should be excluded from speedwalk expansion as well
  as tells you which words are currently being excluded.

  If you had swdirs "n", "e", "s", and "w", you might want to create
  excludes for the words "sense", "news", "sew", ...  Which are real
  words that you most likely don't want to be expanded.

  see also: swdir

  category: commands
  """
  # originally written by Sebastian John
  excludes = args["exclude"]
  quiet = args["quiet"]

  # they typed '#swexclude'--print out all current speedwalking excludes
  if len(excludes) == 0:
    data = exported.get_manager("speedwalk").getExcludesInfo(ses)
    if data == '':
      data = "swexcl: no speedwalking excludes defined."

    exported.write_message(data)
    return

  for exclude in excludes:
    exported.get_manager("speedwalk").addExclude(ses, exclude)
    if not quiet:
      exported.write_message("swexclude: {%s} added." % exclude)

commands_dict["swexclude"] = (swexclude_cmd, "exclude* quiet:boolean=false")


def unswdir_cmd(ses, args, input):
  """
  Allows you to remove swdirs.

  category: commands
  """
  func = exported.get_manager("speedwalk").removeDirs
  modutils.unsomething_helper(args, func, ses, "swdir", "swdirs")

commands_dict["unswdir"] = (unswdir_cmd, "str= quiet:boolean=false")


def unswexclude_cmd(ses, args, input):
  """
  Allows you to remove swexcludes.

  category: commands
  """
  func = exported.get_manager("speedwalk").removeExcludes
  modutils.unsomething_helper(args, func, ses, "swexclude", "swexcludes")

commands_dict["unswexclude"] = (unswexclude_cmd, "str= quiet:boolean=false")


sm = None

def load():
  """ Initializes the module by binding all the commands."""
  global sm
  modutils.load_commands(commands_dict)
  sm = SpeedwalkManager()
  exported.add_manager("speedwalk", sm)

  # FIXME - the number controls the order this gets called in the grand
  # scheme of things.  we should probably do something to make this
  # more obvious.
  hooks.user_filter_hook.register(sm.userfilter, 80)
  hooks.write_hook.register(sm.persist)

def unload():
  """ Unloads the module by calling any unload/unbind functions."""
  global sm
  modutils.unload_commands(commands_dict.keys())
  exported.remove_manager("speedwalk")
  hooks.user_filter_hook.unregister(sm.userfilter)
  hooks.write_hook.unregister(sm.persist)

# Local variables:
# mode:python
# py-indent-offset:2
# tab-width:2
# End:
