from scheduler import *
from exported import *

##################################################################
# example of using the time scheduler
# this is an event which prints something
class PrintEvent(TimeEvent):
    def __init__(self, printwhat='foo', interval=1, times=-1):
        TimeEvent.__init__(self, interval, times)
        self.printwhat = printwhat

    def internal_perform(self, scheduler):
        print self.printwhat

# uncomment these lines to test the time scheduler
# (will print foo once a second forever,
# and foo2 only twice, once a second)

#time_scheduler.add(PrintEvent())
#time_scheduler.add(PrintEvent('foo2', 1, 2))
##################################################################

class RepeatEvent(TimeEvent):
    def __init__(self, dowhat, interval=1,times=-1):
        TimeEvent.__init__(self,interval, times)
        self.dowhat=dowhat

    def internal_perform(self, scheduler):
        data.theapp.HandleUserInput(self.dowhat)

##################################################################
# example of a function which interacts with a mud through lyntin
# makes your character count to count, then say str
def count_then_say(count, str):
    for i in range(count):
        lyntin_command('say %d...'%i)
    lyntin_command('say %s'%str)
##################################################################


##################################################################
# use timedfileexecution to execute a file over a period of time
# time_scheduler.add(timedfileexecution('wearstuff.txt',1,3))
# the line above would cause you to read wearstuff.txt to the
# session in one second intervals sending 3 lines at a time
class timedfileexecution(TimeEvent):
    def __init__(self, filename, interval=1, linesatatime=1):
        self.linesatatime=linesatatime
        try:
            self.file = open(filename,'r')
        except:
            return 0
        else:
            TimeEvent.__init__(self, interval, -1)

    def internal_perform(self, scheduler):
        for i in range(self.linesatatime):
            line=self.file.readline()
            if line=='':
                scheduler.remove(self)
            else:
                lyntin_command(line)

##################################################################
# This class is used to time a command so that it happens so many
# seconds after the class is initialized.  Use like...
#   time_scheduler.add(afterexec('say hi',1))
# The previous python statement would cause "say hi" to be
# executed by lyntin (in lyntin_command) after 1 second.

class afterexec(TimeEvent):
    def __init__(self, command, after=1):
        self.command=command
        TimeEvent.__init__(self,after,1)
    
    def internal_perform(self, scheduler):
        lyntin_command(self.command)
        scheduler.remove(self)

##################################################################
# This is a very simple auto saver but can be dangerous to use if 
# a mud dies before you read in the old saved data.  A better 
# version will be available shortly :) -- James

def autosave_session_data(tuple):
    ses=tuple[0]
    n=ses.name
    lyntin_command("#showme Writing to %s;#write %s" % (n,n))

#uncomment the line below to add auto saving
#hooks.death_hook.add(autosave_session_data)

