#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: deed.py,v 1.1 2002/06/18 04:01:12 willhelm Exp $
#######################################################################
"""
This module defines the DeedManager which handles deeds (user events).
"""

# deed code originally written by Sebastian John.

import string
import manager, utils, lyntin, exported, modutils

class DeedData:
  def __init__(self):
    self._deeds = []
  
  def addDeed(self, deed):
    """ Adds a deed to the list.
    
    arguments:
    
      'deed' -- (string) the deed
    
    """
    self._deeds.append(deed)
  
  def clear(self):
    """ Removes all the deeds."""
    self._deeds = []
  
  def removeDeeds(self, text):
    """ Removes deeds from the list.
    
    Returns a list of the gags that were removed.
    
    arguments:
    
      'text' -- (string) deeds will be removed that match the text
    
    returns:
    
      list of strings of removed deeds
    
    """
    baddeeds = utils.expand_text(text, self._deeds)
    for mem in baddeeds:
      self._deeds.remove(mem)
    return baddeeds
  
  def getDeeds(self):
    """ Returns all deeds stored.
    
    returns:
    
      list of deed strings
    """
    return self._deeds
  
  def getInfo(self, num=""):
    """ Returns information about the deeds in here.
    
    This is used only by #deed to show all the deeds stored.
    
    arguments:
    
      'num=""' -- (string) if a number, only the last num deeds will be
                  returned
    
    returns:
    
      (string) one big string with all the deeds in it
    
    """
    if not self._deeds:
      return ""
    
    if num.isdigit():
      count = int(num)
      list = self._deeds[-count:]
    else:
      list = self._deeds
    
    return string.join(list, "\n")
  
  def getStatus(self):
    """ Returns the number of deeds actually stored.

    returns:

      (int) count of deeds.
    """
    return "%d deed(s)." % len(self._deeds)

class DeedManager(manager.Manager):
  def __init__(self):
    self._deeds = {}

  def addDeed(self, ses, deed):
    if not self._deeds.has_key(ses):
      self._deeds[ses] = DeedData()
    self._deeds[ses].addDeed(deed)

  def clear(self, ses):
    if self._deeds.has_key(ses):
      self._deeds[ses].clear()

  def removeDeeds(self, text):
    if self._deeds.has_key(ses):
      return self._deeds[ses].removeDeeds(text)
    return []

  def getDeeds(self, ses):
    if self._deeds.has_key(ses):
      return self._deeds[ses].getDeeds()
    return []

  def getInfo(self, ses, num=""):
    if self._deeds.has_key(ses):
      return self._deeds[ses].getInfo(num)
    return ""

  def getStatus(self, ses):
    if self._deeds.has_key(ses):
      return self._deeds[ses].getStatus()
    return "0 deed(s)."


commands_dict = {}

def deed_cmd(ses, args, input):
  """
  This adds a deed or prints all the deeds stored till now.

  category: commands
  """
  # original deed_cmd code contributied by Sebastian John

  if (ses.getName() == "common"):
    exported.write_error("deed cannot be applied to common session.")
    return

  deedtext = args["text"]
  quiet = args["quiet"]

  varman = exported.get_manager("variable")
  if varman:
    varexpansion = varman.expand(ses, deedtext)
    if varexpansion:
      deedtext = varexpansion

  if not deedtext:
    data = exported.get_manager("deed").getInfo(ses)
    if data == "":
      data = "deed: no deeds defined."
    
    exported.write_message(data)
    return
  
  if deedtext.isdigit():
    data = exported.get_manager("deed").getInfo(ses, deedtext)
    if data == "":
      data = "deed: no deeds defined."
    
    exported.write_message(data)
    return

  exported.get_manager("deed").addDeed(ses, deedtext)
  if not quiet:
    exported.write_message("deed: {%s} added." % deedtext)

commands_dict["deed"] = (deed_cmd, "text= quiet:boolean=false")


dm = None

def load():
  """ Initializes the module by binding all the commands."""
  global dm
  modutils.load_commands(commands_dict)
  dm = DeedManager()
  exported.add_manager("deed", dm)


def unload():
  """ Unloads the module by calling any unload/unbind functions."""
  global dm
  modutils.unload_commands(commands_dict.keys())
  exported.remove_manager("deed")
