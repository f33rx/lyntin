##################################################################
# This file is part of Lyntin
# copyright (c) Lyn Headley 1996-2001
#
# Lyntin is distributed under the GNU General Public License.  See
# the file LICENSE in the distribution for details.
# $Id$
##################################################################
"""
A reactor is an event handler attached to an event
The reactor will simply be a scheduler attached to the databuffer
There needs to be a list of events, each with a *list* of actions,
as opposed to simply a list of events with *one* actions
could just make an event subclass, EventList, which has one
trigger and a list of actions

reactors must be session-private!

Why not just make action/alias sets?
ok, how?  everybody's got an active set list, you add actions/aliases to 
one set at a time, there is one default set.

new way to handle actions -- if a line is partially completed, check 
triggers, if any of them hit, take the ones that hit off
the list to check when the line completes.  when it completes, check 
the unspent triggers, then restore them all.

change the name of user.py to lt_user.py or perhaps .lyntin? <-- that one

maybe derive RegexMatcher, ExactMatcher from MatchEvent?
this would all go in exported
"""

matchEvent = MatchEvent(RegexMatcher(), EventList())
evt2 = foo()
matchEvent.get_event().append(evt2)
reactor = scheduler.Scheduler()
hooks.databuffer_hook.add(reactor)
