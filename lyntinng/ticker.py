#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: ticker.py,v 1.15 2002/03/10 05:12:28 willhelm Exp $
#######################################################################
"""
This module handles ticker data.
"""
import hooks, lyntin, event, engine, exported

class Ticker:
  """ Manages ticker data."""
  def __init__(self):
    # duration between ticks
    self._ticklen = 2

    # how much before a tick we should warn
    self._tickwarn = 3

    # tickstart -- this is the tick that the ticker started on.
    # we use this for calculating the next tick.
    self._tickstart = 0

    # name of the session this ticker belongs to
    self._sessionname = ''

    # is this ticker enabled? 0 if no, 1 if yes
    self._enabled = 0

  def setTickLen(self, value):
    """ Sets the tick length.

    This is how often a tick occurs.  i.e. if value was 4, then 
    there would be a tick every 4 seconds.

    arguments: 

      'value' -- (int) the interval between ticks

    """
    self._ticklen = value

  def getTickLen(self):
    """ Returns the ticklength.

    returns:

      (int) the interval between ticks.

    """
    return self._ticklen

  def setTickWarn(self, value):
    """ Sets the tick warning length.

    You'll get a warning message this many seconds before
    the tick.

    arguments:

      'value' -- the number of seconds before the tick to do 
                 the warning

    """
    self._tickwarn = value

  def getTickWarn(self):
    """ Returns the tick warning length.

    returns:

      (int) the number of seconds to warn before

    """
    return self._tickwarn

  def getTickStart(self):
    """ Returns the tick start time.

    returns:

      (int) when this ticker was started

    """
    return self._tickstart

  def setSessionName(self, name):
    """ Sets the session name.

    arguments:

      'name' -- the name of the session that owns this ticker

    """
    self._sessionname = name

  def getSessionName(self):
    """ Returns the session name.

    returns:

      session name string

    """
    return self._sessionname

  def isEnabled(self):
    """ 
    Allows other parts of Lyntin to query whether the ticker
    is enabled or not.

    returns:

      (int) 0 if no, 1 if yes
    """
    return self._enabled

  def enableTicker(self):
    """ Enables this ticker.

    Has the side-effect of setting the self._tickstart variable
    as well--this essentially enables tickers as well as resets
    them.
    """
    if self._enabled == 0:
      self._enabled = 1

      # register with the ticker hook 
      hooks.timer_hook.register(self.tickerUpdate)

    self._tickstart = engine.myengine.getCurrentTick() - 1

  def disableTicker(self):
    """ Disables this ticker."""
    if self._enabled == 1:
      self._enabled = 0
      hooks.timer_hook.unregister(self.tickerUpdate)

  def tickerUpdate(self, args):
    """
    This gets called by the timer_hook in the engine every
    second.  It figures out if this current second marks a tick
    or a tickwarning and does accordingly.

    arguments:

      'args' -- tuple containing the current tick

    """
    tick = args[0]

    ticksession = engine.myengine.getSession(self._sessionname)
    if ticksession:

      # if this is a tick...
      if ((tick - self._tickstart) % self._ticklen) == 0:
        tickaction = ticksession.getManager("alias").getAlias("TICK!!!")
        if tickaction:
          event.InputEvent(tickaction, session=ticksession).enqueue()
        else:
          exported.write_message("TICK!!!")

      # if this is a tickwarn...
      if ((tick - self._tickstart) % self._ticklen == 
              (self._ticklen - self._tickwarn)):
        exported.write_message("ticker: " +
              repr(self._tickwarn) + " seconds to tick!")

    else:
      # we kill this ticker because it belongs to a nonexistant 
      # session
      self.disableTicker()

  def clear(self):
    """
    Disables the ticker and clears the variables.
    """
    self.disableTicker()
    self._ticklen = 0
    self._tickwarn = 0

  def getInfo(self):
    """
    Pulls information about the ticker and returns a nice information
    string (if it's enabled).
    """
    if self._enabled == 1:
      return ("(size = " + repr(self._ticklen) + ") " +
              "(start = " + repr(self._tickstart) + ")")

    else:
      return "<none>"
