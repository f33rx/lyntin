#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2001
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: utils.py,v 1.3 2002/01/20 07:21:02 willhelm Exp $
#######################################################################
"""
This has a series of utility functions that aren't related to
classes in the application, but are useful in a variety of
places.  They're not dependent on application things, so 
they're highly unit tested.
"""
import string, re

SEMI_REGEXP = re.compile('(?<!\\\\);')
VAR_REGEXP = re.compile('%(\d+)')

def chomp(data):
  """ Removes \r and \n from the input string."""
  data = data.replace("\n", "")
  data = data.replace("\r", "")
  return data


def expand(str, list):
  """ Returns a subset of the list that matches the given string.

  Takes a list and a string and returns a list of items
  in the original list that match the given string.  
  Handles * and anchors too.
  """
  ret = []
  wildcardcheck = string.find(str, '*')

  # if they didn't have wildcards....
  if wildcardcheck == -1:
    for mem in list:
      if mem == str:
        ret.append(mem)

  # if they had wildcards....
  else:
    # replace * with .*
    str = re.sub('\*', '.*', str)

    # replace ^ with \^
    str = re.sub('\^', '\\\^', str)

    # replace $ with \$
    str = re.sub('\$', '\\\$', str)

    str = '^' + str + '$'
    regex = re.compile(str)

    for mem in list:
      if regex.match(mem):
        ret.append(mem)

  return ret

   
def expand_speedwalk(input):
  """
  Expands speedwalk shorthand into the full-blown exciting
  thrill of mud-input that ever could.

  FIXME - this might be better written
  """
  output = ''
  c = ''
  for mem in input:
    if mem in '0123456789':
      c += mem
    elif len(c) > 0:
      output = output + ((mem + '\n') * int(c))
      c = '' 
    else:
      output = output + mem + '\n'
  return output


def filter_ansi(text):
  """ Filters out ansi codes."""
  return re.sub('\[[0-9;]*[mJ]', '', text)


def filter_cm(text):
  """ Filters out ^M.  Useful for logging."""
  return re.sub('\015|\r', '', text)


def split_commands(text):
  """ Takes text and splits it into separate commands.

  This method takens in text and parses it into separate commands
  on the ;.
  """
  marker = 0
  ret = []

  matchob = SEMI_REGEXP.search(text)
  while (matchob):
    (b, e) = matchob.span()
    # we count braces--this is a bit interesting since
    # if the entire segment we're looking at doesn't have
    # a full set of matched braces, we ignore this semi-colon
    # as a split point.
    count = (text[marker:b].count('{') - 
             text[marker:b].count('}'))

    if count == 0:
      ret.append(text[marker:b])
      marker = e

    matchob = SEMI_REGEXP.search(text, e)

  ret.append(text[marker:])
  return ret


def split_braced(text):
  """ Splits command line arguments into braced pieces.

  Takes the given text and splits it into two pieces taking into
  account possible bracing from the user.  If the text has
  errors--such as unmatched braces, we raise a ValueError.

  examples:
  #alias blah blah2  -> ["blah", "blah2"]
  #alias blah {blah2 blah3} -> ["blah", "blah2 blah3"]
  #alias {blah1 blah2} blah3  => ["blah1 blah2", "blah3"]
  #alias {blah1 blah2} {blah3 blah4} => ["blah1 blah2", "blah3 blah4"]
  """    
  text = text.strip()

  # the text has no braces, so we split it on the first space
  b = text.find('{')
  if b == -1:
    return text.split(' ', 1)

  count = 0
  breakpoint = -1

  # we zip through the array matching braces loosely
  for i in range(0, len(text)):
    c = text[i]
    if c == '{':
      count = count + 1

    if c == '}':
      count = count - 1

    # if we find a space that's not inside braces, this is a
    # a breakpoint
    if c == ' ' and count == 0 and breakpoint == -1:
      breakpoint = i
        
  # if we don't have a breakpoint or the count > 0 at the end
  if breakpoint == -1 or count > 0:
    raise ValueError, "Unmatched braces."

  return [strip_braces(text[:breakpoint]), strip_braces(text[breakpoint:])]


def strip_braces(text):
  """ Returns text after stripping the braces around the text."""
  text = text.strip()
  if text[0] == '{' and text[-1] == '}':
    return text[1:-1]
  return text


def strip_placement_vars(text):
  """ Returns a list of all the variables in a string."""
  ret = []
  match = VAR_REGEXP.search(text)
  while match:
    (b, e) = match.span() 
    if text[b+1:e] not in ret:
      ret.append(text[b+1:e])
    match = VAR_REGEXP.search(text, e)
  return ret


def replace_vars(input, expansion):
  """ Takes an input and an expansion and replaces expansion
  variables with the components from the input.

  Returns the finalized string.
  """
  vars = strip_placement_vars(expansion)

  if len(vars) > 0:
    varlookup = {}
    inputsplit = input.split(' ')

    # for all the variables, find what it translates to
    for mem in vars:
      intmem = int(mem)
      if intmem == 0:
        varlookup['0'] = input.split(' ', 1)[1]
      else:
        if len(inputsplit) > intmem:
          varlookup[mem] = inputsplit[intmem]
        else:
          varlookup[mem] = ''

    # run through the replacements
    for mem in varlookup.keys():
      expansion = re.sub("%" + mem, varlookup[mem], expansion)

  else:
    if input.find(' ') > -1:
      expansion = expansion + ' ' + input.split(' ', 1)[1]

  return expansion


def columnize(textlist, screenwidth=72, indent=0):
  """
  Takes a list of data and converts it into a series of columns
  and rows that are evenly spaced and pretty and stuff.
  """
  if screenwidth > 2 + indent:
    screenwidth = screenwidth - 2 - indent

  SPACING = 4
  maxwidth = 0

  for mem in textlist:
    maxwidth = max(maxwidth, len(mem))

  numcols = max(1, (screenwidth + SPACING) / (maxwidth + SPACING))
  numrows = (len(textlist) + numcols - 1) / numcols

  rows = []
  ## We can't just do "rows = ([],) * rows" -- need distinct lists
  for i in range(numrows): 
    rows.append([])

  idx = 0
  for mem in textlist:
    mem = (mem + (' ' * (maxwidth + (SPACING - 1) - len(mem))))

    rows[idx].append(mem)
    idx = (idx + 1) % numrows

  rows = map(string.rstrip, map(string.join, rows))
  return (indent * " ") + string.join(rows, "\n" + (indent * " "))


def _pass_fail(testoutput, realoutput):
  if testoutput == realoutput:
    print "   pass:", testoutput
  else:
    print "   fail:", testoutput

if __name__ == '__main__':
  print "split_commands tests"
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

  print 

  print "split_braced tests"
  _pass_fail(split_braced('blah blah2'),
            ['blah', 'blah2'])
  _pass_fail(split_braced('blah {blah2 blah3}'),
            ['blah', 'blah2 blah3'])
  _pass_fail(split_braced('{blah1 blah2} blah3'),
            ['blah1 blah2', 'blah3'])
  _pass_fail(split_braced('{blah1 blah2} {blah3 blah4}'),
            ['blah1 blah2', 'blah3 blah4'])
  try:
    split_braced('{blah1 blah2} {blah3 blah')
  except:
    print "   pass: exception"

  print 

  print "replace_vars tests"
  print replace_vars("#test 1 2 3", "#test")
  print replace_vars("#test 1 2 3", "#test %1 %2")
  print replace_vars("#test 1 2 3", "#test %0")
