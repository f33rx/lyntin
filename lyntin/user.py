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

import tkgui
tkgui.fgColorCodes = {
                "30": "#000000",
                "31": "#c00000",
                "32": "#00c000",
                "33": "#c0c000",
                "34": "#0000c0",
                "35": "#c000c0",
                "36": "#00c0c0",
                "37": "#c0c0c0",
                "2030": "#808080",
                "2031": "#ff6060",
                "2032": "#00ff00",
                "2033": "#ffff00",
                "2034": "#8080ff",
                "2035": "#ff40ff",
                "2036": "#00ffff",
                "2037": "#ffffff" }

tkgui.posixfont = ("Fixedsys", 24)

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
