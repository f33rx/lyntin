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
import hooks

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

def autosave_session_data(tuple):
    ses=tuple[0]
    n=ses.name
    lyntin_command("#showme Writing to %s;#write %s" % (n,n))

hooks.death_hook.add(autosave_session_data)
