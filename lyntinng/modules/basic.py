#######################################################################
# This file is part of Lyntin
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: basic.py,v 1.71 2002/04/26 02:34:25 jmberne Exp $
#######################################################################
import string, traceback
import net, utils, engine, lyntin, exported, hooks

"""
This module holds a series of basic commands.
"""
commands_dict = {}

def action_cmd(session, args, input):
  """#action [<trigger> <response>]

  This adds actions and tells you the current action stati of actions
  already registered.
  """
  trigger = args["trigger"]
  action = args["action"]
  quiet = args["quiet"]

  # they typed '#action'--print out all the current actions
  if not trigger and not action:
    data = session.getManager("action").getInfo()
    if data == '':
      data = "action: no actions defined."

    exported.write_message(data)
    return

  # they typed '#action dd*' and are looking for matching actions
  if not action:
    data = session.getManager("action").getInfo(trigger)
    if data == '':
      data = "action: no actions defined."

    exported.write_message(data)
    return

  session.getManager("action").addAction(trigger, action)
  if not quiet:
    exported.write_message("action: {%s} {%s} added." % (trigger, action))

commands_dict["action"] = (action_cmd, "trigger= action= quiet:boolean=false")


def alias_cmd(session, args, input):
  """#alias [<alias> <expansion>]

  This adds aliases and tells you the current alias stati of aliases
  already registered.
  """
  name = args["alias"]
  command = args["expansion"]
  quiet = args["quiet"]

  # they typed '#alias'--print out all current aliases
  if not name and not command:
    data = session.getManager("alias").getInfo()
    if data == '':
      data = "alias: no aliases defined."

    exported.write_message(data)
    return

  # they typed '#alias dd*' and are looking for matching aliases
  if not command:
    data = session.getManager("alias").getInfo(name)
    if data == '':
      data = "alias: no aliases defined."

    exported.write_message(data)
    return

  session.getManager("alias").addAlias(name, command)
  if not quiet:
    exported.write_message("alias: {%s} {%s} added." % (name, command))

commands_dict["alias"] = (alias_cmd, "alias= expansion= quiet:boolean=false")


def ansi_cmd(session, args, input):
  """#ansi [on|off]

  With no arguments, tells you whether ansicolor is enabled.
  With arguments, sets the ansicolor global variable.
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


def boss_cmd(session, words, input):
  """#boss

  This command prints stuff to the screen that looks important.
  Oddly enough, it's actually linked list code.
  """
  # FIXME - somehow make this more universal by having a bossfile?
  exported.write_mud_data(lyntin.BOSSTEXT)

commands_dict["boss"] = (boss_cmd, "")


def char_cmd(session, words, input):
  """#char <new-command-denoting-character>

  With no arguments, tells you what the current command character
  is.  With arguments allows you to set the global command
  character.
  """
  char = args["char"]

  if not char:
    exported.write_message("char: current command character is " + 
                                 lyntin.commandchar + ".")
    return

  lyntin.commandchar = char
  exported.write_message("char: new command character is %s."  % char)

commands_dict["^char"] = (char_cmd, "char=")


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

commands_dict["clear"] = (clear_cmd, "")
  

def cr_cmd(session, args, input):
  """#cr

  This sends a carriage return to the mud.  Sometimes this is useful
  in aliases and the like.
  """
  session.writeSocket("\n")

commands_dict["^cr"] = (cr_cmd, "")


def datagrep_cmd(session, args, input):
  """#datagrep {regularexpression}

  Searches this session's databuffer with a regular expression
  printing all matches in their entirety.
  """
  if (session.getName() == "common"):
    exported.write_error("datagrep cannot be applied to common session.")
    return

  pattern = args["pattern"]

  ret = session.getDataBuffer().grepbuffer(pattern)
  exported.write_message("datagrep %s results:\n%s"
                         % (pattern, string.join(ret, "\n")))

commands_dict["datagrep"] = (datagrep_cmd, "pattern")


def datagreplines_cmd(session, args, input):
  """#datagreplines {regularexpression}

  Searches the lines in this session's databuffer with 
  a regular expression printing all matching lines in their 
  entirety.
  """
  if (session.getName() == "common"):
    exported.write_error("datagrep cannot be applied to common session.")
    return

  pattern = args["pattern"]
  ret = session.getDataBuffer().greplines(pattern)
  exported.write_message("datagreplines %s results:\n%s"
                         % (pattern, string.join(ret, "")))

commands_dict["datagreplines"] = (datagreplines_cmd, "pattern")


def deed_cmd(session, args, input):
  """#deed [deed|count]
  
  This adds a deed or prints all the deeds stored till now.
  """
  # original deed_cmd code contributied by Sebastian John

  if (session.getName() == "common"):
    exported.write_error("deed cannot be applied to common session.")
    return

  deedtext = args["text"]
  varexpansion = session.getManager("variable").expand(deedtext)
  if varexpansion:
    deedtext = varexpansion

  if not deedtext:
    data = session.getManager("deed").getInfo()
    if data == "":
      data = "deed: no deeds defined."
    
    exported.write_message(data)
    return
  
  
  if deedtext.isdigit():
    data = session.getManager("deed").getInfo(deedtext)
    if data == "":
      data = "deed: no deeds defined."
    
    exported.write_message(data)
    return
  
  session.getManager("deed").addDeed(deedtext)
  exported.write_message("deed: {%s} added." % deedtext)

commands_dict["deed"] = (deed_cmd, "text=")


def diagnostics_cmd(session, args, input):
  """#diagnostics [logfile]

  This tells you the current status of Lyntin.  Starting with 
  events and moving into the threadmanager and such.  Also pulls
  from the os and sys modules.
  """
  import os, sys
  message = "Diagnostics:\n"
  message = message + exported.get_engine().getDiagnostics()

  message = message + "Thread statii:\n"

  data = exported.get_engine().checkthreads()
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
    message = message + "   " + mem + ": " + repr(lyntin.options[mem]) + "\n"

  exported.write_message(message)
  exported.write_message("This information can be dumped to a "
        "file by doing:\n   #diagnostics dumpfile.txt")

  logfile = args["logfile"]
  if logfile:
    import time
    try:
      f = open(logfile, "w")
      f.write("This file was created on: " + time.ctime(time.time()) + 
              "\n\n")
      f.write(message)
      f.close()
    except Exception, e:
      exported.write_error("diagnostics: Error writing to file %s. %s" 
                            % (logfile, e))

commands_dict["diagnostics"] = (diagnostics_cmd, "logfile=")


def end_cmd(session, args, input):
  """#end

  This is the end command--it shuts down Lyntin.
  """
  import event
  exported.write_message("end: you'll be back...")
  event.ShutdownEvent().enqueue()

commands_dict["^end"] = (end_cmd, "")


def gag_cmd(session, args, input):
  """#gag [<text>]

  With no arguments, it tells you all the gags currently existing.
  With arguments, it sets up a new gag.
  """
  if not args.has_key("text"):
    data = session.getManager("gag").getInfo()
    if data == '':
      data = "gag: no gags defined."

    exported.write_message(data)
    return

  gaggedtext = input[input.find(' ')+1:]
  session.getManager("gag").addGag(gaggedtext)
  exported.write_message("gag: {%s} added." % gaggedtext)

commands_dict["gag"] = (gag_cmd, "text*")


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
    command_list = exported.get_commands()
    for i in range(len(command_list)):
      if len(command_list[i]) > 0 and command_list[i][0] == "^":
        command_list[i] = command_list[i][1:]
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
      data += "Sorry, but" + mem + " is not a valid help topic.\n"
      continue

    lines = f.readlines()
    f.close()
    data += (string.join(lines, "") + "\n")

  exported.write_message(data)

commands_dict["help"] = (help_cmd)


def highlight_cmd(session, args, input):
  """#highlight [<style>] [<text>]

  With no arguments, lists all the highlights currently set.
  With arguments, sets a new highlight.
  """
  style = args["style"]
  text = args["text"]

  if not text and not style:
    data = session.getManager("highlight").getInfo()
    if data == '':
      data = "highlight: no highlights defined."

    exported.write_message(data)
    return

  if text and style:
    session.getManager("highlight").addHighlight(style, text)
    exported.write_message("highlight: {%s} {%s} added." % (style, text))

commands_dict["highlight"] = (highlight_cmd, "style= text=")


def history_cmd(session, args, input):
  """#history

  Prints the history list.
  """
  historylist = exported.get_history()
  for i in range(0, len(historylist)):
    historylist[i] = repr(i) + " " + historylist[i]
  historylist.reverse()
  exported.write_message("History:\n" + string.join(historylist, "\n"))

commands_dict["history"] = (history_cmd, "")


def if_cmd(session, args, input):
  """#if <expr> <action> [else]

  Implements the Tintin++ #if command.
  """
  # original if_cmd code contributed by Sebastian John

  expr = args["expr"]
  action = args["action"]
  elseaction = args["elseaction"]

  # we have to do manual variable expansion here.
  varexpansion = session.getManager("variable").expand(expr)
  if varexpansion:
    expr = varexpansion

  expr = expr.replace("&&", " and ")
  expr = expr.replace("||", " or ")

  try:
    if eval(expr):
      exported.lyntin_command(action)
    elif elseaction:
      exported.lyntin_command(elseaction)
  except SyntaxError:
    exported.write_error("if: invalid syntax / syntax error.")
  except Exception, e:
    exported.write_error("if: exception: %s" % e)

commands_dict["if"] = (if_cmd, "expr action elseaction=")


def ignore_cmd(session, args, input):
  """#ignore

  Turns on and shuts off ignoring of actions for this session.
  """
  if (session.getName() == "common"):
    exported.write_error("ignore cannot be applied to common session.")
    return

  if session._ignoreactions == 1:
    session._ignoreactions = 0
    exported.write_message("ignore: actions are active for session %s." 
                           % session.getName())
  else:
    session._ignoreactions = 1
    exported.write_message("ignore: now ignoring actions for session %s." 
                           % session.getName())

commands_dict["ignore"] = (ignore_cmd, "")


def info_cmd(session, args, input):
  """#info

  This asks the session about its info.  Commands and such.
  """
  exported.write_message(session.getInfo())

commands_dict["info"] = (info_cmd, "")


def killall_cmd(session, args, input):
  """#killall

  Wipes all the sessions of all information.
  """
  for mem in exported.get_active_sessions():
    mem.clear()
    exported.write_message("killall: session %s cleared." % mem.getName())

commands_dict["^killall"] = (killall_cmd, "")


def log_cmd(session, args, input):
  """#log <filename>

  Starts or stops logging to a logfile.
  """
  logfile = args["logfile"]

  if not logfile:
    if session.getLogfile() != None:
      exported.write_message("Currently logging to %s." 
                             % session.getLogfileName())
    else:
      exported.write_message("Logging is disabled.")
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
      session.openLogfile(logfile)
      exported.write_message("log: starting logging to '%s'." % 
                             session.getLogfileName())
    except:
      exported.write_error("log: logfile cannot be opened for appending.")

commands_dict["log"] = (log_cmd, "logfile=")

         
def loop_cmd(session, args, input):
  """#loop {<from>,<to>} {command}

  Implements the loop command (which is more like a range).
  """
  loop = args["fromto"]
  command = args["comm"]

  # split it into parts
  looprange = loop.split(',')

  if len(looprange) != 2:    
    exported.write_error("syntax: #loop <from,to> <command>")
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
    exported.lyntin_command(loopcommand, internal=1, session=session)

commands_dict["loop"] = (loop_cmd, "fromto comm")


def math_cmd(session, args, input):
  """#math <variable> <math ops>

  Implements the #math command which allows you to manipulate
  variables above and beyond setting them.
  """
  var = args["var"]
  ops = args["operation"]

  # we have to do manual variable expansion here.
  varexpansion = session.getManager("variable").expand(ops)
  if varexpansion:
    ops = varexpansion

  try:
    rvalue = eval(ops)
    session.getManager("variable").addVariable(var, repr(rvalue))
    exported.write_message("math: %s = %s." % (var, ops))
  except Exception, e:
    exported.write_error("math: exception: %s" % e)

commands_dict["math"] = (math_cmd, "var operation")


def mudecho_cmd(session, args, input):
  """#mudecho [on|off]

  Sometimes muds screw up the detail and don't properly turn echo
  on and off.  Sometimes you just want to be able to turn it on
  and off on your own.  So this allows you to do that.
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
 

def nop_cmd(session, args, input):
  """#nop <whatever you want to write here....>

  nop stands for "no operation".  So anything after a #nop
  and before a ; (unless it's braced) will be ignored.

  This was quite possibly the easiest command to program.
  """
  return

commands_dict["nop"] = (nop_cmd, "comment*")

def raw_cmd(session, args, input):
  """#raw text_to_mud

  Takes its arguments and sends them straight to the mud.
  """
  session.writeSocket(string.join(args["input"]," ") + "\n")
  exported.write_message(string.join(args["input"]," "))

commands_dict["raw"] = (raw_cmd, "input*")

def read_cmd(session, args, input):
  """#read <filename>

  Reads in a commands file and executes all the lines.
  """
  filename = args["filename"]

  # http reading contributed by Sebastian John
  if filename.find("http://") == 0:
    url = filename[7:]
    if url.find("/") == -1:
      exported.write_error("read: malformed url.")
      return

    try:
      import httplib
    except:
      exported.write_error("read: httplib (required for http command files) " +
                           "cannot be imported.")
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
    try:
      file = open(filename, "r")
    except:
      exported.write_error("read: file %s cannot be opened." % filename)
      return
    
  contents = file.readlines()

  # we want to get rid of initial blank lines and make sure
  # the file has content in it
  while len(contents) > 0 and len(contents[0].strip()) == 0:
    contents = contents[1:]

  if len(contents) == 0:
    exported.write_message("read: %s had no data." % filename)
    return
      
  if contents[0][0] != lyntin.commandchar:
    session.handleUserData(lyntin.commandchar + "char " + contents[0][0])

  for mem in contents:
    mem = mem.strip()
    if len(mem) > 0:
      exported.lyntin_command(mem, internal=1, session=session)

  exported.write_message("read: file " + filename + " read.")

commands_dict["read"] = (read_cmd, "filename")


def session_cmd(session, args, input):
  """#session <sessionname> <host> <port>

  The first argument is the session name.
  The second argument is the hostname/ip address to connect to.
  The third argument is the port number.
  """
  name = args["sessionname"]
  host = args["host"]
  port = args["port"]

  if not name and not host and (not port or port == -1):
    data = "Sessions available:\n"
    # for mem in engine.myengine.getSessions():
    for mem in exported.get_active_sessions():
      data = data + "   " + mem.getName() + ": " + repr(mem._socket) + "\n"

    exported.write_message(data[:-1])
    return

  if not name or not host or not port or port == -1:
    exported.write_error("syntax: #session <sesname> <host> <port>")
    return

  if name.isdigit():
    exported.write_error("session: session names cannot be all numbers.")
    return

  # we do this to deal with non-unique session names
  # it's lame, but whatever
  count = 0
  test = name
  while not exported.get_engine().isUniqueSessionName(test):
    test = sessionname + repr(count)
    count = count + 1

  name = test
  sock = None
  ses = None

  try:
    # create a SocketCommunicator
    sock = net.SocketCommunicator()

    # create a session for it...
    ses = exported.get_engine().createSession()
    ses.setName(name)
    ses.setSocketCommunicator(sock)
    sock.setSession(ses)
    exported.get_engine().registerSession(ses, name)
    exported.get_engine().changeSession(name)

    # connect to the mud...
    sock.connect(host, port, name)

    # start the network thread
    exported.get_engine().startthread("network", sock.run)

  except Exception, e:
    try: 
      exported.get_engine().unregisterSession(name)
      exported.get_engine().closeSession(name)
      sock.shutdown()
    except:
      pass
    exported.write_error("session: unable to connect. %s" % e)
    exported.write_error("session: had problems creating the session.")

  hooks.connect_hook.spamhook((ses, host, port))

commands_dict["session"] = (session_cmd, "sessionname= host= port:int=-1")


def showme_cmd(session, args, input):
  """#showme <message>

  Prints stuff to the user display.
  """
  if input.find(" ") == -1:
    exported.write_error("syntax: #showme <message>")
  else:
    input = input[input.find(" ")+1:]
    exported.write_message(input)
     
commands_dict["showme"] = (showme_cmd, "message*")


def speedwalk_cmd(session, args, input):
  """#speedwalk [on|off]

  With no arguments, tells you whether speedwalk is enabled.
  With arguments, sets the speedwalk global variable.
  """
  option = args["option"]

  if option == 1:
    lyntin.speedwalk = 1
    exported.write_message("speedwalk: now enabled.")
  elif option == 0:
    lyntin.speedwalk = 0
    exported.write_message("speedwalk: now disabled.")
  else:
    if lyntin.speedwalk:
      exported.write_message("speedwalk: enabled.")
    else:
      exported.write_message("speedwalk: disabled.")

commands_dict["speedwalk"] = (speedwalk_cmd, "option:booleanornone=")


def substitute_cmd(session, args, input):
  """#substitue [<item> <substitution>]

  With no arguments, lists all the substitutions currently set.
  With arguments, sets a new substitution.
  """
  item = args["item"]
  substitution = args["substitution"]

  if not item and not substitution:
    data = session.getManager("substitute").getInfo()
    if data == '':
      data = "substitute: no substitutes defined."

    exported.write_message(data)
    return

  if not substitution:
    data = session.getManager("substitute").getInfo(item)
    if data == '':
      data = "substitute: no substitutes defined."

    exported.write_message(data)
    return 

  session.getManager("substitute").addSubstitute(item, substitution)
  exported.write_message("substitute: {%s} {%s} added." % (item, substitution))

commands_dict["substitute"] = (substitute_cmd, "item= substitution=")


def textin_cmd(session, args, input):
  """#textin <filename>

  Takes the contents of the file and outputs it directly to the mud
  without processing it (like #read does).
  """
  if (session.getName() == "common"):
    exported.write_error("textin cannot be applied to common session.")
    return

  filename = args["filename"]

  if not filename:
    exported.write_error("syntax: #textin <filename>")
    return
   
  try:
    file = open(filename, "r")
    contents = file.readlines()
    for mem in contents:
      mem = mem.strip()
      session.getSocketCommunicator().write(mem + "\n")
    exported.write_message("textin: file %s read and sent to client." % filename)

  except IOError:
    exported.write_error("textin: file %s is not readable." % filename)
  except:
    exported.write_error("textin: exception thrown.")

commands_dict["textin"] = (textin_cmd, "file")


def tick_cmd(session, args, input):
  """#tick

  Displays the # of seconds left before the ticker for this
  session ticks.
  """
  if (session.getName() == "common"):
    exported.write_error("tick cannot be applied to common session.")
    return

  if session.getTicker().isEnabled():
    currenttick = exported.get_engine().getCurrentTick()
    ticklen = session.getTicker().getTickLen()
    tickstart = session.getTicker().getTickStart()
    nexttick = ticklen - ((currenttick - tickstart) % ticklen)
    exported.write_message("tick: next tick in %d seconds." % nexttick)
  else:
    exported.write_message("tick: ticker is not enabled.")

commands_dict["tick"] = (tick_cmd, "")


def tickon_cmd(session, args, input):
  """#tickon

  Turns on the ticker.
  """
  if (session.getName() == "common"):
    exported.write_error("tickon cannot be applied to common session.")
    return

  session.getTicker().enableTicker()
  exported.write_message("tickon: session %s ticker enabled." 
                         % session.getName())

commands_dict["tickon"] = (tickon_cmd, "")


def tickoff_cmd(session, args, input):
  """#tickoff

  Turns off the ticker.
  """
  if (session.getName() == "common"):
    exported.write_error("tickoff cannot be applied to common session.")
    return

  session.getTicker().disableTicker()
  exported.write_message("tickoff: session %s ticker disabled." 
                         % session.getName())

commands_dict["tickoff"] = (tickoff_cmd, "")


def ticksize_cmd(session, args, input):
  """#ticksize [{number}]

  Sets and displays the tick length.
  """
  if (session.getName() == "common"):
    exported.write_error("ticksize cannot be applied to common session.")
    return

  size = args["size"]

  if size == 0:
    exported.write_message("ticksize: ticksize is %d seconds." % 
                           session.getTicker().getTickLen())
    return

  if size < 0:
    exported.write_error("ticksize must be a positive number.")
    return

  session.getTicker().setTickLen(int(size))
  exported.write_message("ticksize: tick length set to %s." % repr(size))

commands_dict["ticksize"] = (ticksize_cmd, "size:int=0")


def togglesubs_cmd(session, args, input):
  """#togglesubs

  Turns on and shuts off ignoring of substitutions for this session.
  """
  if (session.getName() == "common"):
    exported.write_error("togglesubs cannot be applied to common session.")
    return

  option = args["option"]
  if option == 1:
    session._ignoresubs = 1
    exported.write_message("togglesubs: substitutions are active for " +
                           "session %s." % session.getName())
  elif option == 0:
    session._ignoresubs = 1
    exported.write_message("togglesubs: now ignoring substitions for " +
                           "session %s." % session.getName())
  else:
    if session._ignoresubs:
      exported.write_message("togglesubs: substitutions are not active for " +
                             "session %s." % session.getName())
    else:
      exported.write_message("togglesubs: substitutions are active for " +
                             "session %s." % session.getName())
    
commands_dict["togglesubs"] = (togglesubs_cmd, "option:booleanornone=")


def unsomething_cmd(session, args, input):
  """#un(gag|substitute|variable|action|alias) <text>

  Allows you to remove gags|substitutes|variables|actions|aliases
  from whatever manager is handling that thing.  This function
  handles all these commands.
  """
  removedthings = []
  singular = ''
  plural = ''

  command = args["command"]
  text = args["var"]

  if "unaction".find(command) == 0:
    removedthings = session.getManager("action").removeActions(text)
    singular = "action"
    plural = "actions"
  elif "unalias".find(command) == 0:
    removedthings = session.getManager("alias").removeAliases(text)
    singular = "alias"
    plural = "aliases"
  elif "ungag".find(command) == 0:
    removedthings = session.getManager("gag").removeGags(text)
    singular = "gag"
    plural = "gags"
  elif "unhighlight".find(command) == 0:
    removedthings = session.getManager("highlight").removeHighlights(text)
    singular = "highlight"
    plural = "highlights"
  elif "unsubstitute".find(command) == 0:
    removedthings = session.getManager("substitute").removeSubstitutes(text)
    singular = "substitute"
    plural = "substitutes"
  elif "unvariable".find(command) == 0:
    removedthings = session.getManager("variable").removeVariables(text)
    singular = "variable"
    plural = "variables"
      

  if len(removedthings) == 0:
    exported.write_message("un%s: No %s removed." % (singular, plural))
    return

  data = ''
  for mem in removedthings:
    if type(mem) == type( (1,2) ):
      data += singular + " {" + mem[0] + "} {" + mem[1] + "} removed.\n"
    else:
      data += singular + " {" + mem + "} removed.\n"

  exported.write_message(data[:-1])

commands_dict["unaction"] = (unsomething_cmd, "var")
commands_dict["unalias"] = (unsomething_cmd, "var")
commands_dict["ungag"] = (unsomething_cmd, "var")
commands_dict["unhighlight"] = (unsomething_cmd, "var")
commands_dict["unsubstitute"] = (unsomething_cmd, "var")
commands_dict["unvariable"] = (unsomething_cmd, "var")


def variable_cmd(session, args, input):
  """#variable [<var> <expansion>]

  With no arguments, lists all the variables currently set.
  With arguments, sets a new variable.
  """
  var = args["var"]
  expansion = args["expansion"]
  quiet = args["quiet"]

  if not var and not expansion:
    data = session.getManager("variable").getInfo()
    if data == '':
      data = "variable: no variables defined."

    exported.write_message(data)
    return

  if not expansion:
    data = session.getManager("variable").getInfo(var)
    if data == '':
      data = "variable: no variables defined."

    exported.write_message(data)
    return 

  try:
    session.getManager("variable").addVariable(var, expansion)
    if not quiet:
      exported.write_message("variable: {%s} {%s} added." % (var, expansion))
  except Exception, e:
    exported.write_error("variable: cannot be set. %s", e)

commands_dict["variable"] = (variable_cmd, "var= expansion= quiet:boolean=false")


def verbatim_cmd(session, args, input):
  """#verbatim

  Turns on and shuts off verbatim mode.
  """
  if (session.getName() == "common"):
    exported.write_error("verbatim cannot be applied to common session.")
    return

  option = args["option"]
  if option == 1:
    session._verbatim = 1
    exported.write_message("verbatim: verbatim enabled for session %s." 
                           % session.getName())
  elif option == 0: 
    session._verbatim = 0
    exported.write_message("verbatim: verbatim disabled for session %s." 
                           % session.getName())
  else:
    if session._verbatim:
      exported.write_message("verbatim: verbatim is enabled for session %s."
                           % session.getName())
    else:
      exported.write_message("verbatim: verbatim is disabled for session %s."
                           % session.getName())

commands_dict["verbatim"] = (verbatim_cmd, "option:booleanornone=")


def version_cmd(session, args, input):
  """#version

  Prints out the version number, date, copyright info, and
  some other garbage to the user.
  """
  exported.write_message(lyntin.VERSION)

commands_dict["version"] = (version_cmd, "")


def wizlist_cmd(session, args, input):
  """#wizlist

  List of people without whom Lyntin wouldn't exist.
  """
  exported.write_message(lyntin.WIZLIST)

commands_dict["wizlist"] = (wizlist_cmd, "")


def write_cmd(session, args, input):
  """#write <filename>

  Queries the sessions and the lyntin globals for stuff
  and writes it out to a file for persistence.
  """
  filename = args["file"]
  try:
    f = open(filename, "w")
    f.write(session.getWriteFileInfo())
    f.close()
    exported.write_message("write: file %s has been written." % filename)
  except Exception, e:
    exported.write_error("write: error writing to file %s. %s" % (filename, e))

commands_dict["write"] = (write_cmd, "file")


def zap_cmd(session, args, input):
  """#zap

  This closes a session and should close the socket and cause
  the SocketCommunicator to garbage collect.
  """
  if exported.get_engine().closeSession(session):
    exported.write_message("zap: session %s zapped!" % session.getName())
  else:
    exported.write_message("zap: session cannot be zapped!")

commands_dict["zap"] = (zap_cmd, "")


def load():
  """ Initializes the module by binding all the commands."""
  for mem in commands_dict.keys():
    args = commands_dict[mem]
    if type(args) == type(()):
      if len(args) == 2:
        exported.add_command(mem, args[0], args[1])
      elif len(args) == 3:
        exported.add_command(mem, args[0], args[1], args[2])
    else:
      exported.add_command(mem, args)

def unload():
  exported.write_message("unbinding commands.")
  for mem in commands_dict.keys():
    exported.remove_command(mem)
