#######################################################################
# This file is part of Lyntin
# copyright (c) Will Guaraldi 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: basic.py,v 1.19 2002/02/23 21:10:32 willhelm Exp $
#######################################################################
import re, string, traceback
import net, utils, engine, lyntin, exported

"""
This module holds a series of basic commands.
"""
INT_REGEXP = re.compile("\d+")

def action_cmd(session, words, input):
  """#action [<trigger> <response>]

  This adds actions and tells you the current action stati of actions
  already registered.
  """
  # they typed '#action'--print out all the current actions
  if len(words) == 1:
    data = session.getManager("action").getInfo()
    if data == '':
      data = "action: no actions defined."

    exported.write_message(data)
    return

  # they typed '#action dd*' and are looking for matching actions
  if len(words) == 2:
    data = session.getManager("action").getInfo(words[1])
    if data == '':
      data = "action: no actions defined."

    exported.write_message(data)
    return

  try:
    # knock off the first word which is the command
    inputadjusted = input.split(' ', 1)[1]

    # split it into parts
    (a, b) = utils.split_braced(inputadjusted)

    session.getManager("action").addAction(a, b)
    exported.write_message("action: {" + a + "} -> {" + b + "} added.")
  except:
    exported.write_error("action: cannot be added.")
    traceback.print_exc()


def alias_cmd(session, words, input):
  """#alias [<alias> <expansion>]

  This adds aliases and tells you the current alias stati of aliases
  already registered.
  """
  # they typed '#alias'--print out all current aliases
  if len(words) == 1:
    data = session.getManager("alias").getInfo()
    if data == '':
      data = "alias: no aliases defined."

    exported.write_message(data)
    return

  # they typed '#alias dd*' and are looking for matching aliases
  if len(words) == 2:
    data = session.getManager("alias").getInfo(words[1])
    if data == '':
      data = "alias: no aliases defined."

    exported.write_message(data)
    return

  try:
    # knock off the first word which is the command
    inputadjusted = input.split(' ', 1)[1]

    # split it into parts
    (a, b) = utils.split_braced(inputadjusted)

    session.getManager("alias").addAlias(a, b)
    exported.write_message("alias: {" + a + "} -> {" + b + "} added.")
  except:
    exported.write_error("alias: cannot be added.")
    traceback.print_exc()


def ansi_cmd(session, words, input):
  """#ansi [on|off]

  With no arguments, tells you whether ansicolor is enabled.
  With arguments, sets the ansicolor global variable.
  """
  if len(words) == 1:
    if lyntin.ansicolor:
      exported.write_message("ansi: ansi color is enabled.")
    else:
      exported.write_message("ansi: ansi color is disabled.")
    return

  if words[1] == '1' or words[1] == 'on':
    lyntin.ansicolor = 1
    exported.write_message("ansi: ansi is now enabled.")
  elif words[1] == '0' or words[1] == 'off':
    lyntin.ansicolor = 0
    exported.write_message("ansi: ansi is now disabled.")
  else:
    exported.write_error("syntax: #ansi [on|off]")


def boss_cmd(session, words, input):
  """#boss

  This command prints stuff to the screen that looks important.
  Oddly enough, it's actually linked list code.
  """
  # FIXME - somehow make this more universal by having a bossfile?
  exported.write_mud_data(lyntin.BOSSTEXT)


def char_cmd(session, words, input):
  """#char <new-command-denoting-character>

  With no arguments, tells you what the current command character
  is.  With arguments allows you to set the global command
  character.
  """
  if len(words) == 1:
    exported.write_message("char: current command character is " + 
                                 lyntin.commandchar + ".")
    return

  lyntin.commandchar = words[1]
  exported.write_message("char: new command character is " + 
                               lyntin.commandchar + ".")


def clear_cmd(session, words, input):
  """#clear

  This command clears a session of all session data (except
  the actual connection).
  """
  try:
    session.clear()
    exported.write_message("clear: session " + 
                                 session.getName() + " cleared.")
  except:
    exported.write_error("clear: error in clearing session.")

  
def cr_cmd(session, words, input):
  """#cr

  This sends a carriage return to the mud.  Sometimes this is useful
  in aliases and the like.
  """
  session.writeSocket("\n")


def diagnostics_cmd(session, words, input):
  """#diagnostics

  This tells you the current status of Lyntin.  Starting with 
  events and moving into the threadmanager and such.  Also pulls
  from the os and sys modules.
  """
  import os, sys
  message = "Diagnostics:\n"
  message = message + engine.myengine.getDiagnostics()

  message = message + "Thread statii:\n"

  data = engine.myengine.checkthreads()
  for mem in data:
    message += mem + "\n"
      
  message = message + "OS/Python information:\n"
  try: 
    message = message + "   sys.version: " + sys.version + "\n"
  except:
    message = message + "   sys.version not available.\n"

  try: 
    message = message + "   os.name: " + os.name + "\n"
  except:
    message = message + "   os.name not available.\n"
 
  message = message + "Lyntin Options:\n"
  for mem in lyntin.options.keys():
    message = message + "   " + mem + ": " + lyntin.options[mem] + "\n"

  exported.write_message(message)
  exported.write_message("This information can be dumped to a "
        "file by doing:\n   #diagnostics dumpfile.txt")

  if len(words) == 2:
    import time
    try:
      f = open(words[1], "w")
      f.write("This file was created on: " + time.ctime(time.time()) + 
              "\n\n")
      f.write(message)
      f.close()
    except:
      exported.write_error("Error writing to file " + words[1] + ".")
      traceback.print_exc()


def end_cmd(session, words, input):
  """#end

  This is the end command--it shuts down Lyntin.
  """
  import event
  exported.write_message("end: you'll be back...")
  event.ShutdownEvent().enqueue()


def gag_cmd(session, words, input):
  """#gag [<text>]

  With no arguments, it tells you all the gags currently existing.
  With arguments, it sets up a new gag.
  """
  if len(words) == 1:
    data = session.getManager("gag").getInfo()
    if data == '':
      data = "gag: no gags defined."

    exported.write_message(data)
    return

  gaggedtext = utils.strip_braces(input.split(' ', 1)[1])
  session.getManager("gag").addGag(gaggedtext)
  exported.write_message("gag: '" + gaggedtext + "' added.")


def help_cmd(session, words, input):
  """#help [topic|command]

  This is the main help command for Lyntin.
  """
  import os

  helpdir = lyntin.lyntindir + "help"
  data = "::lyntin help::\n"

  if len(words) == 1:
    file_list = os.listdir(helpdir)
    file_list.sort()

    topic_list = []
    command_list = []

    for mem in file_list:
      if len(mem) < 5: continue

      if mem[-4:] == ".tpc":
        topic_list.append(mem[:-4])

    data += "\nTopics Available:\n"
    topic_list.sort()
    data += utils.columnize(textlist=topic_list, indent=3)

    data += "\n\nCommands Available:\n"
    command_list = engine.myengine.getCommands()
    command_list.sort()
    data += utils.columnize(textlist=command_list, indent=3)

    exported.write_message(data)
    return


  for mem in words[1:]:
    try:
      f = open(helpdir + "/" + mem + ".tpc", "r")
    except:
      try:
        f = open(helpdir + "/" + mem + ".cmd", "r")
      except:
        data += mem + " is not a valid help topic.\n"
        continue

      lines = f.readlines()
      f.close()
      data += (string.join(lines, "") + "\n")

  exported.write_message(data)


def highlight_cmd(session, words, input):
  """#highlight [<item> <color>]

  With no arguments, lists all the highlights currently set.
  With arguments, sets a new highlight.
  """
  if len(words) == 1:
    data = session.getManager("highlight").getInfo()
    if data == '':
      data = "highlight: no highlights defined."

    exported.write_message(data)
    return

  if len(words) == 2:
    data = session.getManager("highlight").getInfo(words[1])
    if data == '':
      data = "highlight: no highlights defined."

    exported.write_message(data)
    return 

  try:
    # knock off the first word which is the command
    inputadjusted = input.split(' ', 1)[1]

    # split it into parts
    (a, b) = utils.split_braced(inputadjusted)

    session.getManager("highlight").addHighlight(a, b)
    exported.write_message("highlight: '" + b + 
                                 "' with style " + a + ".")
  except:
    exported.write_error("highlight: cannot be set.")
    traceback.print_exc()


def info_cmd(session, words, input):
  """#info

  This asks the session about its info.  Commands and such.
  """
  exported.write_message(session.getInfo())


def killall_cmd(session, words, input):
  """#killall

  Wipes all the sessions of all information.
  """
  for mem in engine.myengine._sessions.values():
    mem.clear()
    exported.write_message("killall: session " + 
                                 mem.getName() + " cleared.")


def log_cmd(session, words, input):
  """#log <filename>

  Starts or stops logging to a logfile.
  """
  if len(words) == 1:
    exported.write_error("syntax: #logfile <filename>")
    return


  if session.getLogfile() != None:
    try:
      exported.write_message("log: stopping logging to '" + 
                                   session.getLogfileName() + 
                                   "'.")
      session.closeLogfile()
    except:
      exported.write_error("log: logfile cannot be closed.")

  else:
    try:
      session.openLogfile(words[1])
      exported.write_message("log: starting logging to '" + 
                                   session.getLogfileName() + 
                                   "'.")
    except:
      exported.write_error("log: logfile cannot be opened for apending.")

         
def mudecho_cmd(session, words, input):
  """#echo <on|off>

  Sometimes muds screw up the detail and don't properly turn echo
  on and off.  Sometimes you just want to be able to turn it on
  and off on your own.  So this allows you to do that.
  """
  import event
  if len(words) == 1:
    exported.write_error("syntax: #echo <on|off>")
    return

  if words[1] == "on":
    event.EchoEvent(1).enqueue() 
    exported.write_message("echo: turned on manually.")
  elif words[1] == "off":
    event.EchoEvent(0).enqueue() 
    exported.write_message("echo: turned off manually.")
  else:
    exported.write_error("syntax: #echo <on|off>")

 
def nop_cmd(session, words, input):
  """#nop <whatever you want to write here....>

  nop stands for "no operation".  So anything after a #nop
  and before a ; (unless it's braced) will be ignored.

  This was quite possibly the easiest command to program.
  """
  return


def read_cmd(session, words, input):
  """#read <filename>

  Reads in a commands file and executes all the lines.
  """
  if len(words) == 1:
    exported.write_error("syntax: #read <filename>")
    return

  try:
    file = open(words[1], "r")
    contents = file.readlines()

    # FIXME - this doesn't account for bad first characters....
    try:
      session.handleUserData("#char " + contents[0][0])
    except:
      pass

    for mem in contents:
      mem = mem.strip()
      session.handleUserData(mem)
    exported.write_message("read: file " + words[1] + " read.")

  except IOError:
    exported.write_error("read: file " + words[1] + " is not readable.")
    return


def session_cmd(session, words, input):
  """#session <sessionname> <host> <port>

  The first argument is the session name.
  The second argument is the hostname/ip address to connect to.
  The third argument is the port number.
  """
  if len(words) == 1:
    data = "Sessions available:\n"
    for mem in engine.myengine.getSessions():
      s = engine.myengine.getSession(mem)
      data = data + "   " + s.getName() + ": " + repr(s._socket) + "\n"
    exported.write_message(data[:-1])
    return

  if len(words) < 4:
    exported.write_error("syntax: #session <sesname> <host> <port>")
    return

  sessionname = words[1]

  if INT_REGEXP.match(sessionname):
    exported.write_error("session: session names cannot be all numbers.")
    return

  host = words[2]
  try:
    port = int(words[3])
  except:
    exported.write_error("session: port must be a number: " + words[3])
    return

  # we do this to deal with non-unique session names
  # it's lame, but whatever
  count = 0
  test = sessionname
  while not engine.myengine.isUniqueSessionName(test):
    test = sessionname + repr(count)
    count = count + 1

  sessionname = test
  sock = None
  ses = None

  try:
    # connect to the mud...
    sock = net.SocketCommunicator()
    sock.connect(host, port, sessionname)

  except:
    # close/shutdown the socket if there is no session
    try:
      sock.shutdown()
    except:
      pass

    exported.write_error("session: unable to connect.")
    return

  try:
    # create a session for it...
    ses = engine.myengine.createSession()
    ses.setName(sessionname)
    ses.setSocketCommunicator(sock)
    sock.setSession(ses)
    engine.myengine.registerSession(ses, sessionname)
    engine.myengine.changeSession(sessionname)

    # start the network thread
    engine.myengine.startthread("network", sock.run)

  except:
    traceback.print_exc()
    try: 
      engine.myengine.unregisterSession(sessionname)
      engine.myengine.closeSession(sessionname)
    except:
      pass

    exported.write_error("session: had problems creating the session.")


def showme_cmd(session, words, input):
  """#showme <message>

  Prints stuff to the user display.
  """
  if len(words) > 1:
    exported.write_message(string.join(words[1:]))
  else:
    exported.write_error("syntax: #showme <message>")
     

def speedwalk_cmd(session, words, input):
  """#speedwalk [on|off]

  With no arguments, tells you whether speedwalk is enabled.
  With arguments, sets the speedwalk global variable.
  """
  if len(words) == 1:
    if lyntin.speedwalk:
      exported.write_message("speedwalk: enabled.")
    else:
      exported.write_message("speedwalk: disabled.")
    return

  if words[1] == '1' or words[1] == 'on':
    lyntin.speedwalk = 1
    exported.write_message("speedwalk: now enabled.")
  elif words[1] == '0' or words[1] == 'off':
    lyntin.speedwalk = 0
    exported.write_message("speedwalk: now disabled.")
  else:
    exported.write_error("syntax: #speedwalk [on|off]")


def substitute_cmd(session, words, input):
  """#substitue [<item> <substitution>]

  With no arguments, lists all the substitutions currently set.
  With arguments, sets a new substitution.
  """
  if len(words) == 1:
    data = session.getManager("substitute").getInfo()
    if data == '':
      data = "substitute: no substitutes defined."

    exported.write_message(data)
    return

  if len(words) == 2:
    data = session.getManager("substitute").getInfo(words[1])
    if data == '':
      data = "substitute: no substitutes defined."

    exported.write_message(data)
    return 

  try:
    # knock off the first word which is the command
    inputadjusted = input.split(' ', 1)[1]

    # split it into parts
    (a, b) = utils.split_braced(inputadjusted)

    session.getManager("substitute").addSubstitute(a, b)
    exported.write_message("substitute: " + a + " -> '" + b + "'")
  except:
    exported.write_error("substitute: cannot be set.")
    traceback.print_exc()


def textin_cmd(session, words, input):
  """#textin <filename>

  Takes the contents of the file and outputs it directly to the mud
  without processing it (like #read does).
  """
  if len(words) == 1:
    exported.write_error("syntax: #textin <filename>")
    return
   
  try:
    file = open(words[1], "r")
    contents = file.readlines()
    for mem in contents:
      mem = mem.strip()
      session.getSocketCommunicator().write(mem + "\n")
    exported.write_message("textin: file " + words[1] + 
                                   " read and sent to client.")

  except IOError:
    exported.write_error("textin: file " + words[1] + 
                                 " is not readable.")
  except:
    exported.write_error("textin: exception thrown.")


def tick_cmd(session, words, input):
  """#tick

  Displays the # of seconds left before the ticker for this
  session ticks.
  """
  currenttick = engine.myengine.getCurrentTick()
  tick = session.getTicker().getTickLen()
  exported.write_message("tick: next tick in " + 
                  repr(currenttick % tick) + " seconds.")


def tickon_cmd(session, words, input):
  """#tickon

  Turns on the ticker.
  """
  session.getTicker().enableTicker()
  exported.write_message("tickon: session " + session.getName() + 
                               " ticker enabled.")


def tickoff_cmd(session, words, input):
  """#tickoff

  Turns off the ticker.
  """
  session.getTicker().disableTicker()
  exported.write_message("tickoff: session " + session.getName() + 
                               " ticker disabled.")


def ticksize_cmd(session, words, input):
  """#ticksize {number}

  Sets the tick length.
  """
  if len(words) < 2:
    exported.write_error("syntax: #ticksize {number}")
    return

  try:
    ticklength = int(words[1])
  except:
    exported.write_error("syntax: #ticksize {number}")
    return

  session.getTicker().setTickLen(ticklength)
  exported.write_message("ticksize: tick length set to " + 
                               words[1] + ".")


def unsomething_cmd(session, words, input):
  """#un(gag|substitute|variable|action|alias) <text>

  Allows you to remove gags|substitutes|variables|actions|aliases
  from whatever manager is handling that thing.  This function
  handles all these commands.
  """
  if len(words) == 1:
    exported.write_error("syntax: #" + words[0] + " <text>")
    return

  removedthings = []
  singular = ''
  plural = ''

  text = input.split(' ', 1)[1]   
  if "unaction".find(words[0]) == 0:
    removedthings = session.getManager("action").removeActions(text)
    singular = "action"
    plural = "actions"
  elif "unalias".find(words[0]) == 0:
    removedthings = session.getManager("alias").removeAliases(text)
    singular = "alias"
    plural = "aliases"
  elif "ungag".find(words[0]) == 0:
    removedthings = session.getManager("gag").removeGags(text)
    singular = "gag"
    plural = "gags"
  elif "unhighlight".find(words[0]) == 0:
    removedthings = session.getManager("highlight").removeHighlights(text)
    singular = "highlight"
    plural = "highlights"
  elif "unsubstitute".find(words[0]) == 0:
    removedthings = session.getManager("substitute").removeSubstitutes(text)
    singular = "substitute"
    plural = "substitutes"
  elif "unvariable".find(words[0]) == 0:
    removedthings = session.getManager("variable").removeVariables(text)
    singular = "variable"
    plural = "variables"
      

  if len(removedthings) == 0:
    exported.write_message("un" + singular + 
                                 ": No " + plural + " removed.")
    return

  data = ''
  for mem in removedthings:
    if type(mem) == type( (1,2) ):
      data += singular + " {" + mem[0] + "} {" + mem[1] + "} removed.\n"
    else:
      data += singular + " '" + mem + "' removed.\n"

  exported.write_message(data[:-1])


def variable_cmd(session, words, input):
  """#variable [<var> <expansion>]

  With no arguments, lists all the variables currently set.
  With arguments, sets a new variable.
  """
  if len(words) == 1:
    data = session.getManager("variable").getInfo()
    if data == '':
      data = "variable: no variables defined."

    exported.write_message(data)
    return

  if len(words) == 2:
    data = session.getManager("variable").getInfo(words[1])
    if data == '':
      data = "variable: no variables defined."

    exported.write_message(data)
    return 

  try:
    # knock off the first word which is the command
    inputadjusted = input.split(' ', 1)[1]

    # split it into parts
    (a, b) = utils.split_braced(inputadjusted)

    session.getManager("variable").addVariable(a, b)
    exported.write_message("variable: " + a + " -> '" + b + "'")
  except:
    exported.write_error("variable: cannot be set.")
    traceback.print_exc()


def version_cmd(session, words, input):
  """#version

  Prints out the version number, date, copyright info, and
  some other garbage to the user.
  """
  exported.write_message(lyntin.VERSION)


def wizlist_cmd(session, words, input):
  """#wizlist

  Lists all the contributors to Lyntin over the years.
  """
  exported.write_message(lyntin.WIZLIST)


def write_cmd(session, words, input):
  """#write <filename>

  Queries the sessions and the lyntin globals for stuff
  and writes it out to a file for persistence.
  """
  if len(words) == 1:
    exported.write_message("syntax: #write <filename>")
    return

  try:
    f = open(words[1], "w")
    f.write(session.getWriteFileInfo())
    f.close()
    exported.write_message("write: file " + 
                                 words[1] + " has been written.")
  except:
    exported.write_error("write: error writing to file " + 
                                 words[1] + ".")
    traceback.print_exc()


def zap_cmd(session, words, input):
  """#zap

  This closes a session and should close the socket and cause
  the SocketCommunicator to garbage collect.
  """
  if engine.myengine.closeSession(session):
    exported.write_message("zap: session " + 
                                 session.getName() + 
                                 " zapped!")
  else:
    exported.write_message("zap: session cannot be zapped!")


def load():
  """ Initializes the module by binding all the commands."""
  engine.myengine.addCommand("^clear", clear_cmd)
  engine.myengine.addCommand("ansi", ansi_cmd)
  engine.myengine.addCommand("action", action_cmd)
  engine.myengine.addCommand("alias", alias_cmd)
  # engine.myengine.addCommand("antisubstitute", antisubstitute_cmd)
  # engine.myengine.addCommand("bell", bell_cmd)
  engine.myengine.addCommand("boss", boss_cmd)
  engine.myengine.addCommand("^char", char_cmd)
  engine.myengine.addCommand("^cr", cr_cmd)
  # engine.myengine.addCommand("datagrep", datagrep_cmd)
  # engine.myengine.addCommand("datagreplines", datagreplines_cmd)
  engine.myengine.addCommand("diagnostics", diagnostics_cmd)
  # engine.myengine.addCommand("echo", echo_cmd)
  engine.myengine.addCommand("^end", end_cmd)
  engine.myengine.addCommand("gag", gag_cmd)
  engine.myengine.addCommand("help", help_cmd)
  engine.myengine.addCommand("highlight", highlight_cmd)
  # engine.myengine.addCommand("history", history_cmd)
  # engine.myengine.addCommand("ignore", ignore_cmd)
  # engine.myengine.addCommand("import", import_cmd)
  engine.myengine.addCommand("info", info_cmd)
  engine.myengine.addCommand("killall", killall_cmd)
  engine.myengine.addCommand("log", log_cmd)
  # engine.myengine.addCommand("loop", loop_cmd)
  # engine.myengine.addCommand("map", map_cmd)
  # engine.myengine.addCommand("mark", mark_cmd)
  # engine.myengine.addCommand("message", message_cmd)
  engine.myengine.addCommand("mudecho", mudecho_cmd)
  engine.myengine.addCommand("nop", nop_cmd)
  # engine.myengine.addCommand("path", path_cmd)
  # engine.myengine.addCommand("pathdir", pathdir_cmd)
  # engine.myengine.addCommand("presub", presub_cmd)
  engine.myengine.addCommand("read", read_cmd)
  # engine.myengine.addCommand("redraw", redraw_cmd)
  # engine.myengine.addCommand("return", return_cmd)
  # engine.myengine.addCommand("report", report_cmd)
  # engine.myengine.addCommand("savepath", savepath_cmd)
  engine.myengine.addCommand("session", session_cmd)
  engine.myengine.addCommand("showme", showme_cmd)
  # engine.myengine.addCommand("snoop", snoop_cmd)
  engine.myengine.addCommand("speedwalk", speedwalk_cmd)
  engine.myengine.addCommand("substitute", substitute_cmd)
  # engine.myengine.addCommand("tabadd", tabadd_cmd)
  # engine.myengine.addCommand("tabdelete", tabdelete_cmd)
  # engine.myengine.addCommand("tablist", tablist_cmd)
  engine.myengine.addCommand("textin", textin_cmd)
  engine.myengine.addCommand("tick", tick_cmd)
  engine.myengine.addCommand("tickon", tickon_cmd)
  engine.myengine.addCommand("tickoff", tickoff_cmd)
  engine.myengine.addCommand("ticksize", ticksize_cmd)
  # engine.myengine.addCommand("togglesub", togglesub_cmd)
  engine.myengine.addCommand("unaction", unsomething_cmd)
  engine.myengine.addCommand("unalias", unsomething_cmd)
  # engine.myengine.addCommand("unantisubstitute", unsomething_cmd)
  engine.myengine.addCommand("ungag", unsomething_cmd)
  engine.myengine.addCommand("unhighlight", unsomething_cmd)
  # engine.myengine.addCommand("unpath", unpath_cmd)
  engine.myengine.addCommand("unsubstitute", unsomething_cmd)
  engine.myengine.addCommand("unvariable", unsomething_cmd)
  engine.myengine.addCommand("variable", variable_cmd)
  engine.myengine.addCommand("version", version_cmd)
  # engine.myengine.addCommand("verbatim", verbatim_cmd)
  engine.myengine.addCommand("wizlist", wizlist_cmd)
  engine.myengine.addCommand("write", write_cmd)
  engine.myengine.addCommand("zap", zap_cmd)
