#!/usr/bin/python
#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: argparser.py,v 1.24 2002/06/20 01:20:10 willhelm Exp $
#######################################################################
"""
This provides the ArgumentParser class which parses command arguments
automatically into a dictionary.
"""
import string, re, time
import utils

defaultOptions={ "stripBraces": 1,
                 "noparsing": 0,
                 "limitparsing": -1
               }
optionParser = None


class ParserException(Exception):
  pass

class ArgumentParser:
  """
  This is the actual argumentparser class

  Supported options:
  stripBraces (default=on) - whether all arguments should have braces
      stripped before being parsed.
  noparsing (default=off) - doesn't insure that all arguments are
      parsed.  works well when matched with  limitparsing=0 to provide
      a syntax line for commands that parse their own input
  limitparsing:int (default=-1) - only parse this number of tokens into dict,
      the rest of the input line goes into dict["input"]
  """
  
  def __init__(self, argspec, argoptions=None):

    # the syntax line is automatically generated from the argspec.
    # we print it out whenever we have a ParserException in the user input.
    self.syntaxline = ""

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
    global optionParser
    self.argoptions=argoptions
    self.options=defaultOptions.copy()
    if optionParser == None:
      optionParser = ArgumentParser("otherOptions* otherValuedOptions**")
    dict = optionParser.parse(argoptions)

    for key in dict.keys():
      if key=="otherOptions":
        for otherOption in dict[key]:
          self.options[otherOption] = 1
          if len(otherOption)>3 and otherOption[0:2]=="no":
            self.options[otherOption[2:]] = 0
      elif key=="otherValuedOptions":
        for otherKey in dict[key].keys():
          self.options[otherKey] = dict[key][otherKey]
      else:
        self.options[key] = dict[key]

    # set types for certain options
    self.options["limitparsing"] = int(self.options["limitparsing"])

  def buildParsers(self, argspec):
    """
    Build up the set of parsers to be used for argument parsing.

    The argspec follows the following format
    [argname[:argtype]]+ 
    [argname[:argtype]=defaultval]+ 
    [argname:argtype*] 
    [argname[:argtype]]+ 
    [argname[:argtype]=defaultval]+ 
    [argname:argtype**]

    Any of the arguments can be specified either by name or populated
    by position, except for arguments after the index collector
    argument.  Those must be specified by name only.

    Once one default value is given all further arguments must have
    default values (except collector arguments, which have implicit
    default arguments of the empty list and the empty map)

    Examples:  see the test code at the end of argparser.py
    """
    self.parsers = {}
    self.indexparsers = []
    self.extraindexparser = None
    self.extranamedparser = None

    self.argspec = self.split(argspec, buildsyntaxline=1)

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

      if len(argname) >= 1 and argname[-1:] == "*":
        if argdef != None:
          raise ParserException, "cannot specify a default value for a collection argument (%s=%s)" % (argname, argdef)

        if len(argname) >= 2 and argname [-2:] == "**":
          argname = argname[:-2]
          if i < len(parsedspec) -1:
            raise ParserException, "named collection argument must be the last argument (%s)" % (argname)
          parser = extraNamedParser(self,argname)
          namedCollector = 1

        else: #this is an index collection argument
          argname = argname[:-1]
          parser = extraIndexParser(self,argname)
          indexCollector = 1
          doneWithIndices = 1
          
      else:
        parser = Parser(self,argname)

      typechecker = createChecker(typespec)
      if not typechecker:
        raise ParserException, "Unknown type specifier: %s" % (typespec)

      parser.typechecker = typechecker

      if argdef != None:
        parser.setDefault(parser.parse(argdef))
        defaultSeen = 1

      if defaultSeen and not parser.defaultset:
        raise ParserException, "Argument without default value (%s) seen after default values already specified" % (argname)
      
      if not namedCollector and not indexCollector:
        if not doneWithIndices:
          self.indexparsers.append(parser)
        if self.parsers.has_key(argname):
          raise ParserException, "Multiple argument named %s specified." % (argname)
        self.parsers[argname] = parser
      elif namedCollector:
        self.extranamedparser = parser
        self.parsers[argname] = parser
      elif indexCollector:
        self.extraindexparser = parser
        self.parsers[argname] = parser
    
  def parse(self, input):
    """
    Takes an input string and produces the populated dictionary
    matching self's argspec.  Raises an error if extra arguments are
    encounterd (without appropriate oollection arguments specified),
    required arguments are missing or types aren't valid.
    """    
    dict = {}

    arguments = self.split(input,self.getOption("limitparsing"))

    foundNamedArg = 0
    for i in range(0,len(arguments)):
        key,val = arguments[i]

        if val == None:
          if foundNamedArg and not self.extraindexparser:
            raise ParserException, "Non-named argument (%s) found after Named argument" % (key)
          if i < len(self.indexparsers):
            parser = self.indexparsers[i]
          elif self.extraindexparser:
            parser = self.extraindexparser
          else:
            raise ParserException, "Unexpected argument received %s" % (key)
          parser.parseInto(i,key,dict)
        else:
          foundNamedArg = 1
          if self.parsers.has_key(key):
            parser = self.parsers[key]
          elif self.extranamedparser:
            parser = self.extranamedparser
          else:
            raise ParserException, "Invalid named argument: %s=%s" % (key,val)
          parser.parseInto(key,val,dict)


    # now check that everything has been specified, putting in defaults 
    # where available
    for key in self.parsers.keys():
      if not dict.has_key(key):
        parser = self.parsers[key]
        if not parser.defaultset and not self.getOption("noparsing"):
          raise ParserException, "Must specify a value for argument %s" % (key)
        else:
          dict[key] = parser.default
          
    return dict

  def split(self, input, maxsplit=-1, buildsyntaxline=0):
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

    after maxplit arguments are parsed (or never is maxsplit<0) stops
    and returns the rest of input as the final item    
    """
    bracketdepth = 0
    arg = ""
    val = None
    equalsign = 0
    arguments = []
    while input and (maxsplit < 0 or len(arguments) < maxsplit):
      nextchar = input[0:1]
      input = input[1:]

      if nextchar == " " or nextchar == "\t":
        if not bracketdepth:
          # We've completed a full argument
          if arg!="":
            arguments.append( (arg,val) )
            if buildsyntaxline:
              synarg = arg.upper()
              if synarg[-1] == "*":
                synarg = synarg[:-1] + "..."

              if val and len(val) > 0:
                synarg = synarg + "=" + val

              if equalsign == 1:
                self.syntaxline += "[<%s>] " % synarg
              else:
                self.syntaxline += "[%s] " % synarg

          arg = ""
          val = None
          equalsign = 0
        else:
          if val != None:
            val = val + nextchar
          else:
            arg = arg + nextchar
      elif nextchar == "\\":
        if input == "":
          raise ParserException, "\\ at end of line."
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
          raise ParserException, "mismatched }"
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
      elif val == None and bracketdepth == 0 and nextchar == "=":
        val = ""
        equalsign = 1
      else:
        if val != None:
          val = val + nextchar
        else:
          arg = arg + nextchar

    if bracketdepth:
      raise ParserException, "Mismatched {"

    if arg != "":
      arguments.append( (arg, val) )
      if buildsyntaxline:
        synarg = arg.upper()
        if synarg[-1] == "*":
          synarg = synarg[:-1] + "..."

        if val and len(val) > 0:
          synarg = synarg + "=" + val

        if equalsign == 1:
          self.syntaxline += "[<%s>] " % synarg
        else:
          self.syntaxline += "[%s] " % synarg

      arg = ""
      val = ""

    if input:
      arguments.append( ("input",input) )
    
    return arguments

class Parser:
  """
  This is the base class for the parsers that argumentparser uses to
  actually populate the dictionary with each argument.
  """
  def __init__(self, argparser, argname):    
    self.argname = argname
    self.default = None
    self.defaultset = 0
    self.typechecker = None
    self.argparser = argparser

  def parseInto(self, key, val, dict):
    if dict.has_key(self.argname):
      raise ParserException, "Multiple values for argument %s Given" % (self.argname)
    else:
      dict[self.argname] = self.parse(val)

  def parse(self, val):
    if self.argparser.getOption("stripBraces"):
      val = utils.strip_braces(val)
    if self.typechecker:
      return self.typechecker.check(val)
    else:
      return val

  def setDefault(self,val):
    self.default = val
    self.defaultset = 1
      
class extraIndexParser(Parser):
  """
  This class captures the parsing behaviour for an index collector.
  for each call to parseInto an entry is put into the list value in
  the argument dictionary.
  """
  def __init__(self,argparser,argname):
    Parser.__init__(self,argparser,argname)
    self.default = []
    self.defaultset = 1
    
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
    self.defaultset = 1
    
  def parseInto(self, key, val, dict):
    val=self.parse(val)
    if dict.has_key(self.argname):
      if dict.has_key(key) or dict[self.argname].has_key(key):
        raise ParserException, "multiple values given for argument %s" % (key)
      dict[self.argname][key] = (val)
    else:
      dict[self.argname] = {key:val}


typecheckers = {}

def createChecker(typespec):
  """
  This creates a typechecker based on the values in the dictionary
  typecheckers.

  First the typespec is split at its first colon.

  The first element (the typename) of the typespec is used as a key
  into typecheckers to find the function/class object to call to
  create the typechecker. 

  The rest of the typespec (the typeargs) is used with the function to
  construct the typechecker desired.
  """
  typespec = typespec.split(":",1)
  if len(typespec) == 1:
    typename, typeargs = typespec[0],None
  else:
    typename, typeargs = typespec

  if not typecheckers.has_key(typename):
    return None
  typechecker = typecheckers[typename](typename,typeargs)

  return typechecker

class Checker:
  """
  Trivial base class for argument checkers
  """
  def __init__(self, typename, typeargs):
    return

  def check(self, arg):
    return arg

class StringChecker(Checker):
  """
  Essentiallly the same as the trivial base class, but it's explicit
  that we just return the string we take in. 
  """
  def __init__(self, typename, typeargs):
    if typeargs:
      raise ParserException, "TypeArgs (%s) specified for non-configurable type (%s)" % (typeargs, typename)
    return

  def check(self,arg):
    return arg

typecheckers["string"] = StringChecker

class IntChecker(Checker):
  """
  Accept only integer values and return integer objects.
  """
  def __init__(self, typename, typeargs):
    if typeargs:
      raise ParserException, "TypeArgs (%s) specified for non-configurable type (%s)" % (typeargs, typename)
    return

  def check(self,arg):
    return int(arg)

typecheckers["int"] = IntChecker

class BooleanChecker(Checker):
  """
  Accept only boolean values
  True values are :  on, yes, true, 1
  False Values are : off, no, false, 0
  Any other values cause exceptions.
  """
  def __init__(self, typename, typeargs):
    if typeargs:
      raise ParserException, "TypeArgs (%s) specified for non-configurable type (%s)" % (typeargs, typename)
    return

  def check(self,arg):
    ret = utils.convert_boolean(arg)
    if ret == 1 or ret == 0:
      return ret

    raise ParserException, "Invalid boolean value specified: %s" % (arg)

typecheckers["boolean"] = BooleanChecker

class BooleanOrNoneChecker(Checker):
  """
  Accept only boolean values or special "Not specified" values
  True values are :  on, true, 1
  False Values are : off, false, 0
  None Values are : -, None, ""
  Any other values cause exceptions.
  """
  def __init__(self, typename, typeargs):
    if typeargs:
      raise ParserException, "TypeArgs (%s) specified for non-configurable type (%s)" % (typeargs, typename)
    return

  def check(self,arg):
    ret = utils.convert_boolean(arg)
    if ret == 1 or ret == 0:
      return ret
    elif arg == "None" or arg == "-" or arg == "":
      return None
    else:
      raise ParserException, "Invalid boolean value specified: %s" % (arg)

typecheckers["booleanornone"] = BooleanOrNoneChecker

class EvalChecker(Checker):
  """
  Evaluate its input argument as python code and return the resulting object.
  """
  def __init__(self, typename, typeargs):
    if typeargs:
      raise ParserException, "TypeArgs (%s) specified for non-configurable type (%s)" % (typeargs, typename)
    return

  def check(self,arg):
    try:
      return eval(arg)
    except Exception, e:
      raise ParserException, "Error eval-ing argument (%s): %s" % (arg, e)

typecheckers["eval"] = EvalChecker 

class TimeSpanChecker(Checker):
  """
  Accepts an amount of time and converts it to a number of seconds.
  """
  def __init__(self, typename, typeargs):
    if typeargs:
      raise ParserException, "TypeArgs (%s) specified for non-configurable type (%s)" % (typeargs, typename)
    return

  def check(self, arg):
    time = utils.parse_timespan(arg)
    if time != None:
      return time
    else:
      raise ParserException, "Invalid timespan specified %s" % (arg,)

typecheckers["timespan"] = TimeSpanChecker
  
class TimeChecker(Checker):
  """
  Accepts a date specification.

  Will also accept a time specification and apply it as a delta from
  _now_.  converts to the standard seconds-from_epoch. 
  """
  def __init__(self, typename, typeargs):
    if typeargs:
      raise ParserException, "TypeArgs (%s) specified for non-configurable type (%s)" % (typeargs, typename)
    return

  def check(self, arg):
    time = utils.parse_time(arg)
    if time != None:
      return time
    else:
      raise ParserException, "Invalid time specified %s" % (arg,)

typecheckers["time"] = TimeChecker
  
class ChoiceChecker(Checker):
  """
  Allows for a value to come from a selection of different strings.
  Automatically expands to one of them if it is uniquely specified.

  typeargs should be a |-delimitted list of possibly values
  """
  def __init__(self, typename, typeargs):
    if not typeargs:
      raise ParserException("TypeArgs (%s) not specified for %s type - must allow at least one choice." % (typeargs, typename) )
    self._choices = typeargs.split("|")
    return

  def check(self, args):
    possibilities = []
    for item in self._choices:
      if item.find(args) == 0:
        possibilities.append(item)
    if len(possibilities) == 0 or len(possibilities) > 1:
      raise ParserException, "Invalid argument, must be one of %s" % (self._choices,)
    else:
      return possibilities[0]

typecheckers["choice"] = ChoiceChecker

class ReChecker(Checker):
  """
  Compiles the incoming argument as a regular expression.
  """
  def __init__(self, typename, typeargs):
    if typeargs:
      raise ParserException, "TypeArgs (%s) specified for non-configurable type (%s)" % (typeargs, typename)

  def check(self, arg):
    return re.compile(arg)

typecheckers["re"] = ReChecker

if __name__ == '__main__':
  testargs = {
    ("arg1 arg2 arg3* arg4**",None):["test1 test3 test5 test7 help=wahoo woo=weewee"],
    ("mapname*",None):["3k mapper by notadragon","lalala"],
    ("mapname*","noparsing"):["3k mapper by notadragon"],
    ("option* quiet:boolean=true",None):["a b c quiet=false d","a b c quiet=true","x b c"]} 

  for argspec,argoptions in testargs.keys():
    argparser = ArgumentParser(argspec,argoptions)
    print "Argspec: %s" % (argspec)
    if argoptions: print "Argopts: %s" % (argoptions)
    for args in testargs[(argspec,argoptions)]:
      print "Args   : %s" % (args)
      print "Dict   : %s" % (`argparser.parse(args)`)
