#!/usr/bin/env python
#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2001
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id$
#######################################################################
"""
This testserver just allows someone to test Lyntin without
actually connecting to a mud.  It's terribly non-interesting.
"""
import socket, string

RESPONSES = {'hello': 'Hello.',
             'commands': 'COMMANDS' }

def color(data):
   return chr(27) + "[33m" + data + chr(27) + "[0m"

def handle(addr, data):
   print "incoming: '" + data + "'"
   data = string.replace(data, "\r", "")
   data = string.replace(data, "\n", "")
   
   try:
      response = RESPONSES[data]
      response = string.replace(response, 
                 "COMMANDS", 
                 "commands available are: \r\n   " + string.join(RESPONSES.keys(), "\r\n   "))
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

