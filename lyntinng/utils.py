#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: utils.py,v 1.35 2002/06/27 18:41:09 jmberne Exp $
#######################################################################
"""
This has a series of utility functions that aren't related to classes 
in the application, but are useful in a variety of places.  They're 
not dependent on application things, so they're highly unit tested.
"""
import string, re, time

SEMI_REGEXP = re.compile(r'(?<!\\);')

ANSI_COLOR_REGEXP = re.compile(chr(27) + '\[[0-9;]*[mJ]')

TIMESPAN_REGEXP = re.compile(r"^(?P<days>\d+d)?(?P<hours>\d+h)?(?P<minutes>\d+m)?(?P<seconds>\d+s?)?$")
TIME_REGEXP1=re.compile(r"^(?P<hour>[1-9]|1[0-2])(?P<ampm>a|p)$")
TIME_REGEXP2=re.compile(r"^(?P<hour>[1-9]|1[0-2]):(?P<minute>[0-5][0-9])(:(?P<second>[0-5]\d))?(?P<ampm>a|p)?$")
TIME_REGEXP3=re.compile(r"^(?P<hour>0|1[3-9]|2[0-3]):(?P<minute>[0-5][0-9])(:(?P<second>[0-5]\d))?$")



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
    b = text.rfind(chr(27))

    if b < marker:
      textlist.append(text[marker:])
    else:
      textlist.append(text[marker:b])
      textlist.append(text[b:])

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
  wrapcount = 0               # how much we've got on the line so far
  linecount = 0               # which line we're on

  if wraplength > 2:
    wraplength = wraplength - 2

  # split the formatting from the text
  if type(textlist) == type(''):
    textlist = split_ansi_from_text(textlist)

  for i in range(0, len(textlist)):

    # COLOR TOKEN
    if is_color_token(textlist[i]):
      pass

    # TEXT TOKEN
    else:
      marker = 0

      # while we keep finding carriage returns...
      x = textlist[i].find('\n')
      while x != -1:

        # if the carriage return is in a nice place we wrap there.
        if wrapcount + (x - marker) < wraplength:
          textlist[i] = insert_cr(textlist[i], x, indent)
          marker = x + 1
          wrapcount = 0

        # if the carriage return is not in a nice place.
        else:
          breakpoint = x
          # we look to the left for a space to wrap on.
          while wrapcount + (breakpoint - marker) > wraplength:
            breakpoint = textlist[i].rfind(' ', marker, breakpoint)
            if breakpoint <= marker:
              break

          # we either found a breakpoint or there are no spaces.
          # in the case of a breakpoint, we break.  otherwise
          # we just don't wrap that line....  i'm not a big fan
          # of wrapping inside a word thing.
          if breakpoint > marker:
            textlist[i] = insert_cr(textlist[i], breakpoint, indent)

          marker = breakpoint + 1
          wrapcount = 0

        x = textlist[i].find('\n', marker)

      # at this point there are no more carriage returns.  so we gots
      # to break at spaces.

      # if the remaining string exceeds the wraplength...       
      while len(textlist[i]) - marker + wrapcount >= wraplength:
        breakpoint = textlist[i].rfind(' ', 
                                       marker, 
                                       marker + wraplength - wrapcount)

        # we start looking from the end of the string leftwards
        # until we find a space

        # if there's a nice break point, we wrap there...
        if breakpoint > marker:
          textlist[i] = insert_cr(textlist[i], breakpoint, indent)
          wrapcount = 0
          marker = breakpoint
        else:
          break

      wrapcount += len(textlist[i]) - marker

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

  print timespec

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
    print e
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


def expand_vars(text, varmap):
  """ Looks at user input and expands any variables involved.

  It'll return the expansion if there is one.  Otherwise
  it returns None.

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
