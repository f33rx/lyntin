#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: session.py,v 1.42 2002/04/27 20:58:19 jmberne Exp $
#######################################################################
"""
Holds the session class.  Sessions are copied from the common session.
"""
import re, copy, string
import deed, variable, data, exported, engine, hooks, utils, lyntin, event, ticker
import argparser

# this is the regular expression that matches speedwalking stuff

class Session:
  """ A session is a nice container of all the stuff that
  encompasses a user session: aliases, actions, commands...

  All input and output goes through the Session object.
  Almost everything happens throughthe Session.
  """
  def __init__(self):
    """ Initialize."""
    self._socket = None
    self._name = ""
    self._managers = {}
    self._logfile = None
    self._ticker = ticker.Ticker()

    self.setManager("deed", deed.DeedManager())

    self._databuffer = data.DataBuffer()

    # allows users to toggle whether we're handling actions.
    # 0 for handling actions, 1 if we're ignoring actions.
    self._ignoreactions = 0

    # allows users to toggle whether we're doing substitutions.
    # 0 for substitutions, 1 if we're ignoring substitutions
    self._ignoresubs = 0

    # tells us whether we're in verbatim mode where we don't
    # do any massaging of user data.
    # 0 if we're massaging stuff, 1 if we're in verbatim mode
    self._verbatim = 0

    # register with the shutdown hook 
    hooks.shutdown_hook.register(self.shutdown)

  def __copy__(self):
    """ Copies the session and returns a new session with the same 
    stuff.

    We had problems using copy and deepcopy, so our method was
    to implement our own version of copy.
    """
    ses = Session()
    ses._managers = copy.copy(self._managers)
    return ses
      
  def __repr__(self):
    return "session.Session " + self._name
     
  # SESSION STUFF

  def getName(self):
    """ Returns the name of the session."""
    return self._name

  def setName(self, name):
    """ Sets the name of the session."""
    self._name = name
    self.getTicker().setSessionName(name)

  def getDataBuffer(self):
    """ Returns the DataBuffer instance."""
    return self._databuffer

  def shutdown(self, args):
    """ Shuts down the session."""
    # unregister with the shutdown hook
    hooks.shutdown_hook.unregister(self.shutdown)
    if self.getName() != "common":
      engine.myengine.unregisterSession(self.getName())
      if self._socket: self._socket.shutdown()
    event.OutputEvent("Session " + self._name + " shutdown.\n").enqueue()
    self._ticker.clear()

  def getInfo(self):
    """ Returns information about the session."""
    data = ("Session name: " + self._name + "\n" +
            "   socket: " + repr(self._socket) + "\n")

    managerkeys = self._managers.keys()
    managerkeys.sort()

    for mem in managerkeys:
      data += "   " + mem + ": " +  repr(self.getManager(mem).getCount()) + "\n"

    data += ("   ticker: " + self.getTicker().getInfo() + "\n" +
             "   logfile: " + self.getLogfileName() + "\n")

    if lyntin.speedwalk == 1:
      data += "   speedwalk: on\n"
    else: 
      data += "   speedwalk: off\n"

    if self._ignoreactions == 0:
      data += "   ignore: actions are active.\n"
    else:
      data += "   ignore: actions are ignored.\n"

    if self._ignoresubs == 0:
      data += "   togglesubs: substitutions are active.\n"
    else:
      data += "   togglesubs: substitutions are ignored.\n"

    if self._verbatim == 0:
      data += "   verbatim: input is parsed."
    else:
      data += "   verbatim: imput is passed verbatim."

    return data

  def setManager(self, manager, object):
    """ Sets a manager in the manager hash."""
    self._managers[manager] = object

  def getManager(self, manager):
    """ Retrieves a manager from the hash."""
    if self._managers.has_key(manager):
      return self._managers[manager]
    else:
      return None

  def setTicker(self, ticker):
    """ Sets the ticker."""
    self._ticker = ticker

  def getTicker(self):
    """ Returns the ticker."""
    return self._ticker

  def getWriteFileInfo(self):
    """ Pulls all the session information for #write command."""
    data = ''

    # saves speedwalking state
    if lyntin.speedwalk == 1:
      data += lyntin.commandchar + "speedwalk on\n"
    else: 
      data += lyntin.commandchar + "speedwalk off\n"

    # saves ansi state
    if lyntin.ansicolor == 1:
      data += lyntin.commandchar + "ansi on\n"
    else: 
      data += lyntin.commandchar + "ansi off\n"

    def fixinfo(item):
      if item:
        return item + "\n"
      return ""

    managerkeys = self._managers.keys()
    managerkeys.sort()

    for mem in managerkeys:
      data += fixinfo(self._managers[mem].getInfo())

    return data

  def clear(self):
    """ Clears the session (except for connections)."""
    for mem in self._managers.values():
      mem.clear()
    self._ticker.clear()


  ### ------------------------------------------------
  ### Socket stuff
  ### ------------------------------------------------

  def setSocketCommunicator(self, sc):
    """ Sets the socket communicator."""
    self._socket = sc

  def getSocketCommunicator(self):
    """ Returns the socket communicator."""
    return self._socket

  def isConnected(self):
    """ Tells you whether or not a session has a connection."""
    return self._socket != None

  def writeSocket(self, message, tag = None):
    """ Writes data to the socket."""
    for line in message.strip().split("\n"):
      hooks.to_mud_hook.spamhook((self, line, tag))
    if self._socket:
      self._socket.write(str(message))


  ### ------------------------------------------------
  ### User input functions
  ### ------------------------------------------------

  def _prompt(self):
    """ Deals with printint a prompt if this is the common session."""
    if self.getName() == "common":
      engine.myengine.writePrompt()

  def handleUserData(self, input, internal=0 ):
    """ Handles input in the context of this session specifically.

    internal says whether the command came from interally.
    we won't spam hooks and may at some point prevent
    output for internal stuff too.  1 if internal, 0 if not.
    """
    if self._verbatim == 0 or (len(input) > 0 and input[0] == lyntin.commandchar):

      spamtuple = self,internal,input,input
      spamtuple = hooks.user_filter_hook.spamhook(spamtuple)
      if spamtuple == None:
        return
      else:
        input = spamtuple[-1]

    # handle lyntin commands
    if len(input) > 1 and input[0] == lyntin.commandchar:
      input = input[1:]

      # splits out the command name from the rest of the command line
      words = input.split(" ",1)

      # We want an empty argument list if there was one, don't want
      # array out-of-bounds issues       
      if len(words) < 2: words.append("")

      # this checks to see if it's a special #@ command.
      if input[0] == "@":
        engine.myengine.getCommand("@")(self, input.split(" "), input)
        if internal==0: self._prompt()
        return

      # this finds the first matching command and ends there.
      commands = engine.myengine.getCommands()
      commands.sort()
      for mem in commands:
        if mem[0] == "^":
          if re.compile(mem).search(words[0]):
            command = engine.myengine.getCommand(mem)
            argumentparser = engine.myengine.getArgParser(mem)
            if argumentparser == None:
              command(self, input.split(" "), input)
            else:
              try:
                dict = argumentparser.parse(words[1])
                dict["command"]=mem
                command(self, dict, input)
              except ValueError, e:
                exported.write_error("%s: %s" % (mem, e))
              except argparser.ParserException, e:
                exported.write_error("%s: %s" % (mem, e))
            if internal==0: self._prompt()
            break
        else:
          if mem.find(words[0]) == 0:
            command = engine.myengine.getCommand(mem)
            argumentparser = engine.myengine.getArgParser(mem)
            if argumentparser == None:
              command(self, input.split(" "), input)
            else:
              try:
                dict = argumentparser.parse(words[1])
                dict["command"]=mem
                command(self, dict, input)
              except ValueError, e:
                exported.write_error("%s: %s" % (mem, e))
              except argparser.ParserException, e:
                exported.write_error("%s: %s" % (mem, e))
            if internal==0: self._prompt()
            break

      else:
        exported.write_error("Not a valid command: %s" % (words[0]))
        if internal==0: self._prompt()
      return

    # if we don't have a socket then we can't do any non-lyntin-command
    # stuff.
    if self._socket == None:
      exported.write_error("No connection.  Create a session.")
      if internal==0: self._prompt()
      return

    # just regular data to the mud
    self.writeSocket(input + "\n")


  ### ------------------------------------------------
  ### Mud input functions
  ### ------------------------------------------------

  def handleMudData(self, input):
    """ Handles input coming from the mud."""
    if self._logfile:
      self.log(input)

    self._databuffer.addData(input)

    inputlines = input.splitlines(1)

    for i in range(0, len(inputlines)):
      mem = inputlines[i]
      # call the pre-filter hook
      spamtuple = self,mem,mem
      spamtuple = hooks.mud_filter_hook.spamhook(spamtuple)
      mem = spamtuple[2]

      # handle gags
      mem = self.getManager("gag").removeGaggedText(mem)

      # handle substitutions
      if self._ignoresubs == 0:
        mem = self.getManager("substitute").expand(mem)

      # handle actions
      if self._ignoreactions == 0:
        self.getManager("action").checkActions(mem)

      if lyntin.ansicolor == 0:
        mem = utils.filter_ansi(mem)
      else:
        # handle highlights 
        mem = self.getManager("highlight").expand(mem)

      inputlines[i] = mem

    input = string.join(inputlines, "")
    exported.write_mud_data(input, self)


  def log(self, input):
    """ Logs text to a file instance in self._logfile.

    arguments:

      'input' -- (string) the string to log to the logfile for this session

    """
    try:
      # FIXME - this assumes unix files
      self._logfile.write(utils.filter_ansi(utils.filter_cm(input)))
    except:
      exported.write_error("Logfile cannot be written to.")
      self._logfile = None

  def getLogfile(self):
    """ Returns the logfile file instance or None."""
    return self._logfile

  def closeLogfile(self):
    if self._logfile:
      self._logfile.close()
      self._logfile = None

  def openLogfile(self, filename):
    self._logfile = open(filename, "a")

  def getLogfileName(self):
    if self._logfile:
      return self._logfile.name
    else:
      return "<none>"


class ManagerFilterAdapter:
  def __init__(self, managername, function=None):
    self.managername=managername
    self.function = function

  def __call__(self, tuple):
    session, internal, input, filtered = tuple
    if self.function:
      return self.function(session.getManager(self.managername),tuple)
    else:
      return session.getManager(self.managername).filter(tuple)


hooks.user_filter_hook.register(ManagerFilterAdapter("variable"),0)

hooks.user_filter_hook.register(ManagerFilterAdapter("alias"),20)

hooks.user_filter_hook.register(ManagerFilterAdapter("speedwalk"),80)

hooks.user_filter_hook.register(ManagerFilterAdapter("variable",variable.VariableManager.unescapeVariables),90)

