#!/usr/bin/env python
#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id$
#######################################################################
# originally written by Brian Bell<bmbell@yahoo.com> 
"""
This runs a multithreaded server on port 3000.
It used to test mud clients.  It currently take no arguments.
"""
import SocketServer, random, time, thread

class mudTester(SocketServer.StreamRequestHandler):
  """
  Basically this class gets created for every request.
  """
  def __init__(self, request, client_address, server):
    self._vocab = ['look', 'bleeding', 'door', 'cat', 'dog', 'naga',
           'doh!', 'horse', 'slashed', 'hurt', 'jumped', 'dodged',
           'says', 'tell', 'goblin', 'pink', 'crunch', 'smashed',
           'hungry', 'thirsty', 'huh?', 'glows', 'drop', 'blind',
           'to', 'the', 'of', 'broken', 'red', 'smoke']
    self._spamTime = 0.0
    self._spamFreq = 0
    self._lock = thread.allocate_lock()
    self._message = ''
    self._shutdown = 0
    SocketServer.StreamRequestHandler.__init__(self, request, client_address, server)

  def handle(self):
    """
    This is the function that gets called by the StreamRequestHandler object.
    """
    self.wfile.write(self.color("You're logged in.\n"))

    # tuple needed for thread
    lock = (self._lock,)

    # peel off thread for readline
    thread.start_new_thread(self.readInput, lock)

    # check for new message
    while 1:
      if not self._lock.locked():
        self._lock.acquire()
        if self._message:
          text = self._message
          self._message = ''
          self._lock.release()
          self.messageHandler(text)
          text = ''
        else:
          self._lock.release()
      self.spam()
      if self._shutdown:
        break

  def messageHandler(self, text):
    """
    messageHandler('the message read off readline')
    text is the message which is checked against the first 3 letters for
    a command match.
    """
    try:
      #prompt
      self.wfile.write(self.color(time.ctime() + " <" + str(time.clock()) + ">",32,40) + self.color("\n"))

      #QUIT command -> ends session 
      if text[0:3] == 'qui':
        self.wfile.write("bye bye\n")
        self._shutdown = 1
      #HELP command
      elif text[0:3] == 'hel':
        self.wfile.write("type commands for a list of commands\n")
      #COMMAND command -> please mention new commands in here
      elif text[0:3] == 'com':
        self.wfile.write("quit\nhelp\ncommands\ncolors\nword\nline\ntext\nspam <1-3>\n")
      #COLORS command -> puts out 8 lines with all the colors displayed
      elif text[0:3] == 'col':
        response = ''
        for background in range(40,48):
          for foreground in range(30,38):
            response += self.color(str(foreground), foreground, background)
            response += self.color(str((foreground + 100)), (foreground + 100), background)      
          response += self.color("\n",37,40)
        self.wfile.write(response)
      #WORD command -> returns one random word
      elif text[0:3] =='wor':
        response = ''
        response = self.getWords(1) + "\n"
        self.wfile.write(response)
      #LINE command -> returns 10 random words
      elif text[0:3] =='lin':
        response = ''
        response = self.getWords(10) + "\n"
        self.wfile.write(response)
      #TEXT command -> returns 10 lines of 10 words
      elif text[0:3] =='tex':
        response = ''
        for x in range(0,9):
          response += self.getWords(10) + "\n"
        self.wfile.write(response)
      #SPAM command -> starts timed spam
      # 1 = 1 line per sec, 2 = 5 lines per sec, 3 = 10 lines per sec
      elif text[0:3] =='spa':
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
      #CATCH ALL for bad commands
      elif text:
        self.wfile.write(self.color("huh?\n",33) + self.color(''))
    except:
      self._shutdown = 1
    return

  def color(self, data, pcolor = 37,backcolor = 40):
    """
    color(string,int,int)
    returns the string with designated colors on the front of it.
    """
    if pcolor < 100: 
      return chr(27) + "[" + str(pcolor) + "m" + chr(27) + "[" + str(backcolor) + "m" + data
    else:
      return chr(27) + "[1;" + str(pcolor - 100) + "m" + chr(27) + "[" + str(backcolor) + "m" + data

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
      #print spam
      self.wfile.write(self.getWords(10) + "\n")
      #set spam clock
      self._spamTime = time.clock() + (1 / self._spamFreq)
      return
    
  def readInput(self,lock):
    """
    readInput(truple)
    readInput runs on its own thread
    checks for input off rfile
    """
    while 1:
      try:
        text = self.rfile.readline(512)
        lock.acquire()
        self._message += text
        lock.release()
        if text[0:3] == 'qui':
          break
      except:
        #something wierd happened
        print "doh. dying NOW"
        thread.exit()
    #thread dies on return
    return
      
# ONLY one instance   
if __name__=='__main__':
  server=SocketServer.ThreadingTCPServer(('', 3000), mudTester)
  print "Server is up on port 3000"
  server.serve_forever()
