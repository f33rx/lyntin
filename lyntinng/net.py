#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: net.py,v 1.20 2002/05/22 01:29:36 willhelm Exp $
#######################################################################
"""
This holds the SocketCommunicator class which handles socket
connections with a mud and polling the connection for data.
"""
import socket, string, select
import exported, event

### --------------------------------------------
### CONSTANTS
### --------------------------------------------

CODES = {255: "IAC",
         254: "DON'T",
         253: "DO",
         252: "WON'T",
         251: "WILL",
         250: "SB",
         240: "SE",
         0:   "<IS>",
         1:   "[<ECHO> or <SEND>]",
         3:   "<SGA>",
         24:  "<TERMTYPE>",
         31:  "<NegoWindoSize>",
         32:  "<TERMSPEED>",
         35:  "<XDISPLAY>",
         39:  "<ENV>"}

IAC  = chr(255)
DONT = chr(254)
DO   = chr(253)
WONT = chr(252)
WILL = chr(251)
SB   = chr(250)
SE   = chr(240)
SEND = chr(1)
IS   = chr(0)

DD       = DO + DONT
WW       = WILL + WONT
DDWW     = DD + WW

ECHO     = chr(1)
SGA      = chr(3)
TERMTYPE = chr(24)
NAWS     = chr(31)
ENV      = chr(39)



class SocketCommunicator:
  """
  The SocketCommunicator handles all incoming and outgoing
  data from and to the mud.
  """
  def __init__(self):
    self._sessionname = ''
    self._host = ''
    self._port = 0
    self._sock = None
    self._ansimode = 1
    self._nego_buffer = ''
    self._shutdownflag = 0
    self._session = None

  def __repr__(self):
    return "connection %s %d" % (self._host, self._port)

  def setSession(self, newsession):
    """ Sets the local session.

    arguments:

      'newsession' -- (session.Session) the session to set to

    """
    self._session = newsession

  def shutdown(self):
    """ Shuts down a socket connection and the thread polling it."""
    self._shutdownflag = 1
    if self._sock:
      import ui.ui
      event.OutputEvent(ui.ui.Message("Lost connection to: %s\n" % self._host)).enqueue()
      try:
        self._sock.shutdown(2)
      except:
        pass
      self._sock.close()
      self._sock = None
      self._session = None

  def connect(self, host, port, sessionname):
    """ Takes in a host and a port and connects the socket.

    arguments:

      'host' -- (string) the host to connect to

      'port' -- (int) the port to connect at

      'sessionname' -- (string) the name of the session

    """
    if type(port) == type(''):
      port = int(port)

    exported.write_message("Trying to connect to %s." % host)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.setblocking(1)

    self._host = host
    self._port = port
    self._sock = sock
    self._sessionname = sessionname
    exported.write_message("Connection made.")
  
  def run(self):
    """ Polls a socket and returns any data sitting there."""
    try:
      while not self._shutdownflag:
        readers,e,w = select.select([self._sock], [], [], .1)
        if readers:
          data = readers[0].recv(1024)
          if data == '':
            if self._shutdownflag == 0 and self._session: 
              self._session.shutdown(())
            return

          if IAC in data or self._nego_buffer != '':
            data = self.handleNego(self._nego_buffer + data)

          self.handleData(data)

    except SystemExit:
      if self._shutdownflag == 0 and self._session:
        self._session.shutdown(())

    except Exception, e:
      if self._shutdownflag == 0 and self._session:
        self._session.shutdown(())


  def write(self, data, convert=1):
    """ Writes data to the mud.

    arguments:

      'data' -- (string) the data to write to the socket to the mud

      'convert=1' -- (int) 1 if we should convert eol stuff, 0 if not

    """
    if convert:
      data = data.replace("\n", "\r\n")

    try:
      self._sock.send(data)
    except:
      if self._shutdownflag == 0 and self._session:
        # FIXME - this might not be prudent--might want to create
        # an event for shutting down sessions.
        self._session.shutdown(())


  def handleData(self, data):
    """
    Handles incoming data from the mud.

    arguments:

      'data' -- (string) incoming data

    """
    event.MudEvent(self._session, data).enqueue()


  def handleNego(self, data):
    """
    Removes telnet negotiation stuff from the stream and handles 
    it.

    arguments:

      'data' -- (string) incoming data that we need to parse
                for telnet negotiation stuff

    returns:

      (string) the data without the telnet control codes

    """
    # FIXME - this needs to be re-written without the try block
    i = data.find(IAC)

    while (i != -1):
      try:
        if data[i+1] in DDWW:
          if data[i+2] == ECHO:
            if data[i+1] == WILL:
              event.EchoEvent(0).enqueue()
            elif data[i+1] == WONT:
              event.EchoEvent(1).enqueue()
          elif data[i+1] in DD:
            self.write(IAC + WONT + data[i+2])

          data = data[:i] + data[i+3:]

        elif data[i+1] == SB:
          end = data.find(SE, i)
          if end == -1:
            self._nego_buffer = data[i:]
            data = data[:i]
            break
          else:
            data = data[:i] + data[end+1:]

        else:
          data = data[:i] + data[i+3:]

      except IndexError:
        self._nego_buffer = data[i:]
        data = data[:i]
        break

      i = data.find(IAC, i)

    return data
