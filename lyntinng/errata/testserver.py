#!/usr/bin/env python
#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: testserver.py,v 1.11 2002/06/01 15:51:44 willhelm Exp $
#######################################################################
"""
This runs a multithreaded server on port 3000.
It used to test mud clients.  It currently take no arguments.
"""
import SocketServer, random, time, string, thread

# terrible global shutdown variable
shutdown = 0
server = None

class ConnectionHandler(SocketServer.StreamRequestHandler):

  def setup(self):
    print "Connection from: " + repr(self.request)
    SocketServer.StreamRequestHandler.setup(self)
    self._vocab = ['look', 'bleeding', 'door', 'cat', 'dog', 'naga',
           'doh!', 'horse', 'slashed', 'hurt', 'jumped', 'dodged',
           'says', 'tell', 'goblin', 'pink', 'crunch', 'smashed',
           'hungry', 'thirsty', 'huh?', 'glows', 'drop', 'blind',
           'to', 'the', 'of', 'broken', 'red', 'smoke']
    self._spamFreq = 0
    self._message = ''
    self._myline = 'Default testserver line.'

    self._rlist = [self.request]

    self._spamThread = None

    self._dir = []
    for item in dir(self.__class__):
      if ( type( eval("self.%s" % item)) == type(self.__init__) and item.find("handle_") == 0):
        self._dir.append(item)

  def write(self, data):
    # put data in string for writing when socket ready
    data = data.replace("\n", "\r\n")

    # add data for sending
    self.request.send(data)

  def handle(self):
    """
    This is the function that gets called by the StreamRequestHandler object.
    """
    self.write(self.color("You're logged in.") + "\n")
    import select

    try:
      self.request.setblocking(1)
      data = ''
      while shutdown == 0:
        # check to see what is ready on the socket
        conns = select.select([self.request], [], [], 0)[0]
        for mem in conns:
          # lets get the message
          data += self.request.recv(1024)

          if data.find("\n") != -1:
            message = data[:data.find("\n")]
            print "incoming: '%s'" % message[:-1]
            self.messageHandler(message[:-1])
            data = data[data.find("\n") + 1:]
    except Exception, e:
      print "Exception for %s\n%s" % (self.request, e)

    return

  def messageHandler(self, text):
    """
    messageHandler('the message read off readline')
    text is the message which is checked against the first 3 letters for
    a command match.
    """
    comm = text.split(" ", 1)[0]
    self.write(self.color(time.ctime() + " <" + str(time.clock()) + ">",32,40) + " '%s'\n" % text)
    if ("handle_%s" % comm) in self._dir:
      exec ( "self.handle_%s(text)" % comm)
    else:
      # CATCH ALL for bad commands
      self.write(self.color("received unimplemented command '%s'" % comm, 33) + "\n")

  def handle_quit(self, text):
    """ Quits your session."""
    self.write("bye bye\n")
    raise ValueError, "Shutdown of connection requested."
    
  def handle_remember(self, text):
    """ Forces us to memorize something to "repeat" back to you later."""
    self._myline = text[text.find(" ")+1:]

  def handle_repeat(self, text):
    """ Has us repeat something we "remember"."""
    self.write(self._myline + "\n")

  def handle_command(self, text):
    """ Prints out all the commands we understand."""
    commands = []
    for mem in self._dir:
      if mem.find("handle_") == 0:
        doc = ""
        try: doc = eval ("self.%s.__doc__" % mem)
        except: pass

        if doc:
          commands.append(mem[7:] + " - " + doc)
        else:
          commands.append(mem[7:])

    self.write(string.join(commands, "\n") + "\n")

  def handle_colors(self, text):
    """ Prints out all the colors we know about."""
    response = ''
    for background in range(40,48):
      for foreground in range(30,38):
        response += self.color(str(foreground), foreground, background)
        response += self.color(str(foreground), foreground, background, 1)
      response += "\n"

    self.write(response)

  def handle_word(self, text):
    """ Returns a random word."""
    response = ''
    response = self.getWords(1) + "\n"
    self.write(response)

  def handle_line(self, text):
    """ Returns a line consisting of 10 random words."""
    response = ''
    response = self.getWords(10) + "\n"
    self.write(response)
      
  def handle_paragraph(self, text):
    """ Returns a paragraph, which coincidentally, is a description of Lyntin."""
    output = ("Lyntin is a mud client that is written in Python and uses\n" +
             "Python as a scripting language. It strives to be functionally\n" +
             "similar to TinTin++ while enhancing that functionality with\n" +
             "the ability to call Python functions directly from the input\n" +
             "line. It has the advantage of being platform-independent and\n" +
             "has multiple interfaces as well--I use Lyntin at home with\n" +
             "the Tk interface as well as over telnet using the text\n" +
             "interface.")
    self.write(output)

  def handle_coloredline(self, text):
    """ Returns a series of lines with colored text."""
    output = "Notadragon is not a dragon.\n"
    output += "Notadragon is " + self.color("not", 32) + " a dragon.\n"
    output += "N" + self.color("otadragon", 35) + " is not a " + self.color("dragon.", 33) + "\n"
    output += "Beginning of line " + self.color("Hunted by: ", 35) + self.color("No-one", 37) + " rest of line."
    self.write(output)

  def handle_text(self, text):
    """ Returns 10 lines each with 10 random words in it."""
    response = ''
    for x in range(0,9):
      response += self.getWords(10) + "\n"
    self.write(response)

  def handle_spam(self, text):
    """ Starts the spam command."""
    # 1 = 1 line per sec, 2 = 5 lines per sec, 3 = 10 lines per sec
    text = text.split()
    
    try:
      newval = float(text[1])

      if self._spamFreq == 0 and newval > 0:
        self._spamThread = thread.start_new_thread(self.spam, ())

      self._spamFreq = newval
    except Exception, e:
      self._spamFreq = 0
      self.write("That's not an appropriate spam setting. %s\n" % e)

  def color(self, data, pcolor=37, backcolor=40, bold=0):
    """
    color(string,int,int,1/0)
    returns the string with designated colors on the front of it.
    """
    output = chr(27) + "["
    if bold==1:
      output += "1;"
    output += "%s;%sm" % (str(pcolor), str(backcolor))
    output += data
    output += chr(27) + "[0m"
    return output

  def getWords(self, numOfWords = 1):
    """
    words(string,int)
    writes int words to string with spaces
    """
    datam = ''
    for loop in range(0,numOfWords):
      num = int(random.random() * 29)
      datam += self._vocab[num] + " "
    return datam
  
  def spam(self):
    """
    spam()
    generates random 10 word lines per second
    """
    global shutdown
    while not shutdown and self._spamFreq > 0:
      time.sleep(self._spamFreq)

      # print spam
      self.write(self.getWords(10) + "\n")

    return
    
def handler(signum, frame):
  import sys
  global shutdown
  print "Quitting...."
  shutdown = 1
  sys.exit(0)


if __name__=='__main__':
  import signal
  server = SocketServer.ThreadingTCPServer(('', 3000), ConnectionHandler)
  print "Server is up on port 3000"
  signal.signal(signal.SIGINT, handler)
  server.serve_forever()
