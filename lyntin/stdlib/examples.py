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



##################################################################
# example of a function which interacts with a mud through lyntin
# makes your character count to count, then say str
def count_then_say(count, str):
    for i in range(count):
        lyntin_command('say %d...'%i)
    lyntin_command('say %s'%str)
##################################################################
