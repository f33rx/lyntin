#!/usr/bin/env python
#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: testserver.py,v 1.6 2002/04/29 23:14:13 willhelm Exp $
#######################################################################
# originally written by Brian Bell<bmbell@yahoo.com> 
"""
This runs a multithreaded server on port 3000.
It used to test mud clients.  It currently take no arguments.
"""
import SocketServer, random, time, thread, string

shutdown = 0

class ConnectionHandler(SocketServer.StreamRequestHandler):

  def setup(self):
    print "Connection from: " + repr(self.request)
    SocketServer.StreamRequestHandler.setup(self)
    self._vocab = ['look', 'bleeding', 'door', 'cat', 'dog', 'naga',
           'doh!', 'horse', 'slashed', 'hurt', 'jumped', 'dodged',
           'says', 'tell', 'goblin', 'pink', 'crunch', 'smashed',
           'hungry', 'thirsty', 'huh?', 'glows', 'drop', 'blind',
           'to', 'the', 'of', 'broken', 'red', 'smoke']
    self._spamTime = 0.0
    self._spamFreq = 0
    self._lock = thread.allocate_lock()
    self._message = ''
    self.myline = 'Default testserver line.'

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


  def write(self, data):
    data = data.replace("\n", "\r\n")
    self.request.send(data)

  def handle(self):
    """
    This is the function that gets called by the StreamRequestHandler object.
    """
    self.write(self.color("You're logged in.") + "\n")

    try:
      while shutdown == 0:
        # fixme - this needs to be non-blocking
        data = self.request.recv(1024)
        if not data:
          break
        data = data[:-2]
        print "incoming: '%s'" % data
        self.messageHandler(data)
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

    self.write(self.color(time.ctime() + " <" + str(time.clock()) + ">",32,40) + "\n")
    if self._commands.has_key(comm):
      self._commands[comm](text)
    else:
      # CATCH ALL for bad commands
      self.write(self.color("huh?", 33) + "\n")


  def handle_quit(self, text):
    # QUIT command -> ends session 
    self.write("bye bye\n")
    raise ValueError, "Shutdown of connection requested."
    
  def handle_remember(self, text):
    # REMEMBER command
    self.myline = text[text.find(" ")+1:]

  def handle_repeat(self, text):
    self.write(self.myline + "\n")

  def handle_command(self, text):
    # COMMAND command -> please mention new commands in here
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
    try:
      if text[5] == '1':
        self._spamFreq = 1
      elif text[5] == '2':
        self._spamFreq = 5
      elif text[5] == '3':
        self._spamFreq = 10
      elif text:
        self._spamFreq = 0
    except:
      self._spamFreq = 0

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
    if self._spamFreq == 0:
      return
    if self._spamTime > time.clock():
      return
    else:
      # print spam
      self.write(self.getWords(10) + "\n")
      # set spam clock
      self._spamTime = time.clock() + (1.0 / self._spamFreq)
      return
    
def handler(signum, frame):
  import sys
  global shutdown
  print "Quitting...."
  shutdown = 1
  sys.exit(0)


if __name__=='__main__':
  import signal
  server=SocketServer.ThreadingTCPServer(('', 3000), ConnectionHandler)
  print "Server is up on port 3000"
  signal.signal(signal.SIGINT, handler)
  server.serve_forever()
