#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: ui.py,v 1.4 2002/02/04 01:10:17 willhelm Exp $
#######################################################################
"""
Holds the ui components in lyntin as well as the Message
class.  The Message class encapsulates a message to be displayed
to the user through the ui.  Messages have types and the ui
will display the message differently depending on the type.
"""
import string, re, sys
import engine, event, utils

ERROR = "ERROR: "
USERDATA = "USERDATA: "
MUDDATA = "MUDDATA: "
LTDATA = "LTDATA: "
TESTDATA = "TESTDATA: "

MESSAGETYPES = {ERROR: "ERROR: ",
                USERDATA: "USERDATA: ",
                MUDDATA: "MUDDATA: ",
                LTDATA: "LTDATA: ",
                TESTDATA: "TESTDATA: "}

class Message:
  """
  Encapsulates a message to be written to the user.
  """
  def __init__(self, data, messagetype=LTDATA):
    """ Initialize."""
    self.data = data
    self.type = messagetype

  def __repr__(self):
    """ Represents the message (returns data + type)."""
    return MESSAGETYPES[self.type] + repr(self.data)


class BaseUI:
  """ Base ui class.

  This is the Base UI class which defines the interface between
  the ui's and Lyntin.
  """
  def __init__(self):
    """ Initializes.

    If you have initializations to do, override this class,
    but call this function like this:

       'BaseUI.__init__(self)'
    """
    self.shutdownflag = 0
    engine.myengine.register(engine.SHUTDOWN_HOOK, self.shutdown)

  def startui(self):
    """ Initializes your user interface.

    It's best to do all your initialization logic in startui
    including the call to start whatever thread will handle
    polling for user input.
    """
    pass

  def write(self, message):
    """ Writes output to the user.

    Output can come from the mud, lyntin, or even user
    input being printed to the screen.  If the message
    argument is a String object rather than a Message
    object, the ui should assume it's Lyntin output.
    """
    pass

  def prompt(self):
    """ Prints a prompt to the user.

    This is mostly for niceties so the user knows that
    Lyntin is awaiting input.  It should just print
    a prompt.  Prompts only get printed by the common
    session.
    """
    pass

  def run(self):
    pass

  def shutdown(self, args):
    self.shutdownflag = 1

  def flush(self):
    pass

  def handleinput(self, input):
    event.InputEvent(input).enqueue()
