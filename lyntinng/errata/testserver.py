#!/usr/bin/env python
#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: testserver.py,v 1.3 2002/04/11 03:58:22 willhelm Exp $
#######################################################################
"""
This testserver just allows someone to test Lyntin without
actually connecting to a mud.  It's terribly non-interesting.
"""
import socket, string

RESPONSES = {'hello': 'Hello.',
             'commands': 'COMMANDS',
             'colors' : 'Colors' }

def color(data, pcolor=33, backcolor=40):
  if pcolor < 100: 
    return ("%s[%s;%sm%s" % (chr(27), str(pcolor), str(backcolor), data))
  else:
    return ("%s[1;%s;%sm%s" % (chr(27), str(pcolor), str(backcolor), data))

  
def handle(addr, data):
  print "incoming: '" + data + "'"
  data = string.replace(data, "\r", "")
  data = string.replace(data, "\n", "")
   

  try:
    response = RESPONSES[data]
    response = string.replace(response, 
               "COMMANDS", 
               "commands available are: \r\n   " + string.join(RESPONSES.keys(), "\r\n   "))

    #sends out a rainbow of all possible colors and backgrounds
    #with number of color called as text
    if response == "Colors":
     for background in range(40,48):
        response = response + "\n"
        for foreground in range(30,38):
          response += color(str(foreground), foreground, background)
          response += color(str((foreground + 100)), (foreground + 100), background)
        response += color("",37,40)
    
  except KeyError:
    response = "huh?"

  return (color(addr[0]) + ": " + response + "\r\n")

if __name__ == '__main__':
  host = 'localhost'
  port = 3000
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.bind((host, port))
  s.listen(1)
  print "test server starting up."
  while 1:
    conn, addr = s.accept()
    print "connected by", addr
    conn.send("Welcome!\r\n")
    while 1:
      try:
        data = conn.recv(1024)
        if not data: break
        conn.send(handle(addr, data))
      except:
        break

    print "closing", addr
    conn.close()
    conn = None
    addr = None
