#######################################################################
# This file is part of Lyntin
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: lyntincmds.py,v 1.19 2002/10/24 23:07:04 willhelm Exp $
#######################################################################
import string
import net, utils, engine, lyntin, exported, hooks, modutils

"""
This module holds commands that are new and unique to Lyntin.
"""
commands_dict = {}

def bv(bool):
  if bool:
    return "on"
  return "off"

def config_cmd(ses, args, input):
  """
  Allows you to set a wide variety of options, some of which are
  session oriented and some of which are global.  Typing "#config"
  by itself will print out all the options it knows about.

  category: commands
  """
  name = args["name"]
  value = args["value"]
  quiet = args["quiet"]

  if not name:
    output = "Global:\n" + \
             "   ansicolor     " + bv(lyntin.ansicolor) + "  (boolean)\n" + \
             "   commandchar   " + lyntin.commandchar + "  (char)\n" + \
             "   mudecho       " + bv(lyntin.mudecho) + "  (boolean)\n" + \
             "   speedwalk     " + bv(lyntin.speedwalk) + "  (boolean)\n"
    if lyntin.evalmode == lyntin.LYNTIN:
      output += "   evalmode      lyntin  (\"lyntin\" or \"tintin\")\n"
    else:
      output += "   evalmode      tintin  (\"lyntin\" or \"tintin\")\n"

    output += "Session:\n" + \
              "   ignoreactions " + bv(ses._ignoreactions) + "  (boolean)\n" + \
              "   ignoresubs    " + bv(ses._ignoresubs) + "  (boolean)\n" + \
              "   verbatim      " + bv(ses._verbatim) + "  (boolean)\n"
    exported.write_message(output)
    return

  # set the variable to this value
  if name in ["ignoreactions", "ignoresubs", "verbatim"]:
    value = utils.convert_boolean(value)
    if value == 1 or value == 0:
      exec("ses._%s = value" % name)
      if not quiet:
        exported.write_message("config: %s set to %s." % (name, bv(value)))
    else:
      exported.write_error("config: '%s' is not a valid boolean value." % (value))
    return

  if name in ["variablechar", "commandchar"]:
    if len(value) == 1:
      exec("lyntin.%s = value" % name)
      if not quiet:
        exported.write_message("config: %s set to '%s'." % (name, value))
    else:
      exported.write_error("config: '%s' is not a valid %s value." % (value, name))
    return

  if name in ["ansicolor", "speedwalk"]:
    value = utils.convert_boolean(value)
    if value == 1 or value == 0:
      exec("lyntin.%s = value" % name)
      if not quiet:
        exported.write_message("config: %s set to %s." % (name, bv(value)))
    else:
      exported.write_error("config: '%s' is not a valid boolean value." % (value))
    return

  if name == "mudecho":
    import event
    old = lyntin.mudecho
    value = utils.convert_boolean(value)

    if value == 1:
      event.EchoEvent(1).enqueue() 
    else:
      event.EchoEvent(0).enqueue() 

    if not quiet:
      exported.write_message("config: %s set to %s." % (name, bv(value)))
    return

  if name == "evalmode":
    old = lyntin.evalmode
    if value == "tintin":
      lyntin.evalmode = lyntin.TINTIN
      hooks.evalmode_change_hook.spamhook((old, lyntin.TINTIN))
      if not quiet:
        exported.write_message("config: %s set to %s." % (name, value))
    elif value == "lyntin":
      lyntin.evalmode = lyntin.LYNTIN
      hooks.evalmode_change_hook.spamhook((old, lyntin.LYNTIN))
      if not quiet:
        exported.write_message("config: %s set to %s." % (name, value))
    else:
      exported.write_error("config: '%s' is not a valid value." % (value))
    return

  exported.write_error("config: did not recognize '%s' as an attribute." % name)
      
commands_dict["config"] = (config_cmd, "name= value= quiet:boolean=false")
  
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

  Note: Windows users should either use two \\'s or use / to separate
  directory names.

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
 
  message.append("   lyntin: %s" % (lyntin.VERSION[:lyntin.VERSION.find("\n")]))

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
      f.write("This file was created on: %s" % time.asctime())
      f.write(os.linesep + os.linesep)
      f.write(string.join(message, os.linesep))
      f.close()
      exported.write_message("diagnostics: written out to file %s." % logfile)
    except Exception, e:
      exported.write_error("diagnostics: Error writing to file %s. %s" 
                            % (logfile, e))

commands_dict["diagnostics"] = (diagnostics_cmd, "logfile=")


def raw_cmd(session, args, input):
  """
  Sends input straight to the mud.

  category: commands
  """
  session.writeSocket(args["input"] + "\n")
  
commands_dict["raw"] = (raw_cmd, "input=", "limitparsing=0")


def load():
  """ Initializes the module by binding all the commands."""
  modutils.load_commands(commands_dict)


def unload():
  """ Unloads the module by calling any unload/unbind functions."""
  modutils.unload_commands(commands_dict.keys())

# Local variables:
# mode:python
# py-indent-offset:2
# tab-width:2
# End:
