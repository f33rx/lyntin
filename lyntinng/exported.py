#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: exported.py,v 1.22 2002/06/20 03:23:27 willhelm Exp $
#######################################################################
"""
This is the API for lyntin internals and is guaranteed to change 
very rarely even though we might change Lyntin's internals.  If
it does change it'll be between major Lyntin versions.
"""
import engine, ui.ui, lyntin

def lyntin_command(text, internal=0, session=None):
  """
  The best way of executing a Lyntin command as if the user
  had typed it.

  arguments:

    'text' -- the command to execute.  ex. "#help"

    'internal=0' -- whether to execute it "internally" and suppress
                    various outputs

    'session=None' -- the session instance to execute this command
                      in (defaults to the current session)
  """
  if session != None:
    get_engine().handleUserData(text, internal, session)
  else:
    get_engine().handleUserData(text, internal)


def add_command(command, func, arguments=None, argoptions=None, helptext=""):
  """ The best way to add commands to Lyntin.

  arguments:

    'command' -- the command name.  ex. "help"

    'func' -- the function to call when that command is executed.

    'arguments=None' -- (string) the argument stuff for the argument parser.

    'argoptions=None' -- (string) options for how to parse the argument stuff.

    'helptext=""' -- (string) the help text for this command

  """
  get_engine().addCommand(command, func, arguments, argoptions, helptext)

def remove_command(str):
  """ Removes a command from Lyntin.

  arguments:

    'str' -- the command name.
  """
  get_engine().removeCommand(str)

def get_commands():
  """ Returns a list of the commands currently bound.

  returns:

    list of strings
  """
  return get_engine().getCommands()

def add_manager(name, mgr):
  """ Registers a manager with the engine.

  arguments:

    'name' -- (string) the name of the manager to register

    'mgr' -- (manager instance) the manager instance to register
  """
  get_engine().addManager(name, mgr)

def remove_manager(name):
  """ Removes a manager from the engine.

  argumnets:

    'name' -- (string) the name of the manager to remove
  """
  get_engine().removeManager(name)

def get_manager(name):
  """ Retrieves a manager from the engine.

  arguments:

    'name' -- (string) the name of the manager to retrieve
  """
  return get_engine().getManager(name)

def add_help(fqn, helptext):
  """ Adds a help topic to the structure.

  see corresponding helpmanager.HelpManager.addHelp method.

  arguments:

    'fqn' -- (string) a . delmited string of categories ending
             with a help name.

    'helptext' -- (string) the help text

  returns:

    (string) the fqn
  """
  return get_engine().getManager("help").addHelp(fqn, helptext)

def remove_help(fqn):
  """ Removes a help topic from Lyntin.

  arguments:

    'fqn' -- (string) a . delmited string of categories ending
             with a help name.
  """
  get_engine().getManager("help").removeHelp(fqn)

def get_help(fqn):
  """ Retrieves a help topic via a fully qualified name.

  arguments:

    'fqn' -- (string) a . delimited string of categories ending
             with a help name.
  """
  return get_engine().getManager("help").getHelp(fqn)

def get_session(name):
  """
  Returns a named session.

  arguments:

    'name' -- the name of the session to retrieve

  returns

    session.Session instance or None if it doesn't exist
  """
  return get_engine().getSession(name)

def get_active_sessions():
  """
  Returns a list of the active sessions.

  returns:

    list of session.Session instances
  """
  return get_engine()._sessions.values()

def get_current_session():
  """
  Returns the current session.

  returns:

    a session.Session instance
  """
  return get_engine().currentSession()

def set_current_session(session):
  """
  Changes the current session to another session.

  arguments:

    'session' -- a session.Session instance
  """
  # FIXME - should do some data checking on this first
  get_engine()._current_session = session
    
  
def get_num_errors():
  """
  Returns the total number of errors Lyntin has had thus far.

  returns:

    int
  """
  return lyntin.errorcount
 
def set_num_errors(num):
  """
  Sets the number of errors Lyntin has had thus far.  Do be careful
  when setting this because Lyntin keeps track of errors for a reason.

  arguments:

    'num' -- the number of errors to set
  """
  lyntin.errorcount = num

def write_ui(text):
  """ Calls engine.myengine.writeUI which writes a message to the ui.

  arguments:

    'text' -- (string or ui.Message) the message to write 
              to the ui

  """
  if get_engine():
    get_engine().writeUI(text)
  else:
    print text


def write_message(text):
  """ Calls engine.myengine.writeMessage which writes LTDATA message.

  arguments:

    'text' -- (string) the message to send

  """
  text = str(text)
  if get_engine():
    get_engine().writeUI(ui.ui.Message(text + "\n", ui.ui.LTDATA))
  else:
    print "message:", text

def write_error(text, session=None):
  """ Calls engine.myengine.writeError which writes ERROR message.

  arguments:

    'text' -- (string) the message to send

    'session=None' -- (session.Session instance) the session the
                      mud data is associated with

  """
  text = str(text)
  if get_engine():
    get_engine().writeUI(ui.ui.Message(text + "\n", ui.ui.ERROR, session))
  else:
    print "error:", text

def write_user_data(text, session=None):
  """ Calls engine.myengine.writeUserData which writes a USERDATA message.

  arguments:

    'text' -- (string) the message to send

    'session=None' -- (session.Session instance) the session the
                      mud data is associated with

  """
  text = str(text)
  if get_engine():
    get_engine().writeUI(ui.ui.Message(text + "\n", ui.ui.USERDATA, session))
  else:
    print "userdata:", text

def write_mud_data(text, session=None):
  """ Calls engine.myengine.writeMudData which writes a MUDDATA message.

  arguments:

    'text' -- (string) the message to send

    'session=None' -- (session.Session instance) the session the
                      mud data is associated with

  """
  text = str(text)
  if get_engine():
    get_engine().writeUI(ui.ui.Message(text, ui.ui.MUDDATA, session))
  else:
    print "muddata:", text

def get_history(count=30):
  """ Retrieves the history as a oldest to youngest list of strings.

  returns:

    list of strings

  """
  return get_engine().getManager("history").getHistory(count)

def grep_databuffer(str, session):
  """ Not yet implemented."""
  pass

def grep_databuffer_lines(str, session):
  """ Not yet implemented."""
  pass

def get_engine():
  """ Nice way of retrieving the engine instance.

  returns:

    engine.Engine instance

  """
  return engine.myengine

def tally_error():
  """
  This adds one to the current error count and checks to see
  if we're over our limit.  If we are, it enqueues a shutdown
  event which will shutdown Lyntin.
  """
  get_engine().tallyError()
