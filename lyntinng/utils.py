#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: utils.py,v 1.43 2002/08/15 00:30:40 willhelm Exp $
#######################################################################
"""
This has a series of utility functions that aren't related to classes 
in the application, but are useful in a variety of places.  They're 
not dependent on application things, so they're highly unit tested.
"""
import string, re, time
import lyntin

SEMI_REGEXP = re.compile(r'(?<!\\);')

ANSI_COLOR_REGEXP = re.compile(chr(27) + '\[[0-9;]*[mJ]')

TIMESPAN_REGEXP = re.compile(r"^(?P<days>\d+d)?(?P<hours>\d+h)?(?P<minutes>\d+m)?(?P<seconds>\d+s?)?$")
TIME_REGEXP1=re.compile(r"^(?P<hour>[1-9]|1[0-2])(?P<ampm>a|p)$")
TIME_REGEXP2=re.compile(r"^(?P<hour>[1-9]|1[0-2]):(?P<minute>[0-5][0-9])(:(?P<second>[0-5]\d))?(?P<ampm>a|p)?$")
TIME_REGEXP3=re.compile(r"^(?P<hour>0|1[3-9]|2[0-3]):(?P<minute>[0-5][0-9])(:(?P<second>[0-5]\d))?$")

PVAR_REGEXP = re.compile(r'%+(-?(\d+):?-?(\d*)|:-?(\d+))')
DVAR_REGEXP = re.compile(r'\$+(-?(\d+):?-?(\d*)|:-?(\d+))')


def filter_ansi(text):
  """ Filters out ansi codes."""
  return re.sub(chr(27) + '\[[0-9;]*[mJ]', '', text)


def filter_cm(text):
  """ Filters out ^M.  Useful for logging."""
  return re.sub('\r', '', text)


def chomp(text):
  """ Removes all cr and nl from the input string.

  arguments:

    'text' -- (string) the text to chomp

  returns:

    (string) chomped text

  """
  return re.sub("\n|\r", '', text)


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

  return token[0:2] == chr(27) + "[" and token[-1] == "m"


def fix_color(color):
  """
  Helper function for debugging--it'll fix a color token
  so it's readable in ascii.

  arguments:

    'color' -- (string) the color token

  returns:

    string
  """
  return color.replace(chr(27), "ESC")


def split_ansi_from_text(text):
  """ Takes in a string and returns a list of text and ansi tokens.

  arguments:

    'text' -- (string)

  returns:

    list of text and ansi tokens (all strings)
  """
  global ANSI_COLOR_REGEXP

  matchob = ANSI_COLOR_REGEXP.search(text)
  if matchob:
    textlist = []
    marker = 0
    while matchob:
      (b, e) = matchob.span()

      if marker == b:
        textlist.append(text[b:e])
      else:
        textlist.append(text[marker:b])
        textlist.append(text[b:e])

      marker = e
      matchob = ANSI_COLOR_REGEXP.search(text, marker)

    # we do this to handle ansi color sequences which are broken
    # between two network chunks
    if marker < len(text):
      esc = text.find('\33', marker)
      if esc != -1:
        for i in range(marker, len(text)):
          c = text[i]
          if esc != -1:
            if c == '\33':
              esc = i
          else:
            if c.isdigit() or c == ";" or c == "[":
              continue
            else:
              esc = -1

      if esc == -1:
        textlist.append(text[marker:])
      else:
        textlist.append(text[marker:esc])
        textlist.append(text[esc:])

    return textlist

  return [text]


def expand_text(str, list):
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

  # if they didn't have wildcards....
  if not "*" in str:
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

   
def split_commands(text):
  """ Takes text and splits it into separate commands.

  This method takens in text and parses it into separate commands
  on the ;.
  """
  global SEMI_REGEXP
  marker = 0
  ret = []

  matchob = SEMI_REGEXP.search(text)
  while (matchob):
    (b, e) = matchob.span()
    # we count braces--this is a bit interesting since
    # if the entire segment we're looking at doesn't have
    # a full set of matched braces, we ignore this semi-colon
    # as a split point.
    left = 0
    right = 0
    for i in range(marker, b):
      if text[i] == '{' and (i == 0 or text[i-1] != "\\"):
        left += 1
      if text[i] == '}' and (i == 0 or text[i-1] != "\\"):
        right += 1 

    count = left - right

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


def insert_cr(text, index, indent=0):
  """
  Inserts a carriage return into the line and deals with indenting
  the next line (if need be).

  arguments:

    'text' -- (string) the text in question

    'index' -- (int) the place to stick the cr

    'indent=0' -- (int) how much to indent the next line

  returns:

    (string) the text with the cr at the index and the next line
    indented so many spaces

  """
  return (text[:index] + '\n' + (indent * ' ') + text[index+1:].lstrip())


def find_next_break(token, marker, wrapcount, wraplength):
  # first we check to see to see if we need to find a break
  if len(token) < marker - wrapcount + wraplength:
    return -1

  # first we look at carriage returns--they're fun and yummy!
  x = token.rfind("\n", marker, marker + wrapcount - wraplength)
  if x != -1 and x - wrapcount - marker < wraplength:
    return x

  # ok--no carriage returns.  so we try going out wraplength and working
  # to the left for spaces.
  x = token.rfind(" ", marker, marker - wrapcount + wraplength)
  if x != -1:
    return x

  return marker - wrapcount + wraplength


def wrap_text(textlist, wraplength=50, indent=0, firstline=0):
  """
  It takes a block of text and wraps it nicely.

  arguments:

    'textlist' -- (string) or (list of strings) either a string of 
                  text needing to be formatted and 
                  wrapped or a textlist--preferably the former.

    'wraplength' -- (int) how many characters to wrap at

    'indent=0' -- (int) how many spaces to indent each line

    'firstline=0' -- (int) 0 if we don't indent the first line, 1 if we do


  returns:

    (string) the wrapped text 
  """
  wrapcount = 0           # how much we've got on the line so far
  linecount = 0           # which line we're on

  if wraplength > 2:
    wraplength = wraplength - 2

  # split the formatting from the text
  if type(textlist) == type(''):
    textlist = split_ansi_from_text(textlist)

  for i in range(0, len(textlist)):
    # COLOR TOKEN
    if is_color_token(textlist[i]):
      continue

    # TEXT TOKEN
    marker = 0

    if firstline:
      x = find_next_break(textlist[i], marker, wrapcount, wraplength - indent)
    else:
      x = find_next_break(textlist[i], marker, wrapcount, wraplength)

    while x != -1:
      textlist[i] = insert_cr(textlist[i], x, indent)
      marker = x + indent + 1
      wrapcount = 0

      x = find_next_break(textlist[i], marker, wrapcount, wraplength - indent)

    wrapcount = len(textlist[i]) - marker + wrapcount


  # this next line joins the list with no separator (GASP!)
  if firstline:
    return (indent * " ") + ''.join(textlist)
  else:
    return ''.join(textlist)


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


def parse_timespan(timespan):
  """
  Parses a timsspan into a number of seconds.  

  arguments:

    'timespan' -- (string) the timespan to parse

  returns:

    None if the timespan was unparseable, the number of seconds otherwise. 
  """
  match=TIMESPAN_REGEXP.match(timespan)

  if not match:
    return None
    
  timespec=match.groupdict()

  if not timespec["days"] and not timespec["hours"] and not timespec["minutes"] and not timespec["seconds"]:
    return None

  days = timespec["days"]
  if not days:
    days="0"
  elif days[-1]=="d":
    days=days[:-1]
  days=int(days)

  hours = timespec["hours"]
  if not hours:
    hours="0"
  elif hours[-1]=="h":
    hours=hours[:-1]
  hours=int(hours)

  minutes = timespec["minutes"]
  if not minutes:
    minutes="0"
  elif minutes[-1]=="m":
    minutes=minutes[:-1]
  minutes=int(minutes)
    
  seconds = timespec["seconds"]
  if not seconds:
    seconds="0"
  elif seconds[-1]=="s":
    seconds=seconds[:-1]
  seconds=int(seconds)
      
  return days * 24 * 60 * 60 + hours * 60 * 60 + minutes * 60 + seconds


def parse_time(timearg):
  """
  Parses a time into the number of seconds since the epoch.
 
  First attempts to parse as a time of day, and if that fails attempts
  to parse as a timespan.  Timespans are interpretted as times from
  time.time() (now). 

  arguments:

    'timearg' -- (string) the timespan to parse

  returns:

    None if the time was unparseable, the number of seconds otherwise. 
  """
  match = TIME_REGEXP1.match(timearg) or TIME_REGEXP2.match(timearg) or TIME_REGEXP3.match(timearg)

  if not match:
    timespan = parse_timespan(timearg)
    if timespan != None:
      return time.time() + timespan
    else:
      return None

  timespec = match.groupdict()
  currenttime = time.localtime()

  # print timespec

  hour=int(timespec.get("hour",None))
  ampm=timespec.get("ampm",None)
  if hour > 12:
    if ampm:
      return None
    else:
      ampm="p"
  else:
    if ampm == "p":
      hour = hour + 12

  if hour < 1 or hour > 24:
    return None

  minute = timespec.get("minute",None)
  if minute == None:
    minute = 0
  else:
    minute = int(minute)
  
  second = timespec.get("second",None)
  if second == None:
    second = 0
  else:
    second = int(second)

  timetuple = (currenttime[0],currenttime[1],currenttime[2],hour,minute,second,currenttime[6],currenttime[7],currenttime[8])
  if ampm:
    increment=24
  else:
    increment=12
    
  while timetuple < currenttime:
    timetuple = timetuple[:3] + (timetuple[3] + increment,) + timetuple[4:]
  
  try:
    return time.mktime(timetuple)
  except Exception, e:
    # print e
    return None


def figure_color(textlist, currentcolor, leftover=""):
  """ 
  Takes a textlist of text and color tokens and figures out
  the latest current color.

  arguments:

    'textlist' -- the list of strings and ansi color codes

    'currentcolor' -- a tuple of three items that represent
                      the current color.  
                      (attribute, foreground, background)

    'leftover=""' -- if we encounter a half done color code
                     we throw it in the leftover.  the leftover
                     gets prepended to the first textlist element
                     on the next run of figureColor

  returns:

    the new currentcolor and leftover as a tuple
  """
  if leftover:
    ind = textlist[0].find("m")
    if ind > -1:
      leftover += textlist[0][:ind]
      textlist[0] = textlist[0][ind+1:]
    textlist.insert(0, leftover)
    leftover = ''

  for mem in textlist:
    if is_color_token(mem):
      color = mem[2:-1]

      # handles the case where it's ESC[m
      if color == "":
        currentcolor = [-1, -1, -1]

      # handles other cases!
      else:
        color = color.split(";")
        for i in color:
          if not i.isdigit():
            continue

          i = int(i)

          if i == 0:
            # 0 is a reset
            currentcolor = [-1, -1, -1]
      
          elif 0 < i and i < 10:
            # these are ansi color attributes
            currentcolor[0] = i

          elif 30 <= i and i < 40:
            # these are foreground attributes
            currentcolor[1] = i

          elif 40 <= i and i < 50:
            # these are background attributes
            currentcolor[2] = i

  # we're looking for leftover pieces here
  if len(textlist) > 0:
    mem = textlist[-1]
    if len(mem) > 0 and mem[0] == chr(27) and mem[-1] != "m":
      leftover = mem
      
  return currentcolor, leftover


TRUE_VALUES = ["yes", "true", "1", "on"]
FALSE_VALUES = ["no", "false", "0", "off"]

def convert_boolean(text):
  """
  Returns 1 if true, 0 if false, or -1 if it's not a boolean.

  arguments:

    'text' -- (string) the incoming test

  returns:

    1 if true, 0 if false, -1 if not a boolean
  """
  if text in TRUE_VALUES:
    return 1
  elif text in FALSE_VALUES:
    return 0
  else:
    return -1


# --------------------------------------
# variable expansion functions
# --------------------------------------

def expand_vars(text, varmap):
  """
  Figures out which evalmode we're in and calls the appropriate
  variable expansion function.

  Note: If you have a text string and you want the variable manager 
  to expand variables in that string according to session variables,
  use 'exported.expand_ses_vars' instead.

  arguments:

    'text' -- (string) the text to expand variables on

    'varmap' -- (dict) the varname to expansion mapping

  returns:

    the text with all variables expanded
  """
  if lyntin.evalmode == lyntin.TINTIN:
    return tintin_expand_vars(text, varmap)
  else:
    return lyntin_expand_vars(text, varmap)


def lyntin_expand_vars(text, varmap):
  """ 
  Do not call this directly.  Use 'expand_vars' instead.

  Looks at user input and expands any variables involved using
  the Lyntin variable expansion methodology.

  Lyntin variable expansion works by replacing all instances
  of $blah with the appropriate variable.  Then at a later
  point, variables preceded by multiple $ are denested one
  scope and lose a $.

  It returns the (un)adjusted text.

  arguments:

    'text' -- (string) the text to expand variables on

    'varmap' -- (dict) the varname to expansion mapping

  returns:

    the text with all variables expanded
  """
  if not ("%" in text or "$" in text) or len(text) == 0:
    return text

  varmapkeys = varmap.keys()
  i = 0

  # we go through the text expanding things one at a time.
  while (i < len(text)):
    mem = text[i]
    if i != 0:
      memm1 = text[i-1]
    else:
      memm1 = None

    if (mem == "%" or mem == "$") and memm1 != "\\":
      j = i
      ccount = 0

      # count the $/% thingies first
      while j < len(text) and text[j] == mem:
        ccount += 1
        j += 1
 
      if ccount == 1:
        textfragment = text[j:]
        for mem in varmapkeys:
          if textfragment.find(mem) == 0:
            repl = str(varmap[mem])
            text = text[:i] + repl + text[i+len(mem)+ccount:]
            break
      else:
        i += ccount

    i += 1
  return text

def lyntin_denest_vars(text):
  """ Replaces all the nested variables with appropriate variables.

  arguments:

    'text' -- (string) the text to replace nested vars with

  returns:

    (string) the adjusted text
  """
  text = lyntin_denest_vars_worker("$", text)
  return text

def lyntin_denest_vars_worker(varchar, text):
  """ Handles the actual denesting for lyntin_denest_vars."""
  varchar2 = "%s%s" % (varchar, varchar)
  index = text.find(varchar2)

  while (index != -1):
    if (index == 0 or text[index] != "\\") and \
        (index == len(text)-1 or text[index+2] != varchar):
      text = text[:index] + text[index+1:]
    
    index = text.find(varchar2, index+1) 

  return text

def sort_by_length(item1, item2):
  """ Takes two strings and compares them by length."""
  return cmp(len(item1), len(item2))

def tintin_expand_vars(text, varmap):
  """
  Do not call this directly.  Use 'expand_vars' instead.

  Looks at user input and expands any variables involved
  according to Tintin variable expansion heuristics.

  arguments:

    'text' -- (string) the text to expand variables on

    'varmap' -- (dict) the varname to expansion mapping

  returns:

    the text with all variables expanded
  """
  if not (text.find("%") != -1 or text.find("$") != -1) or len(text) == 0:
    return text

  varmapkeys = varmap.keys()
  varmapkeys.sort(sort_by_length)
  i = 0
  count = 1

  # we go through the text expanding things one at a time.
  while (i < len(text)):
    mem = text[i]
    if i != 0:
      memm1 = text[i-1]
    else:
      memm1 = None

    if mem == "{" and memm1 != "\\":
      count += 1

    elif mem == "}" and memm1 != "\\":
      count -= 1

    elif (mem == "%" or mem == "$") and memm1 != "\\":
      j = i
      ccount = 0

      # count the $/% thingies first
      while j < len(text) and text[j] == mem:
        ccount += 1
        j += 1
 
      if ccount == count:
        textfragment = text[j:]
        for mem in varmapkeys:
          if textfragment.find(mem) == 0:
            repl = str(varmap[mem])
            text = text[:i] + repl + text[i+len(mem)+ccount:]
            break
      else:
        i += ccount

    i += 1
  return text

# --------------------------------------
# placmeent variable expansion functions
# --------------------------------------

def expand_placement_vars(input, expansion):
  """
  Takes an user input line and an alias expansion and hands it
  off to the appropriate function for evaluating the placement
  variable replacement.

  Returns the finalized string.

  arguments:

    'input' -- (string) the user's input

    'expansion' -- (string) the expansion of the alias in the 
                   input

  returns:

    The expansion with all nested_vars replaced and placement
    vars replaced.
  """
  if lyntin.evalmode == lyntin.TINTIN:
    return tintin_expand_placement_vars(input, expansion)
  else:
    return lyntin_expand_placement_vars(input, expansion)

def get_variable_value(inputsplit, var):
  """
  Takes a list and a var and figures out what the placement var
  is based on the inputsplit list.

  arguments:

    'inputsplit' -- (list of strings) the input string list

    'var' -- (string) the variable

  returns:

    (string) the variable expansion
  """
  # handles the 0 case
  if var == "0":
    start = 1
    end = len(inputsplit)

  # handles non splits
  elif var.find(':') == -1:
    start = int(var)
    if start == -1:
      end = len(inputsplit)
    else:
      end = start + 1

  # handles splits
  else:
    startmem,endmem = var.split(':')
    if startmem:
      start = int(startmem)
    else:
      start = 0
    if endmem:
      end = int(endmem)
    else:
      end = max(len(inputsplit),start)

  return ' '.join(inputsplit[start:end])


def tintin_expand_placement_vars(input, expansion):
  """
  Takes an input and an expansion and expands placement variables 
  with the components from the input using Tintin placement
  variable evaluation.

  Returns the finalized string.

  arguments:

    'input' -- (string) the user's input

    'expansion' -- (string) the expansion of the alias in the 
                   input

  returns:

    The expansion with all nested_vars replaced and placement
    vars replaced.
  """
  inputsplit = input.split(' ')

  # check to see if there are any % or $ in the expansion
  if not ("%" in expansion or "$" in expansion):
    i = input.find(' ')
    if i != -1:
      expansion = expansion + ' ' + input[i+1:]
    return expansion

  i = 0
  count = 1

  # we go through the expansion expanding things one at a
  # time.
  while (i < len(expansion)):
    mem = expansion[i]
    if i != 0:
      memm1 = expansion[i-1]
    else:
      memm1 = None

    if mem == "{" and memm1 != "\\":
      count += 1

    elif mem == "}" and memm1 != "\\":
      count -= 1

    elif (mem == "%" or mem == "$") and memm1 != "\\":
      if mem == "%":
        matchob = PVAR_REGEXP.match(expansion, i)
      elif mem == "$":
        matchob = DVAR_REGEXP.match(expansion, i)

      if matchob:
        (b, e) = matchob.span()
        var = expansion[b:e]

        # we check to see if this is in our expansion nesting
        if var.count(mem) == count:
          var = var.replace(mem, "")
          var = get_variable_value(inputsplit, var)
          expansion = expansion[:b] + var + expansion[e:]

        else:
          i += len(var) - 1

      # FIXME - if it's not a matchob, should we gobble things up?

    i += 1

  return expansion


VAR_REGEXP = re.compile('(?<!%)%(-?(?:\d+):?-?(?:\d*)|:-?(?:\d+))')
NESTED_VAR_REGEXP = re.compile('{.*%%([0-9]+).*}')

def replace_nested_vars(text):
  """ Replaces all the nested variables with appropriate variables.

  arguments:

    'text' -- (string) the text to replace nested vars with

  returns:

    (string) the adjusted text
  """
  global NESTED_VAR_REGEXP
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
  global VAR_REGEXP

  ret = []
  match = VAR_REGEXP.search(text)
  while match:
    (b,e) = match.span()
    val = match.groups()[0]
    if val not in ret:
      ret.append(val)
    match = VAR_REGEXP.search(text, e)
  return ret


def lyntin_expand_placement_vars(input, expansion):
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
  # expansion = replace_nested_vars(expansion)
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
      expansion = re.sub("(?<!%)%" + mem, varlookup[mem], expansion)

  else:
    if input.find(' ') > -1:
      expansion = expansion + ' ' + input.split(' ', 1)[1]

  expansion = lyntin_denest_vars_worker("%", expansion)

  return expansion

# Local variables:
# mode:python
# py-indent-offset:2
# tab-width:2
# End:
