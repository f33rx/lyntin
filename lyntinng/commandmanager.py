#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id$
#######################################################################
"""
Handles managing commands and also holds the filter for handling commands.
"""
import inspect, re
import manager, lyntin, exported, argparser

class CommandData:
  """
  Holds data relating to a command.  It's a helper class.
  """
  def __init__(self):
    self._name = ""
    self._func = None
    self._argparser = None
    self._fqn = ""

  def __repr__(self): return self._name
  def __str__(self): return self._name

  def setName(self, name): self._name = name
  def getName(self): return self._name
  def setNameAdjusted(self, name): self._name_adjusted = name
  def getNameAdjusted(self): return self._name_adjusted
  def setFunc(self, func): self._func = func
  def getFunc(self): return self._func
  def setArgParser(self, ap): self._argparser = ap
  def getArgParser(self): return self._argparser
  def setFQN(self, fqn): self._fqn = fqn
  def getFQN(self): return self._fqn

class CommandManager(manager.Manager):
  def __init__(self):
    self._commands = {}

  ### ------------------------------------------------
  ### Command functions
  ### ------------------------------------------------

  def getCommands(self):
    """
    Returns a list of the commands we have registered.

    returns:

      (list of strings) all the commands that have been registered

    """
    return self._commands.keys()

  def addCommand(self, name, func, arguments=None, argoptions=None, helptext=""):
    """
    Registers a command.

    arguments:

      'name' -- (string) the command to add

      'func' -- (function) the function that handles it

      'arguments=None' -- (string) argument specification to create 
                          the argparser

      'argoptions=None' -- (string) options for how the argument spec
                           should be parsed

      'helptext=""' -- (string) the help text for this command
      
    """
    if not callable(func):
      raise ValueError, "%s is uncallable." % name

    cd = CommandData()

    syntaxline = ""

    # try to figure out the arguments and syntax line stuff
    if arguments != None:
      try:
        cd.setName(name)
        cd.setArgParser(argparser.ArgumentParser(arguments, argoptions))
        syntaxline = cd.getArgParser().syntaxline
      except Exception, e:
        raise Exception, "Error with arguments for command %s, (%s)" % (name,e)

    # add the command to the command list
    cd.setFunc(func)

    # toss the command thing in the list
    self._commands[name] = cd

    # deal with the help text
    if not helptext:
      if func.__doc__:
        helptext = inspect.getdoc(func)
      else:
        helptext = "\nThis command has no help."

    if name[0] == "^":
      cd.setNameAdjusted(name[1:])
    else:
      cd.setNameAdjusted(name)

    if syntaxline:
      helptext = ("syntax: %s%s %s\n" % 
             (lyntin.commandchar, cd.getNameAdjusted(), syntaxline) + helptext)

    fqn = exported.add_help(cd.getNameAdjusted(), helptext)
    cd.setFQN(fqn)
        
  def removeCommand(self, name):
    """
    Removes a command (and the help text) for whatever reasons.

    arguments:

      'name' -- (string) the name of the command to remove

    """
    if self._commands.has_key(name):
      cd = self._commands[name]
      del self._commands[name]
      try:
        exported.remove_help(cd.getFQN())
      except:
        pass

  def getCommand(self, name):
    """
    Returns the function for a given command name.

    arguments:

      'name' -- (string) the name of the command to retrieve

    returns:

      (function) the function in question or None

    """
    if self._commands.has_key(name):
      return self._commands[name].getFunc()

    if self._commands.has_key("^" + name):
      return self._commands["^" + name].getFunc()

    # this is kind of a kluge to handle the #@ arbitrary
    # python stuff so that it can be in its own module.
    if name[0] == "@" and self._commands.has_key("@"):
      return self._commands["@"].getFunc()

    return None

  def getArgParser(self, name):
    """
    Returns the arguments parser for a given command name.

    arguments:

      'name' -- (string) the name of the command whose arguments should 
                be retrieved

    returns:

      (ArgParser) -- argument parsing object with parse(string) command 
                     to convert incoming arguments into a dictionary
      
    """
    if self._commands.has_key(name):
      return self._commands[name].getArgParser()

    return None

  def filter(self, args):
    ses = args[0]
    internal = args[1]
    input = args[-1]

    if len(input) > 1 and input[0] == lyntin.commandchar:
      input = input[1:]

      # splits out the command name from the rest of the command line
      words = input.split(" ",1)

      # We want an empty argument list if there was one, don't want
      # array out-of-bounds issues       
      if len(words) < 2: words.append("")

      # this checks to see if it's a special #@ command.
      if input[0] == "@":
        self.getCommand("@")(ses, input.split(" "), input)
        if internal==0: self.prompt()
        return

      # this finds the first matching command and ends there.
      commands = self.getCommands()
      commands.sort()
      for mem in commands:
        command = None
        if mem[0] == "^":
          if re.compile(mem).search(words[0]):
            command = self.getCommand(mem)
        else:
          if mem.find(words[0]) == 0:
            command = self.getCommand(mem)

        if command:
          argumentparser = self.getArgParser(mem)
          if argumentparser == None:
            command(ses, input.split(" "), input)
          else:
            try:
              dict = argumentparser.parse(words[1])
              dict["command"]=mem
              command(ses, dict, input)
            except ValueError, e:
              exported.write_error("%s: %s\nsyntax: %s%s %s" % 
                                   (mem, e, lyntin.commandchar, mem,
                                    argumentparser.syntaxline))
            except argparser.ParserException, e:
              exported.write_error("%s: %s\nsyntax: %s%s %s" % 
                                   (mem, e, lyntin.commandchar, mem,
                                    argumentparser.syntaxline))
          break

      else:
        exported.write_error("Not a valid command: %s" % (words[0]))
      return
    return args[-1]
