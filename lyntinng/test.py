#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: test.py,v 1.2 2002/07/17 01:21:58 willhelm Exp $
#######################################################################
"""
This module has its own main method.  It's used to unit test functions in
Lyntin.
"""
def _pass_fail(testoutput, realoutput):
  """ Used for testing purposes."""
  if testoutput == realoutput:
    print "   pass:", testoutput
  else:
    print "   fail:", testoutput


if __name__ == '__main__':
  print "split_commands tests"
  from utils import split_commands
  _pass_fail(split_commands('test'), 
            ['test'])
  _pass_fail(split_commands('test;test2'), 
            ['test', 'test2'])
  _pass_fail(split_commands('#alias t3k #ses a localhost 3000'),
            ['#alias t3k #ses a localhost 3000'])
  _pass_fail(split_commands('#alias gv {put all in vortex;get all}'),
            ['#alias gv {put all in vortex;get all}'])
  _pass_fail(split_commands('#alias sv {put all in vortex;get all};test'),
            ['#alias sv {put all in vortex;get all}', 'test'])
  _pass_fail(split_commands(r'#showme \{ blah;#showme another }'), 
            [r'#showme \{ blah', r'#showme another }'])

  print 

  from utils import split_ansi_from_text
  _pass_fail(split_ansi_from_text("This is some text."),
            ["This is some text."])
  _pass_fail(split_ansi_from_text("\33[1;37mThis is\33[0m text."),
            ["\33[1;37m", "This is", "\33[0m", " text."])
  _pass_fail(split_ansi_from_text("Hi \33[1;37mThis is\33[0m text."),
            ["Hi ", "\33[1;37m", "This is", "\33[0m", " text."])
  _pass_fail(split_ansi_from_text("\33[1;37mThis is\33[0"),
            ["\33[1;37m", "This is", "\33[0"])

  print

  text = "This is a really long line to see if we're wrapping correctly.  Because it's way cool when we write code that works.  Yay!"

  from utils import wrap_text
  print wrap_text(text)
  print wrap_text(text, indent=5)
  print wrap_text(text, indent=5, firstline=1)

  text = "Hi.  Check this out: Thistexthasnospacesinitandmightcausethingstocrashorgointoaninfiniteloopandstuff.whichwouldbesuperbad.  What do you think?"
  print wrap_text(text)
  print wrap_text(text, indent=5)

  text = "This is some text \33[1;37mwith some\33[0m ansi formatting in it to see if we can handle wrapping with it \33[1;37mtoo.\33[0m"
  print wrap_text(text)
  print wrap_text(text, indent=5)

  """
  print "time parsing test"
  from utils import parse_timespan
  _pass_fail(parse_timespan("1h"), 3600)
  _pass_fail(parse_timespan("1m"), 60)
  _pass_fail(parse_timespan("1s"), 1)
  _pass_fail(parse_timespan("1h2m3s"), 3723)
  _pass_fail(parse_timespan("17"), 17)
  _pass_fail(parse_timespan("5h"), 3600 * 5)

  from utils import parse_time
  print parse_time("4:20p")
  print parse_time("4m")
  print parse_time("9")
  print parse_time("1:17:34a")

  from modules.alias import expand_placement_vars
  print "expand_placement_vars tests"
  print expand_placement_vars("#test 1 2 3", "#test")
  print expand_placement_vars("#test 1 2 3", "#test %1 %2")
  print expand_placement_vars("#test 1 2 3", "#test %0")
  print expand_placement_vars("#test 1 2 3", "#test %-1")
  print expand_placement_vars("#test 1 2 3", "#test %:-1")
  print expand_placement_vars("#test 1 2 3", "#test %1:-1")

  from modules.variable import expand_vars
  varmap = {"var1": "value1", "var2": "value2", "var3": "value3"}
  _pass_fail(expand_vars(r"This has no vars.", varmap), "This has no vars.")
  _pass_fail(expand_vars(r"$var1 $var2 $var3", varmap), "value1 value2 value3")
  _pass_fail(expand_vars(r"$var1 $$var2 \$var3", varmap), r"value1 $$var2 \$var3")
  """

# Local variables:
# mode:python
# py-indent-offset:2
# tab-width:2
# End:
