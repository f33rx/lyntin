#!/usr/bin/python
#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: argparser.py,v 1.2 2002/04/21 20:20:45 willhelm Exp $
#######################################################################
"""
This provides the ArgumentParser class which parses command arguments
automatically into a dictionary.
"""
import string, re
import utils

defaultOptions={"stripBraces":1}
optionParser = None

class ArgumentParser:
  """
  This is the actual argumentparser class
  """
  
  def __init__(self,argspec,argoptions):
    self.typecheckers = { "string":stringChecker(), "int":intChecker() , "boolean":booleanChecker(), "booleanornone":booleanOrNoneChecker()}
    if argoptions:
      self.buildOptions(argoptions)
    else:
      self.options = defaultOptions.copy()
    self.buildParsers(argspec)
    return

  def getOption(self, optionname):
    if self.options.has_key(optionname):
      return self.options[optionname]
    else:
      return None

  

  def buildOptions(self,argoptions):
    """
    Set the options for this ArgumentParser
    key=value values in argoptions get put directly into self.options
    other values in argoptions get set to 1 in self.options.

    example:  argoptions="ignorall loud:boolean=true"
              self.options={"ignorall":1,"loud":1}

              argoptions="lalala wewewewe=hahaha"
              self.options={"lalala":1,"wewewewe"="hahaha"

    """
    self.argoptions=argoptions
    self.options=defaultOptions.copy()
    if optionParser == None:
      optionParser = ArgumentParser("otherOptions* otherValuedOptions*")
    dict = optionParser.parse(argoptions)

    for key in dict.keys():
      if key=="otherOptions":
        for otherOption in dict[key]:
          self.options[otherOption] = 1
      elif key=="otherValuedOptions":
        for otherKey in dict[key].keys():
          self.options[otherkey] = dict[key][otherkey]
      else:
        self.options[key] = dict[key]
    

  def buildParsers(self, argspec):
    """
    Build up the set of parsers to be used for argument parsing.

    The argspec follows the following format
    [argname[:argtype]]+ [:]
    [argname[:argtype]=defaultval]+ [:]
    [argname:argtype*] [:]
    [argname:argtype**]

    Any of the arguments can be specified either by name or populated
    by position.  A colon will cause arguments after it to only be
    specifiable by name.

    Once one default value is given all further arguments must have
    default values (except collector arguments, which have implicit
    default arguments of the empty list and the empty map)

    Examples:
    argspec  : arg1 arg2 arg3 : arg4 arg5 arg6*
    arguments: a b c d e f g arg4=h arg5=i
    dict     : {arg1:a, arg2:b, arg3:c, arg4:h, arg5:i, arg6:[d,e,f]

    If the colon had been missing from the argspec then multiple
    assignments (both d and e as the fourth and fifth arguments and
    arg4=h and arg5-i as named arguments) to arg4 and arg5 would have
    caused errors.

    With the colon the only way to specify the value for arg4 and arg5
    is by naming them explicitly.  Default values should probably be
    supplied in this case.
    """
    self.parsers = {}
    self.indexparsers = []
    self.extraindexparser = None
    self.extranamedparser = None

    self.argspec = self.split(argspec)

    parsedspec = self.argspec

    
    doneWithIndices = 0
    defaultSeen = 0
    for i in range(0,len(parsedspec)):
      namedCollector = 0
      indexCollector = 0
      argname, argdef = parsedspec[i]
      if argname.find(":") > -1:
        argname,typespec = argname.split(":",1)
      else:  # extra argname assignment here is just for consistency
        argname,typespec = argname, "string"

      if argname == ":":
        doneWithIndices = 1
        continue

      if len(argname) >= 1 and argname[-1:] == "*":
        if argdef != None:
          raise Exception, "cannot specify a default value for a collection argument (%s=%s)" % (argname, argdef)
        if len(argname) >= 2 and argname [-2:] == "**":
          argname = argname[:-2]
          if i < len(parsedspec) -1:
            raise Exception, "named collection argument must be the last argument (%s)" % (argname)
          parser = extraNamedParser(self,argname)
          namedCollector = 1
        else: #this is an index collection argument
          argname = argname[:-1]
          # Must check to see that we are the last argument or that 
          # the last argument is a named collector.
          if i < len(parsedspec) - 2:
            raise Exception, "index collection argument must be last or second-to last argument (%s)" % (argname)
          if i == len(parsedspec) -2:
            # must check that the last arg is a named collector:
            nextarg,nextdef = parsedspec[i+1]
            if len(nextarg) < 2 or nextarg[-2:] != "**":
              raise Exception, "index collector can only be second-to-last argument when last argument is a named collector"
          parser = extraIndexParser(self,argname)
          indexCollector = 1
      else:
        parser = Parser(self,argname)

      if self.typecheckers.has_key(typespec):
        typechecker = self.typecheckers[typespec]
      else:
        raise Exception, "Unknown type specified"

      parser.typechecker = typechecker

      if argdef != None:
        parser.default = argdef
        defaultSeen = 1

      if defaultSeen and parser.default == None:
        raise Exception, "Argument without default value (%s) seen after default values already specified" % (argname)
      
      if not namedCollector and not indexCollector:
        if not doneWithIndices:
          self.indexparsers.append(parser)
        if self.parsers.has_key(argname):
          raise Exception, "Multiple argument named %s specified." % (argname)
        self.parsers[argname] = parser
      elif namedCollector:
        self.extranamedparser = parser
      elif indexCollector:
        self.extraindexparser = parser
    
  def parse(self, input):
    """
    Takes an input string and produces the populated dictionary
    matching self's argspec.  Raises an error if extra arguments are
    encounterd (without appropriate oollection arguments specified),
    required arguments are missing or types aren't valid.
    """
    dict = {}

    arguments = self.split(input)


    foundNamedArg = 0
    for i in range(0,len(arguments)):
      key,val = arguments[i]

      if val == None:
        if foundNamedArg:
          raise Exception, "Non-named argument (%s) found after Named argument" % (key)
        if i < len(self.indexparsers):
          parser = self.indexparsers[i]
        elif self.extraindexparser:
          parser = self.extraindexparser
        else:
          raise Exception, "Unexpected argument received %s" % (key)
        parser.parseInto(i,key,dict)
      else:
        foundNamedArg = 1
        if self.parsers.has_key(key):
          parser = self.parsers[key]
        elif self.extranamedparser:
          parser = self.extranamedparser
        else:
          raise Exception, "Invalid named argument: %s=%s" % (key,val)
        parser.parseInto(key,val,dict)

    # now check that everything ahs been specified, puttingin defaults 
    # where available
    for key in self.parsers.keys():
      if not dict.has_key(key):
        parser = self.parsers[key]
        if parser.default == None:
          raise Exception, "Must specify a value for argument %s" % (key)
        else:
          defval = parser.parse(parser.default)
          dict[key] = defval
    
    return dict

  def split(self, input):
    """
    Take an input string and tokenizes it into a list of pairs.
    Tokens with equal signs come back as (key,value) pairs, those
    without come back as (argument,None)

    {}s are treated like quotes, and everything between the {}s is
    ignored.

    Any amount of white space between arguments is ignored.  (No empty
    arguments are returned.)

    \ escapes anything, including = and { and } (and, incidentally, \,
    and any character, so \a becomes a in the argument, and
    \n\o\t\a\d\r\a\g\o\n is the same as notadragon.
    
    """
    bracketdepth = 0
    arg = ""
    val = None
    arguments = []
    while input:
      nextchar = input[0:1]
      input = input[1:]

      if nextchar == " " or nextchar == "\t":
        if not bracketdepth:
          # We've completed a full argument
          if arg!="":
            arguments.append( (arg,val) )
          arg = ""
          val = None
        else:
          if val != None:
            val = val + nextchar
          else:
            arg = arg + nextchar
      elif nextchar == "\\":
        if input == "":
          raise Exception, "\\ at end of line."
        else:
          nextchar = input[0:1]
          input = input[1:]
          if val != None:
            val = val + nextchar
          else:
            arg = arg + nextchar
      elif nextchar == "}":
        bracketdepth = bracketdepth - 1
        if bracketdepth < 0:
          raise Exception, "mismatched }"
        if val != None:
          val = val + nextchar
        else:
          arg = arg + nextchar
      elif nextchar == "{":
        bracketdepth = bracketdepth + 1
        if val != None:
          val = val + nextchar
        else:
          arg = arg + nextchar
      elif val == None and nextchar == "=" and bracketdepth == 0:
        val = ""
      else:
        if val != None:
          val = val + nextchar
        else:
          arg = arg + nextchar

    if bracketdepth:
      raise Exception, "Mismatched {"

    if arg != "":
      arguments.append( (arg, val) )
      arg = ""
      val = ""
      
    return arguments

class Parser:
  """
  This is the base class for the parsers that argumentparser uses to
  actually populate the dictionary with each argument.
  """
  def __init__(self, argparser, argname):    
    self.argname = argname
    self.default = None
    self.typechecker = None
    self.argparser = argparser

  def parseInto(self, key, val, dict):
    if dict.has_key(self.argname):
      raise Exception, "Multiple values for argument %s Given" % (self.argname)
    else:
      dict[self.argname] = self.parse(val)

  def parse(self, val):
    if self.argparser.options["stripBraces"]:
      val = utils.strip_braces(val)
    if self.typechecker:
      return self.typechecker.check(val)
    else:
      return val
      
class extraIndexParser(Parser):
  """
  This class captures the parsing behaviour for an index collector.
  for each call to parseInto an entry is put into the list value in
  the argument dictionary.
  """
  def __init__(self,argparser,argname):
    Parser.__init__(self,argparser,argname)
    self.default = []
    
  def parseInto(self, index, val, dict):
    val = self.parse(val)
    if dict.has_key(self.argname):
      dict[self.argname].append(val)
    else:
      dict[self.argname] = [val]

class extraNamedParser(Parser):
  """
  This class captures the parsing behaviour for a named value collector.
  for each call to parseInto a new key=value pair is put into a map
  in the argument dictionary.
  """
  def __init__(self,argparser,argname):
    Parser.__init__(self,argparser,argname)
    self.default = {}
    
  def parseInto(self, key, val, dict):
    val=self.parse(val)
    if dict.has_key(self.argname):
      if dict.has_key(key) or dict[self.argname].has_key(key):
        raise Exception, "multiple values given for argument %s" % (key)
      dict[self.argname][key] = (val)
    else:
      dict[self.argname] = {key:val}


class Checker:
  """
  Trivial base class for argument checkers
  """
  def __init__(self):
    return

  def check(self, arg):
    return arg

class stringChecker(Checker):
  """
  Essentiallly the same as the trivial base class, but it's explicit
  that we just return the string we take in. 
  """
  def __init__(self):
    return

  def check(self,arg):
    return arg

class intChecker:
  """
  Accept only integer values and return integer objects.
  """
  def __init__(self):
    return

  def check(self,arg):
    return int(arg)

class booleanChecker:
  """
  Accept only boolean values
  True values are :  on, true, 1
  False Values are : off, false, 0
  Any other values cause exceptions.
  """
  def __init__(self):
    return

  def check(self,arg):
    if arg == "on" or arg == "true" or arg == "1":
      return 1
    elif arg == "off" or arg == "false" or arg == "0":
      return 0
    else:
      raise Exception, "Invalid boolean value specified: %s" % (arg)

class booleanOrNoneChecker:
  """
  Accept only boolean values or special "Not specified" values
  True values are :  on, true, 1
  False Values are : off, false, 0
  None Values are : -, None, ""
  Any other values cause exceptions.
  """
  def __init__(self):
    return

  def check(self,arg):
    if arg == "on" or arg == "true" or arg == "1":
      return 1
    elif arg == "off" or arg == "false" or arg == "0":
      return 0
    elif arg == "None" or arg == "-" or arg == "":
      return None
    else:
      raise Exception, "Invalid boolean value specified: %s" % (arg)


if __name__ == '__main__':
  testargs = {"arg1 arg2 arg3* arg4**":["test1 test3 test5 test7 help=wahoo woo=weewee"], "mapname*":["3k mapper by notadragon","lalala"]}

  for argspec in testargs.keys():
    argparser = ArgumentParser(argspec)
    print "Argspec: %s" % (argspec)
    for args in testargs[argspec]:
      print "Args   : %s" % (args)
      print "Dict   : %s" % (`argparser.parse(args)`)
