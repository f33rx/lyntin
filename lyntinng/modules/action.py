#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: action.py,v 1.8 2002/08/25 17:23:40 willhelm Exp $
#######################################################################
"""
This module defines the ActionManager which handles managing actions 
(triggers) and expansion of actions.
"""
import re, string, copy
import manager, utils, event, lyntin, hooks, exported, modutils

# the placement variable regular expression
VARREGEXP = re.compile('%_?(\d+)')

class ActionData:
  def __init__(self, ses):
    self._actions = {}
    self._ses = ses

  def addAction(self, trigger, response, onetime=0):
    """
    Compiles a trigger pattern and adds the entire action to the
    hash.

    arguments:

      'trigger' -- (string) the trigger pattern

      'response' -- (string) what to do when the trigger pattern
                    is found

      'onetime' -- (boolean) whethere this should be an auto-removing action

    returns:

      (int) always returns a 1

    """
    if lyntin.evalmode == lyntin.TINTIN:
      # first we expand variables in the action trigger then compile
      # it into a regular expression
      expansion = exported.expand_ses_vars(trigger, self._ses)
    else:
      expansion = trigger

    compiled = compile_action(expansion)
    self._actions[trigger] = (trigger, compiled, response, onetime)
    return 1

  def recompileRegexps(self):
    """
    When a variable changes, we go through and recompile all the
    regular expressions for the actions in this session.
    """
    for mem in self._actions.keys():
      (trigger, compiled, response, onetime) = self._actions[mem]
      expansion = exported.expand_ses_vars(trigger, self._ses)
      if not expansion:
        expansion = trigger
      compiled = compile_action(expansion)

      self._actions[trigger] = (trigger, compiled, response, onetime)

  def clear(self):
    """
    Clears all the stored actions from the action manager.
    """
    self._actions.clear()

  def removeActions(self, text):
    """
    Removes actions that match the given text from the list and
    returns the list of actions that were removed so the calling
    function knows what actually happened.

    arguments:

      'text' -- (string) all actions that match this text pattern
                will be removed.  the text pattern is "expanded" by
                'utils.expand_text'

    returns:

      list of tuples (trigger, response) of the action.  both
      trigger and response are strings--the same strings used when
      calling 'addAction'.

    """
    badactions = utils.expand_text(text, self._actions.keys())

    ret = []
    for mem in badactions:
      ret.append((self._actions[mem][0], self._actions[mem][2]))
      del self._actions[mem]

    return ret

  def getActions(self):
    """
    Returns a list of all the actions this actionmanager is currently
    managing.

    returns:

      list of triggers for the actions we're managing.  the trigger
      is a string.

    """
    list = self._actions.keys()
    list.sort()
    return list

  def checkActions(self, text):
    """
    Checks to see if text triggered any actions.  Any resulting 
    actions will get added as an InputEvent to the queue.

    arguments:

      'text' -- (string) the data coming from the mud to check
                for triggers on

    """
    # FIXME - make sure this works even when lines are broken up.

    matched = []

    # go through all the lines in the data and see if we have
    # any matches
    for (action, actioncompiled, response, onetime) in self._actions.values():
      line = utils.filter_cm(utils.filter_ansi(text))
      match = actioncompiled.search(line)
      if match:
        matched.append((line, action, actioncompiled, response))
        if onetime:
          del self._actions[action]

    # for every match we figure out what the expanded response
    # is and add it as an InputEvent in the queue.  the reason
    # we do a series of separate events rather than one big
    # event with ; separators is due to possible issues with 
    # braces and such in malformed responses.
    for (line, action, actioncompiled, response) in matched:
      match = actioncompiled.search(line)

      # get variables from the action
      actionvars = get_ordered_vars(action)
      varvals = {}
      # fill in values for all the variables in the match
      for i in xrange(len(actionvars)):
        varvals[actionvars[i]] = match.group(i+1)

      # add special variables
      varvals['a'] = line.replace(';', '_')
            
      # fill in response variables from those that
      # matched on the trigger
      response = utils.expand_vars(response, varvals)

      event.InputEvent(response, internal=1).enqueue()

  def getStatus(self):
    """ Returns a one-liner as to how many actions we have.

    returns:

      (string) a description of our status.
    """
    return "%d action(s)." % len(self._actions)

  def getInfo(self, text=""):
    """ Returns information about the actions in here.

    This is used by #action to tell all the actions involved
    as well as #write which takes this information and dumps
    it to the file.

    arguments:

         'text=""' -- (string) the text to expand on to find
                      actions that the user is interested in

    returns:

      a string of all the action information
    """
    if len(self._actions.keys()) == 0:
      return ''

    if text=='':
      list = self._actions.keys()
    else:
      list = utils.expand_text(text, self._actions.keys())

    data = []
    for mem in list:
      actup = self._actions[mem]

      data.append("%saction {%s} {%s} onetime={%s}" % 
              (lyntin.commandchar, mem, actup[2], actup[3]))

    return string.join(data, "\n")

  def getCount(self):
    """ Returns how many aliases we're managing.

    returns:

      (int) the number of aliases being managed.
    """
    return len(self._actions)


class ActionManager(manager.Manager):
  def __init__(self):
    self._actions = {}

  def addAction(self, ses, trigger, response, onetime=0):
    if not self._actions.has_key(ses):
      self._actions[ses] = ActionData(ses)
    return self._actions[ses].addAction(trigger, response, onetime)
    
  def clear(self, ses):
    if self._actions.has_key(ses):
      self._actions[ses].clear()

  def removeActions(self, ses, text):
    if self._actions.has_key(ses):
      return self._actions[ses].removeActions(text)
    return []

  def getActions(self, ses):
    if self._actions.has_key(ses):
      return self._actions[ses].getActions()
    return []

  def checkActions(self, ses, text):
    if self._actions.has_key(ses):
      self._actions[ses].checkActions(text)

  def getInfo(self, ses, text=""):
    if self._actions.has_key(ses):
      return self._actions[ses].getInfo(text)
    return ""

  def addSession(self, newsession, basesession=None):
    if basesession:
      if self._actions.has_key(basesession):
        acdata = self._actions[basesession]._actions
        for mem in acdata.keys():
          self.addAction(newsession, mem, acdata[mem][2], acdata[mem][3])

  def removeSession(self, ses):
    """ over-ridden from manager.Manager."""
    if self._actions.has_key(ses):
      del self._actions[ses]

  def getStatus(self, ses):
    """ over-ridden from manager.Manager."""
    if self._actions.has_key(ses):
      return self._actions[ses].getStatus()
    return "0 action(s)."

  def persist(self, args):
    """
    write_hook function for persisting the state of our session.
    """
    ses = args[0]
    file = args[1]
    quiet = args[2]

    data = self.getInfo(ses)
    if data:
      if quiet == 1:
        data = data.replace("\n", " quiet={true}\n")
        file.write(data + " quiet={true}\n")
      else:
        file.write(data + "\n")

  def variableChange(self, args):
    """
    When a variable changes, we need to recompile the regular
    expressions involved.  This facilitates that.

    This is registered with the variable_change hook.
    """
    ses = args[0]
    if self._actions.has_key(ses):
      self._actions[ses].recompileRegexps()

  def mudfilter(self, args):
    """
    mud_filter_hook function to check for actions when data
    comes from the mud.
    """
    ses = args[0]
    text = args[-1]

    if not ses._ignoreactions:
      self.checkActions(ses, text)
    return text


def compile_action(trigger):
  """
  Converts a trigger with pattern variables into a compiled
  regular expression and returns the regular expression.

  arguments:

    'trigger' -- (string) the trigger string to compile into
                 a regexp

  returns:

    (SRE_Pattern) returns a compiled regexp pattern ob
  """
  regexp = re.sub('%[0-9]+', '(.+?)', trigger)
  regexp = re.sub('%_[0-9]+', '(\S+?)', regexp)
  return re.compile(regexp)


def get_ordered_vars(text):
  """
  Takes in a string and removes any ordered variables
  from it.  Returns a list of the variables.

  arguments:

    'text' -- (string) the incoming string which may have
              ordered variables in it.

  returns:

    list of strings of the form '%[0-9]+' for ordered variable
    substitution.
  """
  keylist = []
  matches = VARREGEXP.findall(text)

  for match in matches:
    keylist.append(match)

  return keylist


def evalmodechange(args):
  """
  Registered with the evalmode_change hook, this handles adjusting
  behavior when the evalmode changes.
  """
  old = args[0]
  new = args[1]

  if (old == lyntin.LYNTIN or old == -1) and new == lyntin.TINTIN:
    # lyntin's just starting up into TINTIN mode or we just switched
    # into TINTIN
    hooks.variable_change_hook.register(am.variableChange)

  elif (old == lyntin.TINTIN or old == -1) and new == lyntin.LYNTIN:
    # lyntin's just starting up into LYNTIN mode or we just switched
    # into LYNTIN
    hooks.variable_change_hook.unregister(am.variableChange)

  elif old == lyntin.TINTIN and new == -1:
    # this module is being unloaded
    hooks.variable_change_hook.unregister(am.variableChange)


commands_dict = {}

def action_cmd(ses, args, input):
  """
  With no arguments, prints all actions.
  With one argument, prints all actions which match the arg.
  With multiple arguments, creates an action.

  When data from the mud matches the trigger clause, the response
  will be executed.  Trigger clauses can use anchors (^ and $)
  to anchor the text to the beginning and end of the line 
  respectively.

  Triggers can also contain Lyntin pattern-variables which start
  with a % sign and have digits: %0, %1, %10...  When Lyntin sees 
  a pattern-variable in an action trigger, it tries to match any 
  pattern against it, and saves any match it finds so you can 
  use it in the response.  See below for examples.

  Triggers get converted to regular expressions by converting
  placement variables %[0-9]+ to (.+?).  Feel free to use
  regular expression matching stuff.

  Note: It should be noted that actions are matched via regular 
  expressions.   %1 gets translated to (.+?) and %_1 gets translated
  to (\S+?).

  The response can be any mud command or Lyntin command and can
  contain placement-variables and the special variable %a which
  means "the whole matched line".

  The onetime argument can be set to true to have the action remove
  itself automatically if it is ever executed.

  examples:

     #action {^You are hungry} {get bread bag;eat bread}
     #action {EVISCERATES joey} {rescue joey}
     #action {%0 gives you %5} {say thanks for the %5, %0!}
     #action {^%_1 tells\s+you %2$} {say %1 just told me %2}

  category: commands
  """
  trigger = args["trigger"]
  action = args["action"]
  onetime = args["onetime"]
  quiet = args["quiet"]

  am = exported.get_manager("action")

  # they typed '#action'--print out all the current actions
  if not trigger and not action:
    data = am.getInfo(ses)
    if data == '':
      data = "action: no actions defined."

    exported.write_message("actions:\n" + data)
    return

  # they typed '#action dd*' and are looking for matching actions
  if not action:
    data = am.getInfo(ses, trigger)
    if data == '':
      data = "action: no actions defined."

    exported.write_message("actions:\n" + data)
    return

  am.addAction(ses, trigger, action, onetime)
  if not quiet:
    exported.write_message("action: {%s} {%s} added." % (trigger, action))

commands_dict["action"] = (action_cmd, "trigger= action= onetime:boolean=false quiet:boolean=false")

def unaction_cmd(ses, args, input):
  """
  Removes action(s) from the manager.

  examples:

    #unaction {missed you.}
    #unaction missed*

  category: commands
  """
  am = exported.get_manager("action")
  func = am.removeActions
  modutils.unsomething_helper(args, func, ses, "action", "actions")

commands_dict["unaction"] = (unaction_cmd, "str= quiet:boolean=false")



am = None

def load():
  """ Initializes the module by binding all the commands."""
  global am, var_module
  modutils.load_commands(commands_dict)
  am = ActionManager()
  exported.add_manager("action", am)

  hooks.mud_filter_hook.register(am.mudfilter, 75)
  hooks.write_hook.register(am.persist)

  hooks.evalmode_change_hook.register(evalmodechange)
  evalmodechange((-1, lyntin.evalmode))

def unload():
  """ Unloads the module by calling any unload/unbind functions."""
  global am, var_module
  modutils.unload_commands(commands_dict.keys())
  exported.remove_manager("alias")
  hooks.mud_filter_hook.unregister(am.mudfilter)
  hooks.write_hook.unregister(am.persist)

  hooks.evalmode_change_hook.unregister(evalmodechange)
  evalmodechange((lyntin.evalmode, -1))

# Local variables:
# mode:python
# py-indent-offset:2
# tab-width:2
# End:
