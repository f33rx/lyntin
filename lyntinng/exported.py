#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: exported.py,v 1.1 2002/02/23 21:11:24 willhelm Exp $
#######################################################################
"""
This is the easy module programmers interface and is guaranteed
not to change even though we might change Lyntin's internals.
"""
import engine, ui.ui

def lyntin_command(str):
  """
  The best way of executing a Lyntin command as if the user
  had typed it.

  arguments:

    'str' -- the command to execute.  ex. "#help"
  """
  pass

def lyntin_add_command(str, func):
  """
  The best way to add commands to Lyntin.

  arguments:

    'str' -- the command name.  ex. "help"

    'func' -- the function to call when that command is executed.
  """
  pass

def lyntin_get_commands():
  """
  Returns a list of the commands currently bound.

  returns:

    list of strings
  """
  pass

def get_session(sesname):
  """
  Returns a named session.

  arguments:

    'sesname' -- the name of the session to retrieve

  returns

    session.Session instance or None if it doesn't exist
  """
  pass

def get_active_sessions():
  """
  Returns a list of the active sessions.

  returns:

    list of session.Session instances
  """
  pass

def get_current_session():
  """
  Returns the current session.

  returns:

    a session.Session instance
  """
  pass

def set_current_session(session):
  """
  Changes the current session to another session.

  arguments:

    'session' -- a session.Session instance
  """
  pass
  
def get_num_errors():
  """
  Returns the total number of errors Lyntin has had thus far.

  returns:

    int
  """
  pass
 
def set_num_errors(num):
  """
  Sets the number of errors Lyntin has had thus far.  Do be careful
  when setting this because Lyntin keeps track of errors for a reason.

  arguments:

    'num' -- the number of errors to set
  """
  pass

def write_ui(text):
  """ Calls engine.myengine.writeUI which writes a message to the ui.

  arguments:

    'text' -- (string or ui.Message) the message to write 
              to the ui

  """
  engine.myengine.writeUI(text)


def write_test(text):
  """ Calls engine.myengine.writeTest which writes TESTDATA message.

  arguments:

    'text' -- (string) the message to send

  """
  engine.myengine.writeUI(ui.ui.Message(text, ui.ui.TESTDATA))

def write_message(text):
  """ Calls engine.myengine.writeMessage which writes LTDATA message.

  arguments:

    'text' -- (string) the message to send

  """
  engine.myengine.writeUI(ui.ui.Message(text, ui.ui.LTDATA))

def write_error(text):
  """ Calls engine.myengine.writeError which writes ERROR message.

  arguments:

    'text' -- (string) the message to send
  """
  engine.myengine.writeUI(ui.ui.Message(text, ui.ui.ERROR))

def write_user_data(text):
  """ Calls engine.myengine.writeUserData which writes a USERDATA message.

  arguments:

    'text' -- (string) the message to send
  """
  engine.myengine.writeUI(ui.ui.Message(text, ui.ui.USERDATA))

def write_mud_data(text):
  """ Calls engine.myengine.writeMudData which writes a MUDDATA message.

  arguments:

    'text' -- (string) the message to send

  """
  engine.myengine.writeUI(ui.ui.Message(text, ui.ui.MUDDATA))

def get_history():
  pass

def set_history(list):
  pass

def grep_databuffer(str, session):
  pass

def grep_databuffer_lines(str, session):
  pass

def get_engine():
  """ Nice way of retrieving the engine instance.

  returns:

    engine.Engine instance

  """
  return engine.myengine
