#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: speedwalk.py,v 1.10 2002/05/04 17:39:58 jmberne Exp $
#######################################################################
"""
This module defines the speedwalking code.
"""

# Originally written 2002 by Sebastian John

import re
import manager, utils, lyntin, engine

class SpeedwalkManager(manager.Manager):
  """
  This is the Speedwalk Manager which does all the speedwalk expanding.
  """
  def __init__(self):
    self._dirs = {}
    self.compileRegexp()
    self._excludes = []
  
  def clearDirs(self):
    """
    Clears all stored speedwalking dirs from the manager.
    """
    self._dirs = {}
    self._aliases = []
  
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
  
  def removeDir(self, alias):
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
      list = utils.expand(text, self._dirs.keys())
    
    cmdchar = lyntin.commandchar
    
    data = ""
    for mem in list:
      data = data + "%sswdir {%s} {%s}\n" % (cmdchar, mem, self._dirs[mem])
    
    return data[:-1]
  
  def getDirsCount(self):
    """
    Returns how many (alias, dir) tuples we are managing.
    
    returns:
    
      (int) the number of (alias, dir) tuples being managed
    
    """
    return len(self._dirs)
  
  def compileRegexp(self):
    """
    Compiles the actual speedwalking pattern.
    Also maintains self._aliases - the default excludes.
    """
    if self._dirs:
      keys = "|".join(self._dirs.keys())
      regexp = "^(\\d*(%s))+$" % (keys)
      self._regexp = re.compile(regexp)
      self._aliases = self._dirs.values()
    else:
      self._regexp = None
      self._aliases = []
  
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
  
  def removeExclude(self, exclude):
    """
    Removes a speedwalking exclude (and only one, no wildcards or the like)
    from the manager.
    
    arguments:
    
      'exclude' -- (string) the exclude to remove
    
    returns:
    
      list with the exclude removed
    """
    try:
      self._excludes.remove(exclude)
    except ValueError:
      return []
    else:
      return [exclude]
  
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
      list = utils.expand(text, self._excludes)
    
    cmdchar = lyntin.commandchar
    
    data = ""
    for mem in list:
      data = data + "%sswexclude {%s}\n" % (cmdchar, mem)
    
    return data[:-1]
  
  def getExcludeCount(self):
    """
    Returns the number of excludes currently stored.
    
    returns:
    
      (int) the number of excludes being managed
    
    """
    return len(self._excludes)
  
  def clear(self):
    """
    Clears both speedwalking dir aliases and excludes.
    """
    self.clearDirs()
    self.clearExcludes()
  
  def getInfo(self):
    """
    Returns the combined speedwalking information, used by #write to store
    the speedwalk manager state into a file.
    
    returns:
    
      (string) the combined speedwalking info for #write
    
    """
    return self.getDirsInfo() + "\n" + self.getExcludesInfo()
  
  def getCount(self):
    """
    Returns the number of speedwalking dirs plus the number of excludes.
    
    returns:
    
      (int) the number of speedwalking dirs together with the number of
      excludes
    
    """
    return self.getDirsCount() + self.getExcludesCount()
  
  def filter(self, args):
    """
    user_filter_hook function to check for speedwalking expansion.
    """
    session = args[0]
    internal = args[1]
    text = args[-1]
     
    if lyntin.speedwalk == 0 or not self._dirs or text in self._excludes or text in self._aliases:
      return text

    if not self._regexp.match(text):
      return text

    swdirs = []
    dirsavailable = self._dirs.keys()
    dir = num = ""
    n = 0
    while n < len(text):
      if text[n].isdigit():
        num = num + text[n]
      else:
        dir = dir + text[n]
        if dir in dirsavailable:
          if num: count = int(num)
          else: count = 1
          for i in range(count):
            swdirs.append(self._dirs[dir])
          dir = num = ""
      n = n + 1

    output = ";".join(swdirs)
    if output == text:
      return text
    else:
      engine.myengine.handleUserData(";".join(swdirs), internal, session)
      return None


