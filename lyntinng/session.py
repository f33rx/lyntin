#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: session.py,v 1.61 2002/07/07 17:44:42 willhelm Exp $
#######################################################################
"""
Holds the session class.  Sessions are copied from the common session.
"""
import re, copy, string
import data, exported, engine, hooks, utils, lyntin, event, ticker
import argparser

ESC = chr(27)

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
    self._host = "none"
    self._port = 0
    self._logfile = None
    self._ticker = ticker.Ticker()
    self._colorbuffer = ''

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
    hooks.write_hook.register(self.getWriteFileInfo)

  def __repr__(self):
    return "session.Session %s" % self._name

  def getName(self):
    """ Returns the name of the session.

    returns:

      (string)
    """
    return self._name

  def setName(self, name):
    """ Sets the name of the session.

    arguments:
      
      'name' -- (string)
    """
    self._name = name
    self.getTicker().setSessionName(name)

  def getDataBuffer(self):
    """ Returns the DataBuffer instance.

    returns:
      
      data.DataBuffer instance
    """
    return self._databuffer

  def shutdown(self, args):
    """ Shuts down the session."""
    # unregister with the shutdown hook
    hooks.shutdown_hook.unregister(self.shutdown)
    if self.getName() != "common":
      try:
        exported.get_engine().unregisterSession(self)
      except Exception, e:
        exported.write_message("Exception unregistering session %s." % e)
      if self._socket: self._socket.shutdown()
    event.OutputEvent("Session %s shutdown.\n" % self._name).enqueue()
    self._ticker.clear()
    hooks.disconnect_hook.spamhook((self, self._host, self._port))

  def getStatus(self):
    """ Returns status of the session.

    returns:
      
      (string)
    """
    data = []
    
    data.append("Session name: %s" % self._name)
    data.append("   socket: %s" % repr(self._socket))

    data.append("   ticker: %s" % self.getTicker().getInfo())
    data.append("   logfile: %s" % self.getLogfileName())

    return data

  def setTicker(self, ticker):
    """ Sets the ticker.

    arguments:
      
      'ticker' -- (ticker.Ticker instance)
    """
    self._ticker = ticker

  def getTicker(self):
    """ Returns the ticker.

    returns:
      
      (ticker.Ticker instance)
    """
    return self._ticker

  def getWriteFileInfo(self, args):
    """ Implements the write_hook."""
    ses = args[0]

    if not ses == self:
      return

    file = args[1]

    data = []

    # saves speedwalking state
    if lyntin.speedwalk == 1:
      data.append(lyntin.commandchar + "speedwalk on")
    else: 
      data.append(lyntin.commandchar + "speedwalk off")

    # saves ansi state
    if lyntin.ansicolor == 1:
      data.append(lyntin.commandchar + "ansi on")
    else: 
      data.append(lyntin.commandchar + "ansi off")

    file.write(string.join(data, "\n") + "\n")

  def clear(self):
    """ Clears the session (except for connections)."""
    engine = exported.get_engine()
    for mem in engine._managers.values():
      mem.clear(self)

    self._ticker.clear()


  ### ------------------------------------------------
  ### Socket stuff
  ### ------------------------------------------------

  def setSocketCommunicator(self, sc):
    """ Sets the socket communicator.

    arguments:
      
      'sc' -- (net.SocketCommunicator instance)
    """
    self._socket = sc

  def getSocketCommunicator(self):
    """ Returns the socket communicator.

    returns:
      
      net.SocketCommunicator instance
    """
    return self._socket

  def isConnected(self):
    """ Tells you whether or not a session has a connection.

    returns:
      
      1 if connected, 0 if not
    """
    return self._socket != None

  def writeSocket(self, message, tag = None):
    """ Writes data to the socket.

    arguments:
      
      'message' -- (string) what is to be written to the mud

      'tag=None' -- (object) Used to tag data being sent to the mud
                    for identification when it comes out of the
                    to_mud_hook.  Simply passed through as-is by
                    lyntin internals.
    """
    for line in message.strip().split("\n"):
      hooks.to_mud_hook.spamhook((self, line, tag))
    if self._socket:
      self._socket.write(str(message))


  ### ------------------------------------------------
  ### User input functions
  ### ------------------------------------------------

  def prompt(self):
    """ Deals with printint a prompt if this is the common session."""
    if self.getName() == "common":
      engine.myengine.writePrompt()

  def handleUserData(self, input, internal=0 ):
    """ Handles input in the context of this session specifically.

    internal says whether the command came from interally.
    we won't spam hooks and may at some point prevent
    output for internal stuff too.  1 if internal, 0 if not.
    """

    # this is the point of much recursion.  everything is registered
    # as a filter and recurses accordingly.
    spamtuple = self,internal,self._verbatim,input,input
    spamtuple = hooks.user_filter_hook.spamhook(spamtuple)
    if spamtuple == None:
      return
    else:
      input = spamtuple[-1]


    # after this point we don't do any more recursion.  so it's
    # safe to unescape things and such.
    input = input.replace("\\;", ";")
    input = input.replace("\\$", "$")
    input = input.replace("\\%", "%")

    # if we don't have a socket then we can't do any non-lyntin-command
    # stuff.
    if not self.isConnected():
      exported.write_error("No connection.  Create a session.\n(See also: #help, #help session)")
      if internal == 0:
        self.prompt()
      return

    # just regular data to the mud
    self.writeSocket(input + "\n")


  ### ------------------------------------------------
  ### Mud input functions
  ### ------------------------------------------------

  def handleMudData(self, input):
    """ Handles input coming from the mud.

    arguments:
      
      'input' -- (string) the data from the mud
    """
    # this sort of handles ansi color codes that get broken 
    # mid-transmission when mud data is chunked and sent across
    # the network.
    if self._colorbuffer:
      input = self._colorbuffer + input
      self._colorbuffer = ''

    index = input.rfind(ESC)
    if index != -1 and input.find("m", index) == -1:
      self._colorbuffer = input[index:]
      input = input[:index]

    if self._logfile:
      self.log(input)

    # we add the new input to the databuffer
    self._databuffer.addData(input)

    # we split the input into a series of lines and operate on
    # those
    inputlines = input.splitlines(1)

    for i in range(0, len(inputlines)):
      mem = inputlines[i]
      # call the pre-filter hook
      spamtuple = self,mem,mem
      spamtuple = hooks.mud_filter_hook.spamhook(spamtuple)
      if spamtuple != None:
        mem = spamtuple[-1]
      else:
        mem = ""

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
      self._logfile.flush()
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

  def setLogfile(self, fileob):
    self._logfile = fileob

  def getLogfileName(self):
    if self._logfile:
      return self._logfile.name
    else:
      return "<none>"
