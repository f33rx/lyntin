#######################################################################
# This file is part of Lyntin
# copyright (c) Will Guaraldi 2001
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: basic.py,v 1.9 2002/01/20 07:21:02 willhelm Exp $
#######################################################################
import re, string, traceback
import net, utils, engine, lyntin

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
    data = session.getActionManager().getActionInfo()
    if data == '':
      data = "action: no actions defined."

    engine.myengine.writeMessage(data)
    return

  # they typed '#action dd*' and are looking for matching actions
  if len(words) == 2:
    data = session.getActionManager().getActionInfo(words[1])
    if data == '':
      data = "action: no actions defined."

    engine.myengine.writeMessage(data)
    return

  try:
    # knock off the first word which is the command
    inputadjusted = input.split(' ', 1)[1]

    # split it into parts
    (a, b) = utils.split_braced(inputadjusted)

    session.getActionManager().addAction(a, b)
    engine.myengine.writeMessage("action: {" + a + "} -> {" + b + "} added.")
  except:
    engine.myengine.writeError("action: cannot be added.")
    traceback.print_exc()


def alias_cmd(session, words, input):
  """#alias [<alias> <expansion>]

  This adds aliases and tells you the current alias stati of aliases
  already registered.
  """
  # they typed '#alias'--print out all current aliases
  if len(words) == 1:
    data = session.getAliasManager().getAliasInfo()
    if data == '':
      data = "alias: no aliases defined."

    engine.myengine.writeMessage(data)
    return

  # they typed '#alias dd*' and are looking for matching aliases
  if len(words) == 2:
    data = session.getAliasManager().getAliasInfo(words[1])
    if data == '':
      data = "alias: no aliases defined."

    engine.myengine.writeMessage(data)
    return

  try:
    # knock off the first word which is the command
    inputadjusted = input.split(' ', 1)[1]

    # split it into parts
    (a, b) = utils.split_braced(inputadjusted)

    session.getAliasManager().addAlias(a, b)
    engine.myengine.writeMessage("alias: {" + a + "} -> {" + b + "} added.")
  except:
    engine.myengine.writeError("alias: cannot be added.")
    traceback.print_exc()


def ansi_cmd(session, words, input):
  """#ansi [on|off]

  With no arguments, tells you whether ansicolor is enabled.
  With arguments, sets the ansicolor global variable.
  """
  if len(words) == 1:
    if lyntin.ansicolor:
      engine.myengine.writeMessage("ansi: ansi color is enabled.")
    else:
      engine.myengine.writeMessage("ansi: ansi color is disabled.")
    return

  if words[1] == '1' or words[1] == 'on':
    lyntin.ansicolor = 1
    engine.myengine.writeMessage("ansi: ansi is now enabled.")
  elif words[1] == '0' or words[1] == 'off':
    lyntin.ansicolor = 0
    engine.myengine.writeMessage("ansi: ansi is now disabled.")
  else:
    engine.myengine.writeError("syntax: #ansi [on|off]")


def boss_cmd(session, words, input):
  """#boss

  This command prints stuff to the screen that looks important.
  Oddly enough, it's actually linked list code.
  """
  # FIXME - somehow make this more universal by having a bossfile?
  engine.myengine.writeMudData(lyntin.BOSSTEXT)


def char_cmd(session, words, input):
  """#char <new-command-denoting-character>

  With no arguments, tells you what the current command character
  is.  With arguments allows you to set the global command
  character.
  """
  if len(words) == 1:
    engine.myengine.writeMessage("char: current command character is " + 
                                 lyntin.commandchar + ".")
    return

  lyntin.commandchar = words[1]
  engine.myengine.writeMessage("char: new command character is " + 
                               lyntin.commandchar + ".")


def clear_cmd(session, words, input):
  """#clear

  This command clears a session of all session data (except
  the actual connection).
  """
  try:
    session.clear()
    engine.myengine.writeMessage("clear: session " + 
                                 session.getName() + " cleared.")
  except:
    engine.myengine.writeError("clear: error in clearing session.")

  
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
 
  engine.myengine.writeMessage(message)
  engine.myengine.writeMessage("This information can be dumped to a "
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
      engine.myengine.writeError("Error writing to file " + words[1] + ".")
      traceback.print_exc()


def end_cmd(session, words, input):
  """#end

  This is the end command--it shuts down Lyntin.
  """
  import event
  engine.myengine.writeMessage("end: you'll be back...")
  event.ShutdownEvent().enqueue()


def gag_cmd(session, words, input):
  """#gag [<text>]

  With no arguments, it tells you all the gags currently existing.
  With arguments, it sets up a new gag.
  """
  if len(words) == 1:
    data = session.getGagManager().getGagInfo()
    if data == '':
      data = "gag: no gags defined."

    engine.myengine.writeMessage(data)
    return

  gaggedtext = utils.strip_braces(input.split(' ', 1)[1])
  session.getGagManager().addGag(gaggedtext)
  engine.myengine.writeMessage("gag: '" + gaggedtext + "' added.")


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

    engine.myengine.writeMessage(data)
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

  engine.myengine.writeMessage(data)


def highlight_cmd(session, words, input):
  """#highlight [<item> <color>]

  With no arguments, lists all the highlights currently set.
  With arguments, sets a new highlight.
  """
  if len(words) == 1:
    data = session.getHighlightManager().getHighlightInfo()
    if data == '':
      data = "highlight: no highlights defined."

    engine.myengine.writeMessage(data)
    return

  if len(words) == 2:
    data = session.getHighlightManager().getHighlightInfo(words[1])
    if data == '':
      data = "highlight: no highlights defined."

    engine.myengine.writeMessage(data)
    return 

  try:
    # knock off the first word which is the command
    inputadjusted = input.split(' ', 1)[1]

    # split it into parts
    (a, b) = utils.split_braced(inputadjusted)

    session.getHighlightManager().addHighlight(a, b)
    engine.myengine.writeMessage("highlight: '" + b + 
                                 "' with style " + a + ".")
  except:
    engine.myengine.writeError("highlight: cannot be set.")
    traceback.print_exc()


def info_cmd(session, words, input):
  """#info

  This asks the session about its info.  Commands and such.
  """
  engine.myengine.writeMessage(session.getInfo())


def killall_cmd(session, words, input):
  """#killall

  Wipes all the sessions of all information.
  """
  for mem in engine.myengine._sessions.values():
    mem.clear()
    engine.myengine.writeMessage("killall: session " + 
                                 mem.getName() + " cleared.")


def log_cmd(session, words, input):
  """#log <filename>

  Starts or stops logging to a logfile.
  """
  if len(words) == 1:
    engine.myengine.writeError("syntax: #logfile <filename>")
    return


  if session._logfile != None:
    session._logfile.close()
    session._logfile = None
    engine.myengine.writeMessage("log: logging to '" + 
                                 session._logfile.name + 
                                 "' stopped.")
    return

  try:
    session._logfile = open(words[1], "a")
    engine.myengine.writeMessage("log: logging to '" + 
                                 session._logfile.name + 
                                 "'.")
  except:
    session._logfile = None
    engine.myengine.writeError("log: logfile cannot be opened for apending.")

         
def mudecho_cmd(session, words, input):
  """#echo <on|off>

  Sometimes muds screw up the detail and don't properly turn echo
  on and off.  Sometimes you just want to be able to turn it on
  and off on your own.  So this allows you to do that.
  """
  import event
  if len(words) == 1:
    engine.myengine.writeError("syntax: #echo <on|off>")
    return

  if words[1] == "on":
    event.EchoEvent(1).enqueue() 
    engine.myengine.writeMessage("echo: turned on manually.")
  elif words[1] == "off":
    event.EchoEvent(0).enqueue() 
    engine.myengine.writeMessage("echo: turned off manually.")
  else:
    engine.myengine.writeError("syntax: #echo <on|off>")

 
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
    engine.myengine.writeError("syntax: #read <filename>")
    return

  try:
    file = open(words[1], "r")
    contents = file.readlines()
    for mem in contents:
      mem = mem.strip()
      session.handleUserData(mem)
    engine.myengine.writeMessage("read: file " + words[1] + " read.")

  except IOError:
    engine.myengine.writeError("read: file " + words[1] + " is not readable.")
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
    engine.myengine.writeMessage(data[:-1])
    return

  if len(words) < 4:
    engine.myengine.writeError("syntax: #session <sesname> <host> <port>")
    return

  sessionname = words[1]

  if INT_REGEXP.match(sessionname):
    engine.myengine.writeError("session: session names cannot be all numbers.")
    return

  host = words[2]
  try:
    port = int(words[3])
  except:
    engine.myengine.writeError("session: port must be a number: " + words[3])
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

    engine.myengine.writeError("session: unable to connect.")
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

    engine.myengine.writeError("session: had problems creating the session.")


def showme_cmd(session, words, input):
  """#showme <message>

  Prints stuff to the user display.
  """
  if len(words) > 1:
    engine.myengine.writeMessage(string.join(words[1:]))
  else:
    engine.myengine.writeError("syntax: #showme <message>")
     

def speedwalk_cmd(session, words, input):
  """#speedwalk [on|off]

  With no arguments, tells you whether speedwalk is enabled.
  With arguments, sets the speedwalk global variable.
  """
  if len(words) == 1:
    if lyntin.speedwalk:
      engine.myengine.writeMessage("speedwalk: enabled.")
    else:
      engine.myengine.writeMessage("speedwalk: disabled.")
    return

  if words[1] == '1' or words[1] == 'on':
    lyntin.speedwalk = 1
    engine.myengine.writeMessage("speedwalk: now enabled.")
  elif words[1] == '0' or words[1] == 'off':
    lyntin.speedwalk = 0
    engine.myengine.writeMessage("speedwalk: now disabled.")
  else:
    engine.myengine.writeError("syntax: #speedwalk [on|off]")


def substitute_cmd(session, words, input):
  """#substitue [<item> <substitution>]

  With no arguments, lists all the substitutions currently set.
  With arguments, sets a new substitution.
  """
  if len(words) == 1:
    data = session.getSubstituteManager().getSubstituteInfo()
    if data == '':
      data = "substitute: no substitutes defined."

    engine.myengine.writeMessage(data)
    return

  if len(words) == 2:
    data = session.getSubstituteManager().getSubstituteInfo(words[1])
    if data == '':
      data = "substitute: no substitutes defined."

    engine.myengine.writeMessage(data)
    return 

  try:
    # knock off the first word which is the command
    inputadjusted = input.split(' ', 1)[1]

    # split it into parts
    (a, b) = utils.split_braced(inputadjusted)

    session.getSubstituteManager().addSubstitute(a, b)
    engine.myengine.writeMessage("substitute: " + a + " -> '" + b + "'")
  except:
    engine.myengine.writeError("substitute: cannot be set.")
    traceback.print_exc()


def textin_cmd(session, words, input):
  """#textin <filename>

  Takes the contents of the file and outputs it directly to the mud
  without processing it (like #read does).
  """
  if len(words) == 1:
    engine.myengine.writeError("syntax: #textin <filename>")
    return
   
  try:
    file = open(words[1], "r")
    contents = file.readlines()
    for mem in contents:
      mem = mem.strip()
      session.getSocketCommunicator().write(mem + "\n")
    engine.myengine.writeMessage("textin: file " + words[1] + 
                                   " read and sent to client.")

  except IOError:
    engine.myengine.writeError("textin: file " + words[1] + 
                                 " is not readable.")
  except:
    engine.myengine.writeError("textin: exception thrown.")


def tick_cmd(session, words, input):
  """#tick

  Displays the # of seconds left before the ticker for this
  session ticks.
  """
  currenttick = engine.myengine.getCurrentTick()
  tick = session.getTicker().getTickLen()
  engine.myengine.writeMessage("tick: next tick in " + 
                  repr(currenttick % tick) + " seconds.")


def tickon_cmd(session, words, input):
  """#tickon

  Turns on the ticker.
  """
  session.getTicker().enableTicker()
  engine.myengine.writeMessage("tickon: session " + session.getName() + 
                               " ticker enabled.")


def tickoff_cmd(session, words, input):
  """#tickoff

  Turns off the ticker.
  """
  session.getTicker().disableTicker()
  engine.myengine.writeMessage("tickoff: session " + session.getName() + 
                               " ticker disabled.")


def ticksize_cmd(session, words, input):
  """#ticksize {number}

  Sets the tick length.
  """
  if len(words) < 2:
    engine.myengine.writeError("syntax: #ticksize {number}")
    return

  try:
    ticklength = int(words[1])
  except:
    engine.myengine.writeError("syntax: #ticksize {number}")
    return

  session.getTicker().setTickLen(ticklength)
  engine.myengine.writeMessage("ticksize: tick length set to " + 
                               words[1] + ".")


def unsomething_cmd(session, words, input):
  """#un(gag|substitute|variable|action|alias) <text>

  Allows you to remove gags|substitutes|variables|actions|aliases
  from whatever manager is handling that thing.  This function
  handles all these commands.
  """
  if len(words) == 1:
    engine.myengine.writeError("syntax: #" + words[0] + " <text>")
    return

  removedthings = []
  singular = ''
  plural = ''

  text = input.split(' ', 1)[1]   
  if "unaction".find(words[0]) == 0:
    removedthings = session.getActionManager().removeActions(text)
    singular = "action"
    plural = "actions"
  elif "unalias".find(words[0]) == 0:
    removedthings = session.getAliasManager().removeAliases(text)
    singular = "alias"
    plural = "aliases"
  elif "ungag".find(words[0]) == 0:
    removedthings = session.getGagManager().removeGags(text)
    singular = "gag"
    plural = "gags"
  elif "unhighlight".find(words[0]) == 0:
    removedthings = session.getHighlightManager().removeHighlights(text)
    singular = "highlight"
    plural = "highlights"
  elif "unsubstitute".find(words[0]) == 0:
    removedthings = session.getSubstituteManager().removeSubstitutes(text)
    singular = "substitute"
    plural = "substitutes"
  elif "unvariable".find(words[0]) == 0:
    removedthings = session.getVariableManager().removeVariables(text)
    singular = "variable"
    plural = "variables"
      

  if len(removedthings) == 0:
    engine.myengine.writeMessage("un" + singular + 
                                 ": No " + plural + " removed.")
    return

  data = ''
  for mem in removedthings:
    if type(mem) == type( (1,2) ):
      data += singular + " {" + mem[0] + "} {" + mem[1] + "} removed.\n"
    else:
      data += singular + " '" + mem + "' removed.\n"

  engine.myengine.writeMessage(data[:-1])


def variable_cmd(session, words, input):
  """#variable [<var> <expansion>]

  With no arguments, lists all the variables currently set.
  With arguments, sets a new variable.
  """
  if len(words) == 1:
    data = session.getVariableManager().getVariableInfo()
    if data == '':
      data = "variable: no variables defined."

    engine.myengine.writeMessage(data)
    return

  if len(words) == 2:
    data = session.getVariableManager().getVariableInfo(words[1])
    if data == '':
      data = "variable: no variables defined."

    engine.myengine.writeMessage(data)
    return 

  try:
    # knock off the first word which is the command
    inputadjusted = input.split(' ', 1)[1]

    # split it into parts
    (a, b) = utils.split_braced(inputadjusted)

    session.getVariableManager().addVariable(a, b)
    engine.myengine.writeMessage("variable: " + a + " -> '" + b + "'")
  except:
    engine.myengine.writeError("variable: cannot be set.")
    traceback.print_exc()


def version_cmd(session, words, input):
  """#version

  Prints out the version number, date, copyright info, and
  some other garbage to the user.
  """
  engine.myengine.writeMessage(lyntin.VERSION)


def wizlist_cmd(session, words, input):
  """#wizlist

  Lists all the contributors to Lyntin over the years.
  """
  engine.myengine.writeMessage(lyntin.WIZLIST)


def write_cmd(session, words, input):
  """#write <filename>

  Queries the sessions and the lyntin globals for stuff
  and writes it out to a file for persistence.
  """
  if len(words) == 1:
    engine.myengine.writeMessage("syntax: #write <filename>")
    return

  try:
    f = open(words[1], "w")
    f.write(session.getWriteFileInfo())
    f.close()
    engine.myengine.writeMessage("write: file " + 
                                 words[1] + " has been written.")
  except:
    engine.myengine.writeError("write: error writing to file " + 
                                 words[1] + ".")
    traceback.print_exc()


def zap_cmd(session, words, input):
  """#zap

  This closes a session and should close the socket and cause
  the SocketCommunicator to garbage collect.
  """
  if engine.myengine.closeSession(session):
    engine.myengine.writeMessage("zap: session " + 
                                 session.getName() + 
                                 " zapped!")
  else:
    engine.myengine.writeMessage("zap: session cannot be zapped!")


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
