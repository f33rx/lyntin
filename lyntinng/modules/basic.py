#######################################################################
# This file is part of Lyntin
# copyright (c) Will Guaraldi 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: basic.py,v 1.37 2002/03/22 02:42:49 willhelm Exp $
#######################################################################
import string, traceback
import net, utils, engine, lyntin, exported

"""
This module holds a series of basic commands.
"""

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
    filter = utils.strip_braces(words[1])
    data = session.getManager("action").getInfo(filter)
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
    exported.write_message("action: {%s} -> {%s} added." % (a, b))
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
    filter = utils.strip_braces(words[1])
    data = session.getManager("alias").getInfo(filter)
    if data == '':
      data = "alias: no aliases defined."

    exported.write_message(data)
    return

  try:
    # knock off the first word which is the command
    # and split it into parts
    (a, b) = utils.split_braced(input.split(' ', 1)[1])

    session.getManager("alias").addAlias(a, b)
    exported.write_message("alias: {%s} -> {%s} added." % (a,b))
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

  option = utils.strip_braces(words[1])

  if option == '1' or option == 'on':
    lyntin.ansicolor = 1
    exported.write_message("ansi: ansi is now enabled.")
  elif option == '0' or option == 'off':
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

  newchar = utils.strip_braces(words[1])

  lyntin.commandchar = newchar
  exported.write_message("char: new command character is " + 
                               lyntin.commandchar + ".")


def clear_cmd(session, words, input):
  """#clear

  This command clears a session of all session data (except
  the actual connection).
  """
  try:
    session.clear()
    exported.write_message("clear: session %s cleared." % session.getName())
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
      filename = utils.strip_braces(words[1])
      f = open(words[1], "w")
      f.write("This file was created on: " + time.ctime(time.time()) + 
              "\n\n")
      f.write(message)
      f.close()
    except:
      exported.write_error("diagnostics: Error writing to file %s." % words[1])
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

  # note: this one might be a problem if they try to gag } { in 
  # the text.  the solution is for them to place the text in
  # braces.
  gaggedtext = utils.strip_braces(input.split(' ', 1)[1])

  session.getManager("gag").addGag(gaggedtext)
  exported.write_message("gag: '%s' added." % gaggedtext)


def help_cmd(session, words, input):
  """#help [topic|command]

  This is the main help command for Lyntin.
  """
  import dircache

  helpdir = lyntin.lyntindir + "help"
  data = "::lyntin help::\n"

  if len(words) == 1:
    file_list = dircache.listdir(helpdir)
    file_list.sort()

    topic_list = []
    command_list = []

    for mem in file_list:
      if len(mem) < 5:
        continue

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

  helpfiles = dircache.listdir(helpdir + "/")

  for mem in words[1:]:
    mem = utils.strip_braces(mem)

    if mem + ".tpc" in helpfiles:
      f = open(helpdir + "/" + mem + ".tpc", "r")
    elif mem + ".cmd" in helpfiles:
      f = open(helpdir + "/" + mem + ".cmd", "r")
    else:
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
    filter = utils.strip_braces(words[1])
    data = session.getManager("highlight").getInfo(filter)
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
    exported.write_message("highlight: '%s' with style '%s'." % (b, a))

  except:
    exported.write_error("highlight: cannot be set.")
    traceback.print_exc()


def history_cmd(session, words, input):
  """#history

  Prints the history list.
  """
  historylist = exported.get_history()
  for i in range(0, len(historylist)):
    historylist[i] = repr(i) + " " + historylist[i]
  historylist.reverse()
  exported.write_message("History:\n" + string.join(historylist, "\n"))


def if_cmd(session, words, input):
  """#if <expr> <action>

  Implements the Tintin++ #if command.
  """
  # 3/18/2002: originally implemented by Sebastian John
  # 3/20/2002: mildly editied by Will Guaraldi
  if len(words) < 3:
    exported.write_error("syntax: #if {<expr>} {<action>}")
    return

  inputadjusted = input.split(" ", 1)[1]
  expr, action = utils.split_braced(inputadjusted)

  expr = expr.replace(" && ", " and ")
  expr = expr.replace(" || ", " or ")

  try:
    if eval(expr):
      engine.myengine.handleUserData(action)
  except SyntaxError:
    exported.write_error("if: invalid syntax / syntax error.")
  except Exception, e:
    exported.write_error("if: exception: %s" % e)


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
    exported.write_message("killall: session %s cleared." % mem.getName())


def log_cmd(session, words, input):
  """#log <filename>

  Starts or stops logging to a logfile.
  """
  if len(words) == 1:
    exported.write_error("syntax: #logfile <filename>")
    return


  if session.getLogfile() != None:
    try:
      exported.write_message("log: stopping logging to '%s'." % 
                             session.getLogfileName())
      session.closeLogfile()
    except:
      exported.write_error("log: logfile cannot be closed.")

  else:
    try:
      filename = utils.strip_braces(words[1])
      session.openLogfile(filename)
      exported.write_message("log: starting logging to '%s'." % 
                             session.getLogfileName())
    except:
      exported.write_error("log: logfile cannot be opened for apending.")

         
def loop_cmd(session, words, input):
  """#loop {<from>,<to>} {command}

  Implements the loop command (which is more like a range).
  """
  import event
  if len(words) < 3:
    exported.write_error("syntax: #loop {<from>,<to>} {command}")
    return

  try:
    # knock off the first word which is the command
    inputadjusted = input.split(' ', 1)[1]

    # split it into parts
    (looprange, command) = utils.split_braced(inputadjusted)
    looprange = looprange.split(',')

    if len(looprange) != 2:    
      exported.write_error("syntax: #loop {<from>,<to>} {command}")
      return

    # remove trailing and leading whitespace and convert to ints
    # so we can use them in a range function
    ifrom = int(looprange[0].strip())
    ito = int(looprange[1].strip())

    # we need to handle backwards and forwards using the step
    # and need to adjust ito so the range is correctly bounded.
    if ifrom > ito:
      step = -1
    else:
      step = 1

    if ito > 0:
      ito = ito + step
    else:
      ito = ito - step

    for i in range(ifrom, ito, step):
      loopcommand = command.replace("%0", repr(i))
      event.InputEvent(input=loopcommand, internal=1).enqueue()

  except:
    exported.write_error("loop: error in the loop.")
    traceback.print_exc()


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

  option = utils.strip_braced(words[1])

  if option == "on":
    event.EchoEvent(1).enqueue() 
    exported.write_message("echo: turned on manually.")
  elif option == "off":
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
    filename = utils.strip_braces(words[1])

    # 3/17/2002 http:// handling written by Sebastian John
    # 3/18/2002 edited by Will
    if filename.find("http://") == 0:
      url = filename[7:]
      if url.find("/") == -1:
        exported.write_error("read: malformed url.")
        return

      try:
        import httplib
      except:
        exported.write_error("read: cannot import httplib.")
        return
        
      host, resource = url.split("/", 1)
      resource = "/" + resource
      
      sock = httplib.HTTP()
      sock.connect(host)   
      sock.putrequest("GET", resource)
      sock.endheaders()
      status, reason, headers = sock.getreply()
      
      if status != 200:
        exported.write_error("read: http error: %d %s" % (status, reason))
        return
      
      file = sock.getfile()
    
    else:
      file = open(filename, "r")
    
    contents = file.readlines()

    # FIXME - this doesn't account for bad first characters....
    try:
      session.handleUserData("#char " + contents[0][0])
    except:
      pass

    for mem in contents:
      mem = mem.strip()
      session.handleUserData(mem)
    exported.write_message("read: file " + filename + " read.")

  except IOError:
    exported.write_error("read: file " + filename + " is not readable.")
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

  inputadjusted = input.split(' ', 1)[1]
  sessionname, b = utils.split_braced(inputadjusted)
  host, port = b.split(" ")

  if port.isdigit():
    port = int(port)
  else:
    exported.write_error("session: port must be a number.")
    return
  
  if sessionname.isdigit():
    exported.write_error("session: session names cannot be all numbers.")
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
    # create a SocketCommunicator
    sock = net.SocketCommunicator()

    # create a session for it...
    ses = engine.myengine.createSession()
    ses.setName(sessionname)
    ses.setSocketCommunicator(sock)
    sock.setSession(ses)
    engine.myengine.registerSession(ses, sessionname)
    engine.myengine.changeSession(sessionname)

    # connect to the mud...
    sock.connect(host, port, sessionname)

    # start the network thread
    engine.myengine.startthread("network", sock.run)

  except:
    traceback.print_exc()
    try: 
      engine.myengine.unregisterSession(sessionname)
      engine.myengine.closeSession(sessionname)
      sock.shutdown()
    except:
      pass
    exported.write_error("session: unable to connect.")
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

  option = utils.strip_braces(words[1])

  if option == '1' or option == 'on':
    lyntin.speedwalk = 1
    exported.write_message("speedwalk: now enabled.")
  elif option == '0' or option == 'off':
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
    filter = utils.strip_braces(words[1])
    data = session.getManager("substitute").getInfo(filter)
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
    filename = utils.strip_braces(words[1])
    file = open(filename, "r")
    contents = file.readlines()
    for mem in contents:
      mem = mem.strip()
      session.getSocketCommunicator().write(mem + "\n")
    exported.write_message("textin: file " + filename + 
                                   " read and sent to client.")

  except IOError:
    exported.write_error("textin: file " + filename + 
                                 " is not readable.")
  except:
    exported.write_error("textin: exception thrown.")


def tick_cmd(session, words, input):
  """#tick

  Displays the # of seconds left before the ticker for this
  session ticks.
  """
  if session.getTicker().isEnabled():
    currenttick = engine.myengine.getCurrentTick()
    ticklen = session.getTicker().getTickLen()
    tickstart = session.getTicker().getTickStart()
    nexttick = repr(ticklen - ((currenttick - tickstart) % ticklen))
    exported.write_message("tick: next tick in " + nexttick + " seconds.")
  else:
    exported.write_message("tick: ticker is not enabled.")


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

  ticklength = utils.strip_braces(words[1])
  if ticklength.isdigit():
    ticklength = int(ticklength)
  else:
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

  text = utils.strip_braces(input.split(' ', 1)[1])
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
    filter = utils.strip_braces(words[1])
    data = session.getManager("variable").getInfo(filter)
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
    filename = utils.strip_braces(words[1])
    f = open(filename, "w")
    f.write(session.getWriteFileInfo())
    f.close()
    exported.write_message("write: file " + filename +
                                 " has been written.")
  except:
    exported.write_error("write: error writing to file " + 
                                 filename + ".")
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
  exported.add_command("^clear", clear_cmd)
  exported.add_command("ansi", ansi_cmd)
  exported.add_command("action", action_cmd)
  exported.add_command("alias", alias_cmd)
  # exported.add_command("antisubstitute", antisubstitute_cmd)
  # exported.add_command("bell", bell_cmd)
  exported.add_command("boss", boss_cmd)
  exported.add_command("^char", char_cmd)
  exported.add_command("^cr", cr_cmd)
  # exported.add_command("datagrep", datagrep_cmd)
  # exported.add_command("datagreplines", datagreplines_cmd)
  exported.add_command("diagnostics", diagnostics_cmd)
  # exported.add_command("echo", echo_cmd)
  exported.add_command("^end", end_cmd)
  exported.add_command("gag", gag_cmd)
  exported.add_command("help", help_cmd)
  exported.add_command("highlight", highlight_cmd)
  exported.add_command("history", history_cmd)
  exported.add_command("if", if_cmd)
  # exported.add_command("ignore", ignore_cmd)
  # exported.add_command("import", import_cmd)
  exported.add_command("info", info_cmd)
  exported.add_command("killall", killall_cmd)
  exported.add_command("log", log_cmd)
  exported.add_command("loop", loop_cmd)
  # exported.add_command("map", map_cmd)
  # exported.add_command("mark", mark_cmd)
  # exported.add_command("message", message_cmd)
  exported.add_command("mudecho", mudecho_cmd)
  exported.add_command("nop", nop_cmd)
  # exported.add_command("path", path_cmd)
  # exported.add_command("pathdir", pathdir_cmd)
  # exported.add_command("presub", presub_cmd)
  exported.add_command("read", read_cmd)
  # exported.add_command("redraw", redraw_cmd)
  # exported.add_command("return", return_cmd)
  # exported.add_command("report", report_cmd)
  # exported.add_command("savepath", savepath_cmd)
  exported.add_command("session", session_cmd)
  exported.add_command("showme", showme_cmd)
  # exported.add_command("snoop", snoop_cmd)
  exported.add_command("speedwalk", speedwalk_cmd)
  exported.add_command("substitute", substitute_cmd)
  # exported.add_command("tabadd", tabadd_cmd)
  # exported.add_command("tabdelete", tabdelete_cmd)
  # exported.add_command("tablist", tablist_cmd)
  exported.add_command("textin", textin_cmd)
  exported.add_command("tick", tick_cmd)
  exported.add_command("tickon", tickon_cmd)
  exported.add_command("tickoff", tickoff_cmd)
  exported.add_command("ticksize", ticksize_cmd)
  # exported.add_command("togglesub", togglesub_cmd)
  exported.add_command("unaction", unsomething_cmd)
  exported.add_command("unalias", unsomething_cmd)
  # exported.add_command("unantisubstitute", unsomething_cmd)
  exported.add_command("ungag", unsomething_cmd)
  exported.add_command("unhighlight", unsomething_cmd)
  # exported.add_command("unpath", unpath_cmd)
  exported.add_command("unsubstitute", unsomething_cmd)
  exported.add_command("unvariable", unsomething_cmd)
  exported.add_command("variable", variable_cmd)
  exported.add_command("version", version_cmd)
  # exported.add_command("verbatim", verbatim_cmd)
  exported.add_command("wizlist", wizlist_cmd)
  exported.add_command("write", write_cmd)
  exported.add_command("zap", zap_cmd)
