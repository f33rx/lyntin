#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: exported.py,v 1.6 2002/04/05 23:55:46 willhelm Exp $
#######################################################################
"""
This is the API for lyntin internals and is guaranteed to change 
very rarely even though we might change Lyntin's internals.  If
it does change it'll be between major Lyntin versions.
"""
import engine, ui.ui

def lyntin_command(str):
  """
  The best way of executing a Lyntin command as if the user
  had typed it.

  arguments:

    'str' -- the command to execute.  ex. "#help"
  """
  get_engine().handleUserData(action)

def add_command(str, func):
  """ The best way to add commands to Lyntin.

  arguments:

    'str' -- the command name.  ex. "help"

    'func' -- the function to call when that command is executed.
  """
  get_engine().addCommand(str, func)

def get_commands():
  """ Returns a list of the commands currently bound.

  returns:

    list of strings
  """
  return get_engine().getCommands()

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

def write_ui(text, sess=None):
  """ Calls engine.myengine.writeUI which writes a message to the ui.

  arguments:

    'text' -- (string or ui.Message) the message to write 
              to the ui

    'session=None' -- (session.Session instance) the session the
                      mud data is associated with

  """
  if get_engine():
    get_engine().writeUI(text, session=sess)
  else:
    print text


def write_test(text, session=None):
  """ Calls engine.myengine.writeTest which writes TESTDATA message.

  arguments:

    'text' -- (string) the message to send

    'session=None' -- (session.Session instance) the session the
                      mud data is associated with

  """
  if get_engine():
    get_engine().writeUI(ui.ui.Message(text + "\n", ui.ui.TESTDATA, session))
  else:
    print "test:", text

def write_message(text):
  """ Calls engine.myengine.writeMessage which writes LTDATA message.

  arguments:

    'text' -- (string) the message to send

  """
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
  if get_engine():
    get_engine().writeUI(ui.ui.Message(text, ui.ui.MUDDATA, session))
  else:
    print "muddata:", text

def get_history():
  """ Retrieves the history as a oldest to youngest list of strings.

  returns:

    list of strings

  """
  return get_engine().getHistoryManager().getHistory()

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
