#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id$
#######################################################################
"""
This module defines the speedwalking code.
"""

# Originally written 2002 by Sebastian John

import re
import manager, utils, lyntin

class SpeedwalkError(Exception):
  pass

class SpeedwalkManager(manager.Manager):
  """
  This is the Speedwalk Manager which does all the speedwalk expanding.
  """
  def __init__(self):
    self._dirs = {}
    self.compileRegexp()
    self._exclusions = []
  
  def clearDirs(self):
    """
    Clears all stored speedwalking dirs from the manager.
    """
    self._dirs = {}
  
  def addDir(self, alias, dir):
    """
    Adds a speedwalking direction alias to the manager.
    
    arguments:
    
      'alias' -- (string) the speedwalking alias
      
      'dir' -- (string) the actual direction
    
    """
    if alias == dir:
      raise ValueError, "Alias cannot be the same as dir."

    for mem in self._dirs.keys():
      if mem.find(alias) != -1 or mem.find(dir) != -1:
        raise SpeedwalkError, "possible ambiguity"
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
    """
    if self._dirs:
      regexp = "^(\\d*(%s))+$" % "|".join(self._dirs.keys())
      self._regexp = re.compile(regexp)
    else:
      self._regexp = None
  
  def clearExclusions(self):
    """
    Clears the list of exclusions (things we don't want to expand speedwalking
    on).
    """
    self._exclusions = []
  
  def addExclusion(self, exclusion):
    """
    Adds a speedwalking exclusion to the manager.
    
    arguments:
    
      'exclusion' -- (string) the exclusion to add
    
    """
    if exclusion not in self._exclusions:
      self._exclusions.append(exclusion)
  
  def removeExclusion(self, exclusion):
    """
    Removes a speedwalking exclusion (and only one, no wildcards or the like)
    from the manager.
    
    arguments:
    
      'exclusion' -- (string) the exclusion to remove
    
    returns:
    
      list with the exclusion removed
    """
    try:
      self._exclusions.remove(exclusion)
    except ValueError:
      return []
    else:
      return [exclusion]
  
  def getExclusions(self):
    """
    Returns the exclusion list we are managing.
    
    returns:
    
      the sorted list of exclusions being managed
    
    """
    self._exclusions.sort()
    return self._exclusions
  
  def getExclusionsInfo(self, text=""):
    """
    Returns information about the speedwalking exclusions in here.
    
    This is used by #swexcl to tell all the exclusions involved as well as
    #write which takes this information and dumps it to the file.
    
    arguments:
    
      'text=""' -- (string) the text to expand on to find exclusions that the
                   user is interested in
    
    returns:
    
      a string of all the speedwalking exclusion list information
    
    """
    if len(self._exclusions) == 0:
      return ""
    
    if text == "":
      list = self._exclusions
    else:
      list = utils.expand(text, self._exclusions)
    
    cmdchar = lyntin.commandchar
    
    data = ""
    for mem in list:
      data = data + "%sswexclude {%s}\n" % (cmdchar, mem)
    
    return data[:-1]
  
  def getExclusionsCount(self):
    """
    Returns the number of exclusions currently stored.
    
    returns:
    
      (int) the number of exclusions being managed
    
    """
    return len(self._exclusions)
  
  def clear(self):
    """
    Clears both speedwalking dir aliases and exclusions.
    """
    self.clearDirs()
    self.clearExlusions()
  
  def getInfo(self):
    """
    Returns the combined speedwalking information, used by #write to store
    the speedwalk manager state into a file.
    
    returns:
    
      (string) the combined speedwalking info for #write
    
    """
    return self.getDirsInfo() + "\n" + self.getExclusionsInfo()
  
  def getCount(self):
    """
    Returns the number of speedwalking dirs plus the number of exclusions.
    
    returns:
    
      (int) the number of speedwalking dirs together with the number of
      exclusions
    
    """
    return self.getDirsCount() + self.getExclusionsCount()
  
  def filter(self, args):
    """
    user_filter_hook function to check for speedwalking expansion.
    """
    text = args[-1]
     
    if lyntin.speedwalk == 0 or not self._dirs or text in self._exclusions or not self._regexp.search(text):
      return text

    swdirs = []
    dir = num = ""
    n = 0
    while n < len(text):
      if text[n].isdigit():
        num = num + text[n]
      else:
        dir = dir + text[n]
        if dir in self._dirs:
          if num: count = int(num)
          else: count = 1
          for i in range(count):
            swdirs.append(self._dirs[dir])
          dir = num = ""
      n = n + 1
    return "\n".join(swdirs)
