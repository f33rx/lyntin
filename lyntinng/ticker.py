#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2001
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: alias.py,v 1.1.1.1 2001/12/01 04:27:46 willhelm Exp $
#######################################################################
"""
This module handles ticker data.
"""
import lyntin, event, engine

class Ticker:
   """ Manages ticker data."""
   def __init__(self):
      # duration between ticks
      self._ticklen = 2

      # how much before a tick we should warn
      self._tickwarn = 3

      # action that runs at the tick
      self._tickaction = ''

      # name of the session this ticker belongs to
      self._sessionname = ''

      # is this ticker enabled? 0 if no, 1 if yes
      self._enabled = 0

   def setTickLen(self, value):
      """ Sets the tick length.

      This is how often a tick occurs.

      i.e. if value was 4, then there would be a tick every 4 seconds.
      """
      self._ticklen = value

   def getTickLen(self):
      """ Returns the ticklength."""
      return self._ticklen

   def setTickWarn(self, value):
      """ Sets the tick warning length.

      You'll get a warning message this many seconds before
      the tick.
      """
      self._tickwarn = value

   def getTickWarn(self):
      """ Returns the tick warning length."""
      return self._tickwarn

   def setTickAction(self, action):
      """ Sets the tick action."""
      self._tickaction = action

   def getTickAction(self):
      """ Returns the tick action."""
      return self._tickaction

   def setSessionName(self, name):
      """ Sets the session name."""
      self._sessionname = name

   def getSessionName(self):
      """ Returns the session name."""
      return self._sessionname

   def enableTicker(self):
      """ Enables this ticker."""
      if self._enabled == 0:
         self._enabled = 1

         # register with the ticker frequency
         engine.myengine.register(engine.TIMERFREQ, self.tickerUpdate)

   def disableTicker(self):
      """ Disables this ticker."""
      if self._enabled == 1:
         self._enabled = 0
         engine.myengine.unregister(engine.TIMERFREQ, self.tickerUpdate)

   def tickerUpdate(self, args):
      """
      This gets called by the TIMERFREQ in the engine every
      second.  It figures out if this current second marks a tick
      or a tickwarning and does accordingly.
      """
      tick = args[0]

      # if this is a tick...
      if (tick % self._ticklen) == 0:
         input = lyntin.commandchar + self._sessionname + " " + self._tickaction
         event.InputEvent(input).enqueue()

      # if this is a tickwarn...
      if tick % self._ticklen == self._ticklen - self._tickwarn:
         pass
         engine.myengine.writeMessage("ticker: " +
               repr(self._tickwarn) + " seconds to tick!")

   def clearTicker(self):
      """
      Disables the ticker and clears the variables.
      """
      self.disableTicker()
      self._ticklen = 0
      self._tickwarn = 0
      self._tickaction = ''

   def getTickerInfo(self):
      """
      Pulls information about the ticker and returns a nice information
      string (if it's enabled).
      """
      if self._enabled == 1:
         return ("'" + self._tickaction + "' every " + 
                 repr(self._ticklen) + " seconds.")

      else:
         return "ticker is disabled."
