#!/usr/bin/env python
#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: lyntin.py,v 1.13 2002/03/29 18:09:59 willhelm Exp $
#######################################################################
"""
This module holds the Lyntin "global variables" and constants as well
as the main function which starts Lyntin off.
"""

# lyntin's title and catch phrase
LYNTINTITLE = "Lyntin -- The Hacker's Mudclient "

# version information
VERSION = """Lyntin version 3.0 beta 1
For bugs, suggestions, mailing list info, feature requests,
architecture docs, et al, see http://lyntin.sourceforge.net/
"""

# help text which gets printed to stdout if you do 'Lyntin.py --help'
HELPTEXT = """syntax: Lyntin.py [--help] [--readfile <file>] [--datadir <dir>] [--ui <ui>]

  --help
         displays this text and exits.

  --datadir
         If you don't set your datadir, Lyntin will set the datadir to
         the HOME environment variable.  Using this option allows you to
         set it manually.

  --readfile
         reads a file in at startup populating the common
         session with aliases, actions, and whatnot.

  --ui
         launches a specific ui for Lyntin.  current options
         are 'text', 'tk', and 'curses'.
"""

# the wizlist of folks without whom Lyntin wouldn't exist.
WIZLIST = """This is the wizlist--people who have worked to bring you Lyntin:
Lyn Headley    - he who wrote the first Lyntin
Will Guaraldi  - he who took it over, debugged a bit, and wrote Lyntin 3.0
Sebastian John - helped with Lyntin 3.0 by testing, code submissions, 
                 and peer-rview
"""

# bosstext - code derived from the original Lyntin
BOSSTEXT = """
      hooks.too_many_errors_hook.add(abort_due_to_errors)
      sys.path.append(data.initdir + 'stdlib')

        
   def PreHandleUserInput(self, input):
      \"""
      Do stuff that we want to do one time for each command, like
      registering the command in the history list.
      We can't do this in HandleUserInput because it is recursive
      \"""
      if input == '\\n':
          self.SendPlainInput('\\r')

      elif input:
          self.RecordHistory(input)

          # run the received_user_input hook
          newinput = strip_final_elt_if(input, ['\\r', '\\n'])
          hooks.received_user_input_hook.run((newinput,))

          # send it along to the recursive workhorse
          self.HandleUserInput(input)


   def HandleUserInput(self, input):
      \"""
      The main "eval" command for Lyntin.  This function is
      recursive.
      \"""
      if not input:
"""

# holds the application options--these are adjusted
# by command-line arguments only
options = {'ui': 'textui', 'readfile': '', 'datadir': ''}

# the character used to denote variables.
variablechar = '$'

# the character used to denote commands
commandchar = '#'

# whether or not we do speedwalking checks
# 1 if yes, 0 if no
speedwalk = 1

# whether or not we whack all the ansi stuff for incoming
# mud data.
ansicolor = 1

# this is the data directory.  if it isn't overriden,
# then this is the directory that everything will be pulled
# from.
datadir = "./"

# this is the lyntin directory--where all the help files and
# such are located.
lyntindir = "."

# Lyntin counts the total number of errors it's encountered.
# This enables us to shut ourselves down if we encounter too
# many indicating a "bigger problem".
errorcount = 0

if __name__ == '__main__':
  try:
    import sys, os, getopt
    import lyntin, engine, event

    # figure out where the lyntin files are
    tmp = sys.argv[0]
    if len(tmp) == 0:
      raise Exception, "Lyntin root dir cannot be determined."
    lyntin.lyntindir = tmp[:tmp.rfind("/")+1].replace("/", os.sep)

    # read through options and arguments
    optlist, args = getopt.getopt(sys.argv[1:], 
                                  'u:r:d:vh',
                                  ['ui=', 
                                   'readfile=', 
                                   'datadir=', 
                                   'help', 
                                   'version'])

    for mem in optlist:
      if mem[0] == '--ui' or mem[0] == '-u':
        lyntin.options['ui'] = mem[1]

      elif mem[0] == '--readfile' or mem[0] == '-r':
        lyntin.options['readfile'] = mem[1]

      elif mem[0] == '--datadir' or mem[0] == '-d':
        if mem[1][-1] != os.sep:
          lyntin.options['datadir'] = mem[1] + os.sep
        else:
          lyntin.options['datadir'] = mem[1]

      elif mem[0] == '--help':
        print HELPTEXT
        sys.exit(0)

      elif mem[0] == '--version':
        print VERSION
        sys.exit(0)

    # if they haven't set the datadir via the command line, then
    # we go see if they have a HOME in their environment variables....
    if lyntin.options['datadir'] == '':
      if os.environ.has_key("HOME"):
        datadir = os.environ["HOME"]
        if len(datadir) > 0:
          if datadir[-1] != os.sep: 
            datadir = datadir + os.sep
          lyntin.options['datadir'] = datadir


    # instantiate an engine
    engine.myengine = engine.Engine()
    engine.myengine.initialize()

    # generate a startup event.
    # StartupEvent handles all the rest of the initialization
    # including parsing command-line arguments and such.
    event.StartupEvent(sys.argv).enqueue()

    # start the engine which will execute the startupevent
    # and start executing.
    engine.myengine.runengine()

  except SystemExit:
    if engine.myengine != None:
      event.ShutdownEvent().enqueue()
      engine.myengine.runengine()
    
  except:
    import traceback
    traceback.print_exc()
    sys.exit(1)
