#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: utils.py,v 1.22 2002/05/15 00:16:55 willhelm Exp $
#######################################################################
"""
This has a series of utility functions that aren't related to
classes in the application, but are useful in a variety of
places.  They're not dependent on application things, so 
they're highly unit tested.
"""
import string, re

SEMI_REGEXP = re.compile('(?<!\\\\);')
VAR_REGEXP = re.compile('%(-?(\d+):?-?(\d*)|:-?(\d+))')
NESTED_VAR_REGEXP = re.compile('{.*%%([0-9]+).*}')
ANSI_CODE_REGEXP = re.compile('\[[0-9;]*[mJ]')

def chomp(text):
  """ Removes all '\\r' and '\\n' from the input string.

  arguments:

    'text' -- (string) the text to chomp

  returns:

    (string) chomped text

  """
  text = text.replace("\n", "")
  text = text.replace("\r", "")
  return text


def http_get(url):
  """ Retrieves the data at a given url and returns it as a big string.

  arguments:

    'url' -- (string) the url of the resource to retrieve

  returns:

    one big string of the resource

  raises:

    ValueError if the url is not valid or if the resource doesn't exist
  """
  import httplib
  if url.find("http://") == -1:
    raise ValueError, "This is not a valid url."

  filename = url[7:]

  if filename.find("/") == -1:
    filename += "/"
  host, resource = filename.split("/", 1)

  resource = "/" + resource
  sock = httplib.HTTP()
  sock.connect(host)
  sock.putrequest("GET", resource)
  sock.endheaders()
  status, reason, headers = sock.getreply()

  if status != 200:
    raise ValueError, "HTTP error: %d %s" % (status, reason)

  return sock.getfile()


def is_color_token(token):
  """ Returns whether or not this is a color token.

  arguments:

    'token' -- (string) the token to test

  returns:

    1 if it's a color token, 0 if not
  """
  if len(token) == 0:
    return 0

  return token[0] == chr(27)


def split_ansi_from_text(text):
  """ Takes in a string and returns a list of text and ansi tokens.

  arguments:

    'text' -- (string)

  returns:

    list of text and ansi tokens (all strings)
  """
  matchob = ANSI_COLOR_REGEXP.search(text)
  if matchob:
    textlist = []
    marker = 0
    while matchob:
      (b, e) = matchob.span()
      if marker != b:
        textlist.append(text[marker:b])
      else:
        textlist.append(text[b:e])

      marker = e
      matchob = ANSI_COLOR_REGEXP.search(text, marker)
    textlist.append(text[marker:])
    return textlist

  return [text]


def expand(str, list):
  """ Returns a subset of the list that matches the given string.

  Takes a list and a string and returns a list of items
  in the original list that match the given string.  
  Handles * and anchors too.

  arguments:

    'str' -- (string) the string to match

    'list' -- (list of strings) the list of strings to match on

  returns:

    (list of strings) the list of matches

  """
  ret = []
  wildcardcheck = str.find('*')

  # if they didn't have wildcards....
  if wildcardcheck == -1:
    for mem in list:
      if mem == str:
        ret.append(mem)

  # if they had wildcards....
  else:
    str = re.escape(str)

    # escaping the string will replace * with \* so we unreplace
    # it with .*
    str = str.replace("\\*", ".*")

    str = '^' + str + '$'
    regex = re.compile(str)

    for mem in list:
      if regex.match(mem):
        ret.append(mem)

  return ret

   
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


def strip_braces(text):
  """ Returns text after stripping the braces around the text.

  If the incoming text has a { at the beginning and a } at the
  end, it removes the braces.

  arguments:

    'text' -- (string) the string to remove the braces from

  returns:

    (string) text with the braces (if matched) removed
  """
  text = text.strip()
  if len(text) == 0:
    return text

  if text[0] == '{' and text[-1] == '}':
    return text[1:-1]
  return text


def parse_args(args):
  """
  Takes in a list of args and parses it out into a hashmap
  of arg-name to value(s).

  arguments:

    'args' -- The list of command-line arguments.

  returns:

    list of tuples of (arg, value) pairings
  """
  i = 0
  optlist = []
  while (i < len(args)):

    if args[i][0] == "-":
      if (i+1 < len(args)):
        if args[i+1][0] != "-":
          optlist.append((args[i], args[i+1]))
          i = i + 1
        else:
          optlist.append((args[i], ""))
      else:
        optlist.append((args[i], ""))

    else:
      optlist.append(("", args[i]))

    i = i + 1

  return optlist


def replace_nested_vars(text):
  """ Replaces all the nested variables with appropriate variables.

  arguments:

    'text' -- (string) the text to replace nested vars with

  returns:

    (string) the adjusted text
  """
  match = NESTED_VAR_REGEXP.search(text)
  while match:
    pat = '%%'+match.group(1)
    repl = '%'+match.group(1)
    text = re.sub(pat, repl, text)
    match = NESTED_VAR_REGEXP.search(text)

  return text

def strip_placement_vars(text):
  """ Returns a list of all the variables in a string.

  arguments:

    'text' -- (string) the text to strip placement vars from

  returns:

    list of replacement var strings
  """
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

  arguments:

    'input' -- (string) the user's input

    'expansion' -- (string) the expansion of the alias in the 
                   input

  returns:

    The expansion with all nested_vars replaced and placement
    vars replaced.
  """
  expansion = replace_nested_vars(expansion)
  vars = strip_placement_vars(expansion)

  if len(vars) > 0:
    varlookup = {}
    inputsplit = input.split(' ')

    # for all the variables, find what it translates to
    for mem in vars:
      if mem.find(':') < 0:
        start = int(mem)
        if start == -1:
          end = len(inputsplit)
        else:
          end = start + 1
      else:
        startmem,endmem = mem.split(':')
        if startmem:
          start = int(startmem)
        else:
          start = 0
        if endmem:
          end = int(endmem)
        else:
          end = max(len(inputsplit),start)

      varlookup[mem] = ' '.join(inputsplit[start:end])

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

  arguments:

    'textlist' -- (list of strings) the list to columnize

    'screenwidth=72' -- (int) the width to wrap against

    'indent=0' -- (int) the amount to indent each line

  returns:

    the final formatted string
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
  """ Used for testing purposes."""
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

  print "replace_vars tests"
  print replace_vars("#test 1 2 3", "#test")
  print replace_vars("#test 1 2 3", "#test %1 %2")
  print replace_vars("#test 1 2 3", "#test %0")
  print replace_vars("#test 1 2 3", "#test %-1")
  print replace_vars("#test 1 2 3", "#test %:-1")
  print replace_vars("#test 1 2 3", "#test %1:-1")
