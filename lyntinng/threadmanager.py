#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: threadmanager.py,v 1.3 2002/01/20 07:21:02 willhelm Exp $
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

    As an interesting side-effect this function also triggers
    the removal of dead threads from the list that we use to
    keep track of them.  We'll have at most one dead thread
    at any given time.
    """
    # clean up the list of threads that we maintain first
    self._threadCleanup()

    # create and initialize the new thread and stick it in our list
    t = Thread(None, func)
    t.setDaemon(1)
    t.setName(name)
    t.start()
    self._threads.append(t)

  def checkThreadsStatus(self):
    """ Checks the status of all the threads in the thread list.

    Returns an array of strings that detail our threads and their status.
    """
    data = []
    for mem in self._threads:
      data.append("   " + mem.getName() + " " + repr(mem.isAlive()))

    return data

  def _threadCleanup(self):
    """ Removes threads which have ended."""
    removeme = []
    for i in range(len(self._threads)):
      if self._threads[i].isAlive() == 0:
        removeme.append(self._threads[i])

    for mem in removeme:
      self._threads.remove(mem)
