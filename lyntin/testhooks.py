##################################################################
# This file is part of Lyntin
# copyright (c) Lyn Headley 1996-2001
#
# Lyntin is distributed under the GNU General Public License.  See
# the file LICENSE in the distribution for details.
# $Id$
##################################################################
"""
bunch of sample functions which we add to lyntin's hooks.
"""
import hooks

##################################################################
# here are a bunch of sample functions which we add to
# lyntin's hooks.
##################################################################

def death(tuple):
    deadses = tuple[0]
    print 'death hook: %s died'%deadses

def action(tuple):
    ses = tuple[0]
    line = tuple[1]
    response = tuple[2]
    print 'action hook: session %s'%ses
    print 'action hook: line %s'%line
    print 'action hook: response %s'%response

def data(tuple):
    buf = tuple[0]
    print 'data hook: databuffer has %d entries'%buf.size

def setses(tuple):
    old = tuple[0]
    new = tuple[1]
    print 'setses hook: old is %s'%old
    print 'setses hook: new is %s'%new
    
def shutdown(tuple):
    print 'shutting down!'

def received_user_input(tuple):
    input = tuple[0]
    print 'you just typed %s!'%input

def default(tuple):
    print 'arg tuple contains %d arguments'%len(tuple)

def connect(tuple):
    print 'name: %s, host: %s, port: %d'%(tuple[0], tuple[1], tuple[2])

##################################################################
# register the hooks with lyntin
##################################################################

def add_hooks():
    hooks.death_hook.add(death)
    hooks.action_hook.add(action)
#    hooks.data_hook.add(data)
    hooks.set_session_hook.add(setses)
    hooks.shut_down_lyntin_hook.add(shutdown)
    hooks.received_user_input_hook.add(received_user_input)
    hooks.exec_user_code_hook.add(default)
    hooks.action_command_hook.add(default)
    hooks.alias_command_hook.add(default)
    hooks.clear_command_hook.add(default)
    hooks.cr_command_hook.add(default)
    hooks.databuffer_command_hook.add(default)
    hooks.datagrep_command_hook.add(default)
    hooks.datagreplines_command_hook.add(default)    
    hooks.gag_command_hook.add(default)
    hooks.history_command_hook.add(default)
    hooks.killall_command_hook.add(default)
    hooks.log_command_hook.add(default)
    hooks.read_command_hook.add(default)
    hooks.session_command_hook.add(default)
    hooks.showme_command_hook.add(default)
    hooks.substitute_command_hook.add(default)
    hooks.speedwalk_command_hook.add(default)
    hooks.unaction_command_hook.add(default)
    hooks.textin_command_hook.add(default)
    hooks.unalias_command_hook.add(default)
    hooks.ungag_command_hook.add(default)
    hooks.unsubstitute_command_hook.add(default)
    hooks.variable_command_hook.add(default)
    hooks.write_command_hook.add(default)
    hooks.connect_failed_hook.add(connect)
    hooks.connect_succeeded_hook.add(connect)    
