#######################################################################
# This file is part of Lyntin
# copyright (c) Free Software Foundation 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: modutils.py,v 1.1 2002/05/05 13:30:31 willhelm Exp $
#######################################################################
import exported

"""
This module holds helper functions for building other Lyntin modules.
"""

def load_commands(commands_dict):
  """ Takes in a dict and loads all the commands in that dict.

  The dict is the same form as the exported.add_command function
  signature.

  arguments:

    'commands_dict' -- (map) of command name -> tuple
  """
  for mem in commands_dict.keys(): 
    args = commands_dict[mem]
    if type(args) == type(()):
      exported.add_command(*((mem,)+args))
    else:
      exported.add_command(mem, args)

def unload_commands(commands_list):
  """ Takes in a list of command names and unloads all the commands
  in the list.

  arguments:

    'commands_list' -- (sequence) of command name strings
  """
  for mem in commands_list:
    exported.remove_command(mem)
