#!/usr/bin/env python
#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: lyntin.py,v 1.27 2002/07/12 00:11:56 willhelm Exp $
#######################################################################
"""
This module holds the Lyntin "global variables" and constants as well
as the main function which starts Lyntin off.
"""

# lyntin's title and catch phrase
LYNTINTITLE = "Lyntin -- The Hacker's Mudclient "

# version information
VERSION = """Lyntin version 3.0 alpha 4
For bugs, suggestions, mailing list info, feature requests,
architecture docs, et al, see http://lyntin.sourceforge.net/
"""

# help text which gets printed to stdout if you do 'Lyntin.py --help'
HELPTEXT = """syntax: lyntin.py [--help] [--read <file>] [--datadir <dir>] [--ui <ui>] [--version]

  --help
         displays this text and exits.

  --datadir or -d
         If you don't set your datadir, Lyntin will set the datadir to
         the HOME environment variable.  Using this option allows you to
         set it manually.

  --evalmode or -e
         Lyntin has two user input evaluation modes: lyntin and tintin.
         This allows you to set the mode at the command line.

  --read or --readfile or -r
         reads a file in at startup populating the common
         session with aliases, actions, and whatnot.

  --ui or -u
         launches a specific ui for Lyntin.  current options
         are 'text', 'tk', and 'curses'.

  --version or -v
         prints out the version information and exits.
"""

# the wizlist of folks without whom Lyntin wouldn't exist.
WIZLIST = """This is the wizlist--people who have worked to bring you Lyntin:
Lyn Headley, Will Guaraldi, James, Aquarius, Sebastian John, Joshua Berne
Brian Bell
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



TINTIN = 0
LYNTIN = 1

# holds the application options--these are adjusted
# by command-line arguments only
options = {'ui': 'textui', 'readfile': [], 'datadir': '', 'evalmode': LYNTIN}

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

# whether or not we're echoing user input to the ui
mudecho = 1

# this is the data directory.  if it isn't overriden,
# then this is the directory that everything will be pulled
# from.
datadir = "./"

# Lyntin counts the total number of errors it's encountered.
# This enables us to shut ourselves down if we encounter too
# many indicating a "bigger problem".
errorcount = 0

# Lyntin has two modes for user input evaluation.  TINTIN mode
# will evaluate user input just like TINTIN does.  LYNTIN mode
# evaluates user input using different semantics.  We default
# to LYNTIN mode.
evalmode = LYNTIN

def shutdown():
  import hooks, exported
  try:
    exported.write_message("shutting down...  goodbye.")
  except:
    print "shutting down...  goodbye."
  hooks.shutdown_hook.spamhook()

if __name__ == '__main__':
  try:
    import sys, os
    import lyntin, engine, event, utils

    # read through options and arguments
    optlist = utils.parse_args(sys.argv[1:])

    for mem in optlist:
      if mem[0] == '--ui' or mem[0] == '-u':
        lyntin.options['ui'] = mem[1]

      elif mem[0] == '--readfile' or mem[0] == "--read" or mem[0] == '-r':
        lyntin.options['readfile'].append(mem[1])

      elif mem[0] == '--datadir' or mem[0] == '-d':
        if mem[1][-1] != os.sep:
          lyntin.options['datadir'] = mem[1] + "/"
        else:
          lyntin.options['datadir'] = mem[1]

      elif mem[0] == '--evalmode' or mem[0] == '-e':
        if mem[1] == 'tintin':
          lyntin.options['evalmode'] = TINTIN
        else:
          lyntin.options['evalmode'] = LYNTIN

      elif mem[0] == '--help':
        print HELPTEXT
        sys.exit(0)

      elif mem[0] == '--version':
        print VERSION
        sys.exit(0)

      else:
        opt = mem[0]
        while len(opt) > 0 and opt[0] == "-":
          opt = opt[1:]

        if len(opt) > 0:
          if lyntin.options.has_key(opt):
            lyntin.options[opt].append(mem[1])
          else:
            lyntin.options[opt] = [mem[1]]

    # if they haven't set the datadir via the command line, then
    # we go see if they have a HOME in their environment variables....
    datadir = lyntin.options['datadir']
    if datadir == '':
      if os.environ.has_key("HOME"):
        datadir = os.environ["HOME"]
        if len(datadir) > 0:
          if datadir[-1] != os.sep: 
            datadir = datadir + os.sep

    lyntin.options['datadir'] = datadir.replace("/", os.sep)

    # set the lyntin evalmode
    lyntin.evalmode = lyntin.options['evalmode']

    import atexit
    atexit.register(lyntin.shutdown)

    # instantiate an engine
    engine.myengine = engine.Engine()
    engine.myengine.initialize()

    # generate a startup event.
    # StartupEvent handles all the rest of the initialization
    # including parsing command-line arguments and such.
    event.StartupEvent().enqueue()

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

# Local variables:
# mode:python
# py-indent-offset:2
# tab-width:2
# End:
