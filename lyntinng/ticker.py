#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: ticker.py,v 1.25 2003/01/01 00:36:25 willhelm Exp $
#######################################################################
"""
This module handles ticker stuff.  A session can have an associated
ticker which kicks off a ticker event every x seconds.  The ticker
works off of the "timer_hook".
"""
import lyntin, event, engine, exported

DEFAULT_LEN = 2
DEFAULT_WARN_LEN = 3

class Ticker:
  """
  Manages ticker data.
  """
  def __init__(self):
    global DEFAULT_LEN, DEFAULT_WARN_LEN

    # duration between ticks
    self._ticklen = DEFAULT_LEN

    # how much before a tick we should warn
    self._tickwarn = DEFAULT_WARN_LEN

    # tickstart -- this is the tick that the ticker started on.
    # we use this for calculating the next tick.
    self._tickstart = 0

    # name of the session this ticker belongs to
    self._sessionname = ''

    # is this ticker enabled? 0 if no, 1 if yes
    self._enabled = 0

  def setTickLen(self, value):
    """
    Sets the tick length.  This is how often a tick occurs.  i.e. if 
    value was 4, then there would be a tick every 4 seconds.

    @param value: the interval of seconds between ticks
    @type  value: int
    """
    self._ticklen = value

  def getTickLen(self):
    """
    Returns the ticklength.

    @returns: the tick length interval
    @rtype: int
    """
    return self._ticklen

  def setTickWarn(self, value):
    """
    Sets the tick warning length.  You'll get a warning message this 
    many seconds before the tick.

    @param value: the number of seconds before the tick to do the warning
    @type  value: int
    """
    self._tickwarn = value

  def getTickWarn(self):
    """
    Returns the tick warning length.

    @returns: the tick warning length
    @rtype: int
    """
    return self._tickwarn

  def getTickStart(self):
    """
    Returns the tick start time.

    @returns: at which tick the ticker was started--this is ticks since
        Lyntin start, not since the epoch
    @rtype: int
    """
    return self._tickstart

  def setSessionName(self, name):
    """
    Sets the session name.

    @param name: the session name
    @type  name: string
    """
    self._sessionname = name

  def isEnabled(self):
    """ 
    Allows other parts of Lyntin to query whether the ticker
    is enabled or not.

    @returns: 0 if the ticker is not enabled, and 1 if it is enabled
    @rtype: boolean
    """
    return self._enabled

  def enableTicker(self):
    """
    Enables this ticker if it's not currently enabled.  Has the side-effect 
    of setting the self._tickstart variable as well--this essentially 
    enables tickers as well as resets them.
    """
    if self._enabled == 0:
      self._enabled = 1

      # register with the ticker hook 
      exported.hook_register("timer_hook", self.tickerUpdate)

    self._tickstart = engine.myengine.getCurrentTick() - 1

  def disableTicker(self):
    """
    Disables this ticker.
    """
    if self._enabled == 1:
      self._enabled = 0
      exported.hook_unregister("timer_hook", self.tickerUpdate)

  def tickerUpdate(self, args):
    """
    This gets called by the timer_hook in the engine every
    second.  It figures out if this current second marks a tick
    or a tickwarning and does accordingly.

    @param args: the args sent by the timer_hook--should contain the
        current tick so we can figure out if we need to execute things
        or not.
    @type  args: tuple
    """
    tick = args[0]

    ticksession = engine.myengine.getSession(self._sessionname)
    if ticksession:

      # if this is a tick...
      if ((tick - self._tickstart) % self._ticklen) == 0:
        tickaction = ""
        am = exported.get_manager("alias")
        if am:
          tickaction = am.getAlias(ticksession, "TICK!!!")
        if not tickaction:
          tickaction = am.getAlias(ticksession, "TICK")

        if tickaction:
          event.InputEvent(tickaction, internal=1, ses=ticksession).enqueue()
        else:
          exported.write_message("TICK!!!")

      # if this is a tickwarn...
      if ((tick - self._tickstart) % self._ticklen == 
              (self._ticklen - self._tickwarn)):

        tickaction = ""
        am = exported.get_manager("alias")
        if am:
          tickaction = am.getAlias(ticksession, "TICKWARN!!!")
        if not tickaction:
          tickaction = am.getAlias(ticksession, "TICKWARN")

        if tickaction:
          event.InputEvent(tickaction, internal=1, ses=ticksession).enqueue()

        exported.write_message("ticker: %d seconds to tick!" % self._tickwarn)


    else:
      # we kill this ticker because it belongs to a nonexistant 
      # session
      self.disableTicker()

  def clear(self):
    """
    Disables the ticker and clears the variables.
    """
    global DEFAULT_LEN, DEFAULT_WARN_LEN

    self.disableTicker()
    self._ticklen = DEFAULT_LEN
    self._tickwarn = DEFAULT_WARN_LEN

  def getInfo(self):
    """
    Pulls information about the ticker and returns a nice information
    string (if it's enabled).

    @returns: a string giving the Ticker status
    @rtype: string
    """
    if self._enabled == 1:
      return "(size = %d) (warn = %d) (start = %d)" % (self._ticklen, self._tickwarn, self._tickstart)
    else:
      return "<none>"

# Local variables:
# mode:python
# py-indent-offset:2
# tab-width:2
# End:
