#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: session.py,v 1.19 2002/03/29 06:23:29 willhelm Exp $
#######################################################################
"""
Holds the session class.  Sessions are copied from the common session.
"""
import re, copy, string
import exported, engine, utils, lyntin, event, ticker

# this is the regular expression that matches speedwalking stuff
SPEEDWALK_REGEXP = re.compile('^\d*[udnsew][udnsew\d]*$')

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

    # allows users to toggle whether we're handling actions.
    # 0 for handling actions, 1 if we're ignoring actions.
    self._ignoreactions = 0

    # allows users to toggle whether we're doing substitutions.
    # 0 for substitutions, 1 if we're ignoring substitutions
    self._ignoresubs = 0

    # register with the shutdown hook 
    engine.myengine.register(engine.SHUTDOWN_HOOK, self.shutdown)

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

  def shutdown(self, args):
    """ Shuts down the session."""
    # unregister with the shutdown hook
    engine.myengine.unregister(engine.SHUTDOWN_HOOK, self.shutdown)
    if self.getName() != "common":
      engine.myengine.unregisterSession(self.getName())
      if self._socket: self._socket.shutdown()
    event.OutputEvent("Session " + self._name + " shutdown.").enqueue()
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
      data += "   ignore: substitutions are active."
    else:
      data += "   ignore: substitutions are ignored."

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

  def writeSocket(self, message):
    """ Writes data to the socket."""
    if self._socket:
      self._socket.write(message)


  ### ------------------------------------------------
  ### User input functions
  ### ------------------------------------------------

  def _prompt(self):
    """ Deals with printint a prompt if this is the common session."""
    if self.getName() == "common":
      engine.myengine.writePrompt()

  def handleUserData(self, input, internal=0):
    """ Handles input in the context of this session specifically.

    internal says whether the command came from interally.
    we won't spam hooks and may at some point prevent
    output for internal stuff too.  1 if internal, 0 if not.
    """
    # we deal with possible variables...
    varexpansion = self.getManager("variable").expand(input)
    if varexpansion:
      varexpansion = self.getManager("variable").unescapeVariables(varexpansion)
      engine.myengine.handleUserData(varexpansion, internal)
      return

    # replace \$ -> $
    input = self.getManager("variable").unescapeVariables(input)

    # handle lyntin commands
    if len(input) > 1 and input[0] == lyntin.commandchar:
      input = input[1:]

      words = input.split(" ")

      # this checks to see if it's a special #@ command.
      if input[0] == "@":
        engine.myengine.getCommand("@")(self, words, input)
        if internal==0: self._prompt()
        return

      # this finds the first matching command and ends there.
      commands = engine.myengine.getCommands()
      commands.sort()
      for mem in commands:
        if mem[0] == "^":
          if re.compile(mem).search(words[0]):
            engine.myengine.getCommand(mem)(self, words, input)
            if internal==0: self._prompt()
            break
        else:
          if mem.find(words[0]) == 0:
            engine.myengine.getCommand(mem)(self, words, input) 
            if internal==0: self._prompt()
            break

      else:
        exported.write_error("Not a valid command.")
        if internal==0: self._prompt()
      return

    # we check for aliases here--and if we find some, we
    # do the variable expansion and then recurse over the result
    aliasexpansion = self.getManager("alias").expand(input)
    if aliasexpansion:
      # replace placement variables in the expansion
      aliasexpansion = utils.replace_vars(input, aliasexpansion)

      engine.myengine.handleUserData(aliasexpansion, internal)
      return

    # if we don't have a socket then we can't do any non-lyntin-command
    # stuff.
    if self._socket == None:
      exported.write_error("No connection.  Create a session.")
      if internal==0: self._prompt()
      return

    # are we speedwalking?... ("news" explicitly doesn't count)
    if lyntin.speedwalk == 1:
      # FIXME - handle news and sense differently
      if SPEEDWALK_REGEXP.search(input) and input != 'news':
        self._socket.write(utils.expand_speedwalk(input))
        return

    # just regular data to the mud
    self._socket.write(input + "\n")


  ### ------------------------------------------------
  ### Mud input functions
  ### ------------------------------------------------

  def handleMudData(self, input):
    """ Handles input coming from the mud."""
    if self._logfile:
      self.log(input)

    inputlines = input.splitlines(1)

    for i in range(0, len(inputlines)):
      mem = inputlines[i]
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
    exported.write_mud_data(input)


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
