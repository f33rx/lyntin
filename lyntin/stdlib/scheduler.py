##################################################################
# This file is part of Lyntin
# copyright (c) Lyn Headley 1996-1998
#
# Lyntin is distributed under the GNU General Public License.  See
# the file COPYING for details.
#
# module scheduler contains the scheduler class:
# schedules _events_ to be run at certain intervals, either a set
# number of times or forever.
# events are classes with the methods ready_to_perform and perform
# the TimeEvent implements time-based events, which are scheduled
# to run a certain number of times at certain intervals
# override your time-based events from TimeEvent
##################################################################

import time

class Scheduler:
    def __init__(self):
        self.event_list = []

    # add an event to the scheduler
    def add(self, event):
        self.event_list.append(event)
    
    # remove an event from the scheduler
    # by default removes every copy of event we have
    # to remove just the first, pass 0 as second arg
    def remove(self, event, all=1):
        if all:
            try:
                while 1:
                    self.event_list.remove(event)
            except ValueError:
                return
        else:
            self.event_list.remove(event)


    # called regularly to perform any events that are ready
    def perform_events(self):
        todo = []

        # build a list of ready events
        for evt in self.event_list:
            if evt.ready_to_perform():
                todo.append(evt)

        # perform ready events
        for ready in todo:
            ready.perform(self)

    # another way to check and invoke events regularly
    def __call__(self, tuple):
        self.perform_events()


# event class meant to be called at certain intervals
# derive your time-related events from this class
class TimeEvent:
    # interval is the number of seconds between invocations
    # times is the total number of invocations
    # (< 1 means an unlimited number)
    def __init__(self, interval=1, times=-1):
        self.last_performed = time.time()
        self.interval = interval
        self.times = times

    # time to perform the event?
    def ready_to_perform(self):
        if time.time() > (self.last_performed + self.interval):
            return 1
        return 0
        
    # this is just a wrapper around the real functionality
    # which checks times and deschedules if times is up
    def perform(self, scheduler):
        self.internal_perform(scheduler) # override
        if(self.times > 0):
            self.times = self.times - 1
            if self.times == 0: # all used up
                scheduler.remove(self)
        self.last_performed = time.time()

    # override this method to provide real functionality
    def internal_perform(self, scheduler):
        pass

