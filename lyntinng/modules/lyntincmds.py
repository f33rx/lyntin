#######################################################################
# This file is part of Lyntin
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: lyntincmds.py,v 1.7 2002/06/18 04:01:12 willhelm Exp $
#######################################################################
import string, traceback
import net, utils, engine, lyntin, exported, hooks, modutils

"""
This module holds commands that are new and unique to Lyntin.
"""
commands_dict = {}

def ansi_cmd(session, args, input):
  """
  Toggles whether Lyntin takes out all the ansi coloring for you
  or not.  Mind you, the mud has to send ansi colors your way--otherwise
  this toggle won't do anything for you at all.

  This is to help folks whose mud servers aren't so friendly.

  category: commands
  """
  option = args["option"]

  if option == 1:
    lyntin.ansicolor = 1
    exported.write_message("ansi: ansi is now enabled.")

  elif option == 0:
    lyntin.ansicolor = 0
    exported.write_message("ansi: ansi is now disabled.")

  else:
    if lyntin.ansicolor:
      exported.write_message("ansi: ansi color is enabled.")
    else:
      exported.write_message("ansi: ansi color is disabled.")

commands_dict["ansi"] = (ansi_cmd, "option:booleanornone=")


def datagrep_cmd(session, args, input):
  """
  Searches this session's databuffer with a regular expression printing 
  all matches in their entirety.

  category: commands
  """
  if (session.getName() == "common"):
    exported.write_error("datagrep cannot be applied to common session.")
    return

  pattern = args["pattern"]
  size = args["size"]

  ret = session.getDataBuffer().grepbuffer(pattern,size)
  exported.write_message("datagrep %s results:\n%s"
                         % (pattern, string.join(ret, "\n")))

commands_dict["datagrep"] = (datagrep_cmd, "pattern size:int=300")


def datagreplines_cmd(session, args, input):
  """
  Searches the lines in this session's databuffer with a regular 
  expression printing all matching lines in their entirety.

  category: commands
  """
  if (session.getName() == "common"):
    exported.write_error("datagrep cannot be applied to common session.")
    return

  pattern = args["pattern"]
  size = args["size"]
  ret = session.getDataBuffer().greplines(pattern,size)
  exported.write_message("datagreplines %s results:\n%s"
                         % (pattern, string.join(ret, "")))

commands_dict["datagreplines"] = (datagreplines_cmd, "pattern size:int=300")


def diagnostics_cmd(session, args, input):
  """
  This is very useful for finding out all the information about Lyntin
  while it's running.  This will print out operating system information,
  Python version, what threads are running (assuming they're registered
  with the ThreadManager), hooks, functions connected to hooks, and
  #info for every session.  It's very helpful in debugging problems that
  are non-obvious or are platform specific.  It's also invaluable in
  bug-reporting.

  It can take a filename argument and will copy the #diagnostics output
  to that file.  This allows you easier method of submitting diagnostics
  output along with bug reports.

  category: commands
  """
  import os, sys
  message = []
  message.append("Diagnostics:")
  message.append(exported.get_engine().getDiagnostics())

  message.append("Thread statii:")
  data = exported.get_engine().checkthreads()
  for mem in data:
    message.append(mem)
      
  message.append("OS/Python information:")
  try: 
    message.append("   sys.version: %s" % sys.version)
  except:
    message.append("   sys.version not available.")

  try: 
    message.append("   os.name: %s" % os.name)
  except:
    message.append("   os.name not available.")
 
  message.append("Lyntin Options:")
  for mem in lyntin.options.keys():
    message.append("   %s: %s" % (mem, repr(lyntin.options[mem])))

  exported.write_message(string.join(message, "\n"))
  exported.write_message("This information can be dumped to a "
        "file by doing:\n   #diagnostics dumpfile.txt")

  logfile = args["logfile"]
  if logfile:
    import time
    try:
      f = open(logfile, "w")
      f.write("This file was created on: %s\n\n" % time.ctime(time.time()))
      f.write(message)
      f.close()
      exported.wirte_message("diagnostics: written out to file %s." % logfile)
    except Exception, e:
      exported.write_error("diagnostics: Error writing to file %s. %s" 
                            % (logfile, e))

commands_dict["diagnostics"] = (diagnostics_cmd, "logfile=")


def mudecho_cmd(session, args, input):
  """
  Toggles echoing user commands.  When echo is on, all user commands
  will be printed to the screen.  When off, user commands are hidden.

  Muds use echo for switching in and out of password handling.  This
  command was created so that if your mud screws up echo settings,
  you can set it locally.

  category: commands
  """
  import event
  option = args["option"]

  if option == 1:
    event.EchoEvent(1).enqueue() 
    exported.write_message("mudecho: turned on manually.")
  elif option == 0:
    event.EchoEvent(0).enqueue() 
    exported.write_message("mudecho: turned off manually.")

commands_dict["mudecho"] = (mudecho_cmd, "option:boolean")


def raw_cmd(session, args, input):
  """
  Sends input straight to the mud.

  category: commands
  """
  session.writeSocket(args["input"] + "\n")
  
commands_dict["raw"] = (raw_cmd, "input=", "limitparsing=0")


def load():
  """ Initializes the module by binding all the commands."""
  exported.write_message("binding commands.")
  modutils.load_commands(commands_dict)


def unload():
  """ Unloads the module by calling any unload/unbind functions."""
  exported.write_message("unbinding commands.")
  modutils.unload_commands(commands_dict.keys())
