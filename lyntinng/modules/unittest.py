#######################################################################
# This file is part of Lyntin
# copyright (c) Will Guaraldi 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: unittest.py,v 1.8 2002/03/10 04:49:31 willhelm Exp $
#######################################################################
import string, traceback, sys
import utils, engine, exported

"""
This module holds one command (#test) and a series of helper functions
that allow you to unit test stuff.  Currently, all unit testing is
scripted in this module and it will likely remain so unless a 
nicer way is found that's as easy to deal with.

I'll add functionality as I need it here.

# FIXME - probably should use the unittest module Python provides
"""

# holds the lookup for tests and the list of commands and such
# that compose the test.
test_lookup = {
               'alias': ["print testing bracket handling."
                         "#alias bb cc",
                         "#alias bb {say cc}",
                         "#alias {test} {say $word",
                         "#alias {test} {say $word}",
                         "print testing printint out of aliases",
                         "#alias",
                         "#alias b*",
                         "print testing unaliasing",
                         "#unalias",
                         "#unalias bb*",
                         "#alias"],
               'gag': ["print testing bracketing",
                       "#gag this is good",
                       "#gag {this is bad",
                       "#gag this also is bad}",
                       "#gag {this is good}",
                       "print testing printing of gags",
                       "#gag",
                       "print testing ungag",
                       "#ungag",
                       "#ungag th*",
                       "#gag"],
               'substitute': ["print Requires being connected to a mud."
                              "print And see the word 'The'.",
                              "look",
                              "#sub The **THE**",
                              "look",
                              "#unsub The",
                              "look",
                              "print Testing bracket handling.",
                              "#sub {The} **THE**",
                              "#sub The **THE**",
                              "#sub {The*",
                              "#unsub",
                              "#unsub The*",
                              "#sub"],
               'variable': ["print This test requires a server connection.",
                            "print Use the testserver.py if you like.",
                            "#variable word hoobie",
                            "#variable word2 hobby",
                            "#alias {bb} {#showme $word}",
                            "bb",
                            "#variable",
                            "#variable wo*",
                            "#unvariable",
                            "#unvariable wo*",
                            "#variable"],
               'history': ["print testing history",
                           "#showme one two three four",
                           "#history",
                           "!1 two=2"],
               'etc': ["print Testing loops....",
                       "#5 #showme LOOP",
                       "#loop {1,3} {#showme %0 for the money!}"]
              }


def test_cmd(session, words, input):
  """ Implements the test command.

  '#test [<test>]'

  With no arguments, lists the tests available.
  With one argument, runs the test specified.

  #test only deals with registered test.  Registered tests come
  from the module--you can't register tests by commands.
  """
  if len(words) == 1:
    if len(test_lookup.keys()) > 0:
      list = test_lookup.keys()
      list.sort()
      data = ("Unit tests available:\n" + 
              utils.columnize(list, indent=3))
    else:
      data = "There are no tests registered."

    exported.write_message(data)
    return

  if words[1] == 'all':
    exported.write_test("Running all tests.")
    for mem in test_lookup.keys():
      run_test(test_lookup[mem])
    return

  if test_lookup.has_key(words[1]):
    exported.write_test("Running test: " + words[1])
    run_test(test_lookup[words[1]])
  else:
    exported.write_error("There is no test for '" + words[1] + "'")


def run_test(testsequence):
  """ Runs a test sequence."""
  exported.write_test("BEGINNING OF TEST.")
  for mem in testsequence:
    # we use print to allow tests to tell the user what they
    # should be looking for
    if mem.find("print") == 0:
      exported.write_test(mem.split(' ', 1)[1])
      continue

    exported.write_test("test: '" + mem + "'")
    # if it's not a print, then it's a lyntin command
    try:
      engine.myengine.handleUserData(input=mem, internal=1)
    except:
      exported.write_test("exception:\n" + 
         string.join(traceback.format_list(traceback.extract_tb()), '\n'))

  exported.write_test("END OF TEST.")


def load():
  """ Initializes the module by binding the commands."""
  exported.add_command("^test", test_cmd)
