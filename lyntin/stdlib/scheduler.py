##################################################################
# This file is part of Lyntin
# copyright (c) Lyn Headley 1996-2001
#
# Lyntin is distributed under the GNU General Public License.  See
# the file LICENSE in the distribution for details.
# $Id: scheduler.py,v 1.3 2001/08/06 02:00:19 willhelm Exp $
##################################################################
"""
schedules _events_ to be run at certain intervals, either a set
number of times or forever.
events are classes with the methods ready_to_perform and perform
the TimeEvent implements time-based events, which are scheduled
to run a certain number of times at certain intervals
override your time-based events from TimeEvent.
"""

import time

class Scheduler:
   def __init__(self):
      self.event_list = []

   def add(self, event):
      """
      add an event to the scheduler
      """
      self.event_list.append(event)
    
   def remove(self, event, all=1):
      """
      remove an event from the scheduler
      by default removes every copy of event we have
      to remove just the first, pass 0 as second arg
      """
      if all:
         try:
            while 1:
               self.event_list.remove(event)
         except ValueError:
            return
      else:
         self.event_list.remove(event)


   def perform_events(self):
      """
      called regularly to perform any events that are ready
      """
      todo = []

      # build a list of ready events
      for evt in self.event_list:
         if evt.ready_to_perform():
            todo.append(evt)

      # perform ready events
      for ready in todo:
         ready.perform(self)

   def __call__(self, tuple):
      """
      another way to check and invoke events regularly
      """
      self.perform_events()


class TimeEvent:
   """
   event class meant to be called at certain intervals
   derive your time-related events from this class
   """
   def __init__(self, interval=1, times=-1):
      """
      interval is the number of seconds between invocations
      times is the total number of invocations
      (< 1 means an unlimited number)
      """
      self.last_performed = time.time()
      self.interval = interval
      self.times = times

   def ready_to_perform(self):
      """
      time to perform the event?
      """
      if time.time() > (self.last_performed + self.interval):
         return 1
      return 0
        
   def perform(self, scheduler):
      """
      this is just a wrapper around the real functionality
      which checks times and deschedules if times is up
      """
      self.internal_perform(scheduler) # override
      if(self.times > 0):
         self.times = self.times - 1
         if self.times == 0: # all used up
            scheduler.remove(self)
      self.last_performed = time.time()

   def internal_perform(self, scheduler):
      """
      override this method to provide real functionality
      """
      pass

