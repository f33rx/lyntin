#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2001
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: session.py,v 1.6 2002/01/20 07:21:02 willhelm Exp $
#######################################################################
"""
Holds the session class.  Sessions are copied from the common session.
"""
import re, copy
import engine, utils, lyntin, event, ticker

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
    self._actionmanager = None
    self._aliasmanager = None
    self._gagmanager = None
    self._hlmanager = None
    self._submanager = None
    self._varmanager = None
    self._logfile = None
    self._ticker = ticker.Ticker()

    # register with the shutdown frequency
    engine.myengine.register(engine.SHUTDOWNFREQ, self.shutdown)

  def __copy__(self):
    """ Copies the session and returns a new session with the same 
    stuff.

    We had problems using copy and deepcopy, so our method was
    to implement our own version of copy.
    """
    ses = Session()
    ses._actionmanager = copy.copy(self._actionmanager)
    ses._aliasmanager = copy.copy(self._aliasmanager)
    ses._gagmanager = copy.copy(self._gagmanager)
    ses._hlmanager = copy.copy(self._hlmanager)
    ses._submanager = copy.copy(self._submanager)
    ses._varmanager = copy.copy(self._varmanager)
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
    # unregister with the shutdown frequency
    engine.myengine.unregister(engine.SHUTDOWNFREQ, self.shutdown)
    if self.getName() != "common":
      engine.myengine.unregisterSession(self.getName())
      if self._socket: self._socket.shutdown()
    event.OutputEvent("Session " + self._name + " shutdown.").enqueue()

  def getInfo(self):
    """ Returns information about the session."""
    data = ("Session name: " + self._name + "\n" +
            "   socket: " + repr(self._socket) + "\n" +
            "   actions: " + 
            repr(len(self.getActionManager().getActions())) + "\n" +
            "   aliases: " + 
            repr(len(self.getAliasManager().getAliases())) + "\n" +
            "   gags: " + repr(len(self.getGagManager().getGags())) + "\n" +
            "   highlights: " + 
            repr(len(self.getHighlightManager().getHighlights())) + "\n" +
            "   substitutes: " + 
            repr(len(self.getSubstituteManager().getSubstitutes())) + "\n" +
            "   variables: " + 
            repr(len(self.getVariableManager().getVariables())) + "\n" +
            "   ticker: " + self.getTicker().getTickerInfo())
    return data

  def setActionManager(self, am):
    """ Sets the action manager."""
    self._actionmanager = am

  def getActionManager(self):
    """ Returns the action manager."""
    return self._actionmanager

  def setAliasManager(self, am):
    """ Sets the alias manager."""
    self._aliasmanager = am

  def getAliasManager(self):
    """ Returns the alias manager."""
    return self._aliasmanager

  def setGagManager(self, gm):
    """ Sets the gag manager."""
    self._gagmanager = gm

  def getGagManager(self):
    """ Returns the gag manager."""
    return self._gagmanager

  def setHighlightManager(self, hm):
    """ Sets the highlight manager."""
    self._hlmanager = hm

  def getHighlightManager(self):
    """ Returns the highlight manager."""
    return self._hlmanager

  def setSubstituteManager(self, sm):
    """ Sets the substitution manager."""
    self._submanager = sm

  def getSubstituteManager(self):
    """ Returns the substitution manager."""
    return self._submanager

  def setVariableManager(self, vm):
    """ Sets the variable manager."""
    self._varmanager = vm

  def getVariableManager(self):
    """ Returns the variable manager."""
    return self._varmanager

  def setTicker(self, ticker):
    """ Sets the ticker."""
    self._ticker = ticker

  def getTicker(self):
    """ Returns the ticker."""
    return self._ticker

  def getWriteFileInfo(self):
    """ Pulls all the session information for #write command."""
    data = ''

    # save the command char (if it's not the default)
    if lyntin.commandchar != '#':
      data += "#char " + lyntin.commandchar + "\n"

    # saves speedwalking state
    if lyntin.speedwalk == 1:
      data += "#speedwalk on\n"
    else: 
      data += "#speedwalk off\n"

    # saves ansi state
    if lyntin.ansicolor == 1:
      data += "#ansi on\n"
    else: 
      data += "#ansi off\n"

    def fixinfo(item):
      if item:
        return item + "\n"
      return ""

    data += fixinfo(self._aliasmanager.getAliasInfo())
    data += fixinfo(self._actionmanager.getActionInfo())
    data += fixinfo(self._gagmanager.getGagInfo())
    data += fixinfo(self._hlmanager.getHighlightInfo())
    data += fixinfo(self._submanager.getSubstituteInfo())
    data += fixinfo(self._varmanager.getVariableInfo())
    return data

  def clear(self):
    """ Clears the session (except for connections)."""
    self._aliasmanager.clear()
    self._actionmanager.clear()
    self._gagmanager.clear()
    self._hlmanager.clear()
    self._submanager.clear()
    self._varmanager.clear()
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
    we won't spam frequencies and may at some point prevent
    output for internal stuff too.  1 if internal, 0 if not.
    """
    # we deal with possible variables...
    varexpansion = self.getVariableManager().expand(input)
    if varexpansion:
      varexpansion = self.getVariableManager().unescapeVariables(varexpansion)
      engine.myengine.handleUserData(varexpansion, internal)
      return

    # replace \$ -> $
    input = self.getVariableManager().unescapeVariables(input)

    # handle lyntin commands
    if len(input) > 1 and input[0] == lyntin.commandchar:
      input = input[1:]

      words = input.split(" ")
      handled_command = 0

      # this finds the first matching command and ends there.
      commands = engine.myengine.getCommands()
      commands.sort()
      for mem in commands:
        if mem[0] == "^":
          if re.compile(mem).search(words[0]):
            engine.myengine.getCommand(mem)(self, words, input)
            if internal==0: self._prompt()
            handled_command = 1
            break
        else:
          if mem.find(words[0]) == 0:
            engine.myengine.getCommand(mem)(self, words, input) 
            if internal==0: self._prompt()
            handled_command = 1
            break

      else:
        engine.myengine.writeError("Not a valid command.")
        if internal==0: self._prompt()
      return

    # we check for aliases here--and if we find some, we
    # do the variable expansion and then recurse over the result
    aliasexpansion = self.getAliasManager().expand(input)
    if aliasexpansion:
      # replace placement variables in the expansion
      aliasexpansion = utils.replace_vars(input, aliasexpansion)

      engine.myengine.handleUserData(aliasexpansion, internal)
      return

    # if we don't have a socket then we can't do any non-lyntin-command
    # stuff.
    if self._socket == None:
      engine.myengine.writeError("No connection.  Create a session.")
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

    # handle gags
    input = self.getGagManager().removeGaggedText(input)

    # handle substitutions
    input = self.getSubstituteManager().expand(input)

    # handle actions
    self.getActionManager().checkActions(input)

    if lyntin.ansicolor == 0:
      input = utils.filter_ansi(input)
    else:
      # handle highlights 
      input = self.getHighlightManager().expand(input)

    engine.myengine.writeMudData(input)

  def log(self, input):
    """ Logs text to a file instance in self._logfile."""
    try:
      # FIXME - this assumes unix files
      self._logfile.write(utils.filter_ansi(utils.filter_cm(input)))
    except:
      engine.myengine.writeError("Logfile cannot be written to.")
      self._logfile = None
