#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2001
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id$
#######################################################################
"""
The thread manager allows us to centralize the management of
all the threads in one place.  Just keeps track of them all--doesn't
really _do_ anything other than make sure they're all initialized
the same way.
"""
from threading import Thread

class ThreadManager:
   """ Manages threads.

   This centralizes thread creation so that we can keep track
   of which threads are running in Lyntin.
   """
   def __init__(self):
      self._threads = []

   def startThread(self, name, func):
      """
      Starts a thread with the name and func given and adds it to
      the list of threads the ThreadManager has started.
      Note: We keep track of threads in a list--so multiple 
      threads can have the same name if that makes a difference.
      """
      t = Thread(None, func)
      t.setDaemon(1)
      t.setName(name)
      t.start()
      self._threads.append(t)

   def checkThreads(self):
      """ Checks the status of all the threads in the thread list.

      Returns an array of strings.
      """
      data = []
      for mem in self._threads:
         data.append("   " + mem.getName() + " " + repr(mem.isAlive()))

      return data

