#!/usr/bin/env python
#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: testserver.py,v 1.7 2002/04/30 02:53:46 willhelm Exp $
#######################################################################
# originally written by Brian Bell <bmbell@yahoo.com> 
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

    self._commands = {}
    self._commands["quit"] = self.handle_quit
    self._commands["command"] = self.handle_command
    self._commands["remember"] = self.handle_remember
    self._commands["repeat"] = self.handle_repeat
    self._commands["help"] = self.handle_command
    self._commands["colors"] = self.handle_colors
    self._commands["word"] = self.handle_word
    self._commands["line"] = self.handle_line
    self._commands["text"] = self.handle_text
    self._commands["spam"] = self.handle_spam

    self._rlist = [self.request]

    self._spamThread = None

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
      self.request.setblocking(0)
      data = ''
      while shutdown == 0:
        #check to see what is ready on the socket
        conns = select.select([self.request], [], [], 0)[0]

        for mem in conns:
          #lets get the message
          data += self.request.recv(1024)

          if data.find("\n") != -1:
            message = data[:data.find("\n")-1]
            print "incoming: '%s'" % message
            self.messageHandler(message)
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
    if self._commands.has_key(comm):
      self._commands[comm](text)
    else:
      # CATCH ALL for bad commands
      self.write(self.color("huh?", 33) + "\n")
    self.write(self.color(time.ctime() + " <" + str(time.clock()) + ">",32,40) + "\n")

  def handle_quit(self, text):
    # QUIT command -> ends session 
    self.write("bye bye\n")
    raise ValueError, "Shutdown of connection requested."
    
  def handle_remember(self, text):
    # REMEMBER command
    self._myline = text[text.find(" ")+1:]

  def handle_repeat(self, text):
    self.write(self._myline + "\n")

  def handle_command(self, text):
    # COMMAND command -> see startup for adding new commands
    self.write(string.join(self._commands, "\n") + "\n")

  def handle_colors(self, text):
    # COLORS command -> puts out 8 lines with all the colors displayed
    response = ''
    for background in range(40,48):
      for foreground in range(30,38):
        response += self.color(str(foreground), foreground, background)
        response += self.color(str(foreground), foreground, background, 1)
      response += "\n"

    self.write(response)

  def handle_word(self, text):
    # WORD command -> returns one random word
    response = ''
    response = self.getWords(1) + "\n"
    self.write(response)

  def handle_line(self, text):
    # LINE command -> returns 10 random words
    response = ''
    response = self.getWords(10) + "\n"
    self.write(response)
      
  def handle_text(self, text):
    # TEXT command -> returns 10 lines of 10 words
    response = ''
    for x in range(0,9):
      response += self.getWords(10) + "\n"
    self.write(response)

  def handle_spam(self, text):
    # SPAM command -> starts timed spam
    # 1 = 1 line per sec, 2 = 5 lines per sec, 3 = 10 lines per sec
    text = text.split()
    
    try:
      newval = int(text[1])

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
