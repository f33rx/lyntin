##################################################################
# module user
##################################################################
"""
this file is executed when lyntin starts up
users should initialize their environment, define functions,
etc here.
"""

# import predefined user functions into our own namespace
from exported import *
from scheduler import *
import hooks
import re

##################################################################
# variables you can set to customize lyntin's behavior
# do not delete them or change their datatypes!
##################################################################

user_custom = {
   'too_many_errors': 20,
   'history_size': 30,
   'extra_source_dirs': [],
   'lyntin_variable_char': '$'
}


##################################################################
# Insert your customizations here
##################################################################


# uncomment this line to use the examples
#from examples import *

def search_history(str):
   retl=[]
   hist=get_history()
   reg=re.compile(str)
   for n in hist:
      if reg.match(n):
         retl.append(n)
   return retl

