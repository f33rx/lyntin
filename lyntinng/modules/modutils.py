#######################################################################
# This file is part of Lyntin
# copyright (c) Free Software Foundation 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: modutils.py,v 1.2 2002/05/09 23:20:12 willhelm Exp $
#######################################################################
import string
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


def unsomething_helper(args, func, sing, plur):
  """
  Helps automate some of the un(something) commands.

  arguments:

    'args' -- (map) the map with the 'str' and 'quiet' arguments
              in it.

    'func' -- (function instance) the function to call to unsomething
              things.  it should take a single string argument.

    'sing' -- (string) the singular form of the unsomething--for
              output

    'plur' -- (string) the plural form of the unsomething--for
              output
  """
  str = args["str"]
  quiet = args["quiet"]

  removedthings = func(str)

  if not quiet:
    if len(removedthings) == 0:
      data = "%s: No %s removed." % (sing, plur)
    else:
      data = []
      for mem in removedthings:
        if type(mem) == type(()):
          data.append("%s: {%s} {%s} removed." % (sing, mem[0], mem[1]))
        else:
          data.append("%s: {%s} removed." % (sing, mem))
      data = string.join(data, "\n")
    exported.write_message(data)

