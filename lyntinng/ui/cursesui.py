#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 2001, 2002
#
# Lyntin is distributed under the GNU General Public License.  See
# the file LICENSE in the distribution for details.
# $Id: cursesui.py,v 1.12 2002/05/29 23:58:03 willhelm Exp $
#######################################################################
"""
This module holds the Curses ui.  It could use some _serious_ work.
"""
import curses, string, re
import ui, hooks, event, engine, utils

myui = None
def get_ui_instance():
  global myui
  if myui == None:
    myui = Cursesui()
  return myui

class MessageTypeUnknown(Exception): pass
class IllegalTupleinstrtoDisplay(Exception): pass
class Cursesui(ui.BaseUI):
  """
  Anyhow, this is a very un-fully-featured curses ui at the moment.
  Needs:
    - scrollback

    - input catch (pgup pgdwn bring back commands)

    - speed it up

  """
   
  def __init__(self):
    """ Initializes."""
    ui.BaseUI.__init__(self)
    self._main = None
    self._input = None
    self._output = None

    self._newline = []
    self._shutdown = 0
    self._echoon = 1
    #color-attribute -> see getColor
    self._colorAttrDict = {'0':'X','1':'B','2':'N','3':'A','4':'U','5':'b','6':'b','7':'R','8':'I'}
    #color default for first message, also where getColor remembers last color
    self._color = 'N 3740'
    #color escape code
    self._colorEscape = chr(27)
    #attribute dictionary
    self._attrDict = {'b':curses.A_BLINK,
                      'B':curses.A_BOLD,
                      'N':curses.A_NORMAL,
                      'U':curses.A_UNDERLINE,
                      'R':curses.A_NORMAL,
                      'X':curses.A_NORMAL,
                      'I':curses.A_NORMAL,
                      'A':curses.A_NORMAL}
    #colors
    self._colorList = [curses.COLOR_BLACK,
                       curses.COLOR_RED,
                       curses.COLOR_GREEN,
                       curses.COLOR_YELLOW,
                       curses.COLOR_BLUE,
                       curses.COLOR_MAGENTA,
                       curses.COLOR_CYAN,
                       curses.COLOR_WHITE]
    #supported prompts
    self._Prompts = { '' : '\nlyntin: ', ui.ERROR :'\nerror: ',
                      ui.LTDATA : '\nlyntin: ', ui.TESTDATA : '\nTEST: ',
                      ui.USERDATA : '', ui.MUDDATA : ''}

    #partial color code support
    self._isPartialLine = 0
    self._partialLine = ''
    
    #optimized re searches
    self._aNumber_re = re.compile('[0-9]')
    self._notNumber_re = re.compile('[^0-9]')

    #start up display
    self._stdscr = curses.initscr()
    self._stdscr.refresh()
    curses.start_color()
    
    if curses.has_colors():
      self._colors = 1
      # create color pairs -> colorpair 0 is hard set white black, so 
      # avoid setting again.
      colorPair = 0
      for backgroundColor in self._colorList[1:]:
        for foregroundColor in self._colorList:
          colorPair += 1
          curses.init_pair(colorPair,foregroundColor,backgroundColor)

      for foregroundColor in self._colorList[:7]:
        colorPair += 1
        curses.init_pair(colorPair, foregroundColor, curses.COLOR_BLACK)
    else:
      #no color so only black and white
      for pairs in range(0,64):
        curses.init_pair(pairs, curses.COLOR_WHITE, curses.COLOR_BLACK)
      

    #colorpair color dictionary
    self._ansiClrtoClrPairDict = {}
    colorPair = 0
    
    for backGround in range(41,48):
      for foreGround in range(30,38):
        colorPair += 1
        self._ansiClrtoClrPairDict[str(foreGround) + str(backGround)] = colorPair

    for foreGround in range(30,37):
      colorPair += 1
      self._ansiClrtoClrPairDict[str(foreGround) + '40'] = colorPair
      
    self._ansiClrtoClrPairDict['3740'] = 0

    #end of color varibles

    curses.noecho()
    curses.cbreak()

    self._stdscr.nodelay(0)
    self._stdscr.keypad(0)

    (self._height, self._width) = self._stdscr.getmaxyx()
    self._main = curses.newwin(self._height, self._width, 0, 0)

    self._output = self._main.subwin(self._height - 3, self._width, 0, 0)
    # FIXME - might want to try a textbox here
    self._input = self._main.subwin(self._height - 2, 0)
    self._input.hline(0, 0, curses.ACS_HLINE, self._width)
    self._input.move(1,0)
    self._output.move((self._height - 4), 0)
    # self._output.nodelay(1)
    # self._input.nodelay(0) 
    self.refresh_all()
    hooks.startup_hook.register(self.startui)
    hooks.shutdown_hook.register(self.shutdown)


  def startui(self, args):
    """ Starts the ui."""
    #import engine
    hooks.to_user_hook.register(self.write)
    engine.myengine.startthread("ui", self.run)


  def shutdown(self, args):
    """
    Gets called (it's registered with the shutdown hook).
    This is important because it ends the curses session
    returning the client back to "normal" land.
    """
    self._shutdown = 1 
    curses.nocbreak()
    self._stdscr.keypad(0)
    curses.echo()
    curses.endwin()


  def getPrompt(self, message_type):
    """
    returns the prompt as a string
    """
    userPrompt = ""
    if self._Prompts.has_key(message_type):
      return self._Prompts[message_type]
    else:
      return ""


  def getColor(self, ansi_code):
    """
    getColor string -> ansi code which is everything inbetween [ and m
    returns a string code like Xb 3740 where X is the attribute and 3740 
    is the color.
    NOTE: this needs to have a color state to remember colors and attributes.
    """
    #FIXME:
    # Possible design change
    #   Make each attribute a on/off switch.  Then as reading in attr's just
    #   turn on.  Might simplify all the term checking at the end of getColor
    #   and handle properly attributes being left on
    
    #check for a ; -> single terms
    if ansi_code == '':
      return self._color

    #one term
    if ansi_code.count(';') < 1:
      colorCodes = [ansi_code]

    #multiple terms  
    else:
      colorCodes = ansi_code.split(';')

    colorCodes.sort()
    returnCode = ''

    for oneCode in colorCodes:
      if oneCode == '':
        continue

      #any non-number -> loop out
      aNum = self._notNumber_re.search(oneCode)
      if aNum != None:
        continue

      numOneCode = int(oneCode)

      #is it an attribute  
      if (numOneCode < 8) and (numOneCode > -1):
        #letters in front, numbers in back
        returnCode = self._colorAttrDict[oneCode] + returnCode

      #is it a forground or background color
      elif (numOneCode > 29) and (numOneCode < 48):
        if (numOneCode == 38) or (numOneCode == 39):
          continue
        returnCode += oneCode

    #picks up the speed and correctly displays 3k type ansi
    if returnCode == 'X':
      return 'N 3740'
 
    #------------> area below is to check to that a complete color code is returned ie X 3740
    #  forgBackColor[0] = attributes string
    #  forgBackColor[1] = forgroundBackground colors ie 3740
    #---------------------------------------------------------------------------------
      
    findNumber = self._aNumber_re.search(returnCode)
    returnCode_len = len(returnCode)
  
    forgBackColor = self._color.split(' ')
    
    if findNumber == None:
      
      if len(returnCode) == 0:
        returnCode = forgBackColor[0] # <----- which is the attributes string

      #splits the terms with a space and returns 
      returnCode = returnCode + ' ' + forgBackColor[1]

    #this has some numbers where findNumber has the begining
    else:
      #split the colors and attributes with a space
      returnCode = returnCode[:findNumber.start()] + ' ' + returnCode[findNumber.start():]
      numbLen = returnCode_len - findNumber.start()

      if findNumber.start() == 0:
        returnCode = forgBackColor[0] + returnCode
      
      #if = 2 then add either foreground or background
      if numbLen == 2:
        
        if int(returnCode[-2:]) > 37:
          #its a background color. Add foreground
          returnCode = returnCode[:-2] + forgBackColor[1][0:2] + returnCode[-2:]

        else:
          returnCode += forgBackColor[1][-2:]
          #its a forground color. Add background
          
      #elif = 4 then check that first two #'s are forg and last 2 are back
      #else okay not 2 or 4 wipe it bad code
      
    return returnCode
    #return letter for 1-8 and corrisponding numbers that are legal
    
  def strtoDisplay(self, col_mess_tuple):
    """
    strtoDisplay tuple -> (message, color, prompt)
    This is the dirty work of putting the single color message onto the screen
    """
    
    singleLines = []
    
    try: 
      (message, color, prompt)= col_mess_tuple
    except Exception:
      raise IllegalTupleinstrtoDisplay
    
    #break color into attr and forgback
    splitColor = color.split(' ')

    if splitColor[0] == '':
      splitColor[0] = 'N'
    
    #combine all attr into one binary operation
    combinedAttr = self._attrDict[splitColor[0][0]]
    for aLetter in range(1,(len(splitColor[0]) - 1)):
      combinedAttr = combinedAttr|self._attrDict[splitColor[0][aLetter]]
     
    if prompt:
      message = prompt + message.replace("\n" , prompt)
    
    #if more than one line split it
    if message.count("\n") > 0:
      singleLines = message.split("\n")
      
    else:
      singleLines =[message]
      
    counter = 0
    while len(singleLines):
      #basically a newline but first line does not have new line
      if counter > 0:
        self._output.move(0,0)
        self._output.deleteln()
        self._output.move((self._height - 4),0)

      #if blank short cut out before heavy work 
      if singleLines[0] == '':
        singleLines.pop(0)
        counter = 1
        continue

      #how big is my display and will the upcoming string fit in it  
      (y,x) = self._output.getyx()
      (maxy, maxx) = self._output.getmaxyx()
      toPrintStrLen = len(singleLines[0])
      spaceLeft = maxx - (x + toPrintStrLen + 1)

      #check to see if line fits. 
      if spaceLeft < 0:
        
        #go to the place the split is wanted and find a space 
        toSplitIndex = singleLines[0].rfind(' ', 0, (spaceLeft + toPrintStrLen))
        
        if toSplitIndex < 1:
          #failed to find a space: Force a split
          toSplitIndex = spaceLeft + toPrintStrLen
          
        singleLines.insert(1,singleLines[0][toSplitIndex:])
        singleLines[0] = singleLines[0][:toSplitIndex]

      #FIXME -> in extremely small screens (approx 25 chars or less) errors start for
      #printing outside screen area.  Prob. some bad math in the word splitting of 1 letter
      #FIXME -> might want to protect this with a try when ready for stable release
      self._output.addstr(singleLines.pop(0),
                        combinedAttr|
                        curses.color_pair(int(self._ansiClrtoClrPairDict[splitColor[1]])))
        
      counter += 1

    self._output.refresh()

  
  def write(self, message):
    """
    Sends a message object to the display
    """
    if type(message) == type(""):
      message = ui.Message(message, ui.LTDATA)

    if message.data == '':
      return

    if message.type == ui.USERDATA and message.data[-1] == "\n":
      message.data = message.data[:-1]

    # set prompt
    myPrompt = self.getPrompt(message.type)
    
    # chop up message by color
    if message.data.find(self._colorEscape) == -1:
      newColorLines = [message.data]
     
    else:
      newColorLines = message.data.split(self._colorEscape)
     
    #check for old color ie imcomplete line
    if self._isPartialLine == 1:
      #read to m
      fullLine = self._partialLine + newColorLines.pop(0)
      endLoc = 0
      endLoc = fullLine.find('m')
      self._color = self.getColor(fullLine[1:endLoc])
      self._isPartialLine = 0
      self._partialLine = ''
      self.strtoDisplay((fullLine[(endLoc + 1):],self._color,myPrompt))

    else:  
      #first line has no color data
      self.strtoDisplay((newColorLines.pop(0),self._color,myPrompt))

    # read off all data up to m
    for aColorLine in newColorLines:
      endLoc = 0
      endLoc = aColorLine.find('m')

      #check for partial color code ie imcomplete line
      if endLoc == -1:
        self._isPartialLine = 1
        self._partialLine = aColorLine
        continue

      colorPart = aColorLine[1:endLoc]
      
      #remove everything upto and including m
      messagePart = aColorLine[(endLoc+1):]
      self._color = self.getColor(colorPart)
      
      # send results to screen
      self.strtoDisplay((messagePart,self._color,myPrompt))
  
  def run(self):
    """ Reads through keys typed one by one and handles them accordingly."""
    while not self._shutdown:
      newchar = self._input.getch()
      
      if newchar == 10:
        self.handleinput(string.join(self._newline, ''))
        self._newline = []
        self._input.deleteln()
	self._input.move(1,0)

      elif newchar == 13:
        continue

      elif (newchar == curses.KEY_DC or 
        newchar == curses.KEY_BACKSPACE or 
        newchar == 8 or newchar == 127):
	
        if len(self._newline) > 0:
          self._newline = self._newline[:-1]
          (y,x) = self._input.getyx()
          self._input.delch(y, x - 1)

      elif newchar == 21:
        self._input.erase()
        self._newline = []

      elif newchar > 0 and newchar < 256:
        self._input.addch(newchar)
        self._newline.append(chr(newchar))


  def refresh_all(self):
    """
    Refreshes the display.
    """
    self._main.refresh()


  def echo(self, yesno):
    """
    Overridden function.  Changes echo to yesno (hopefully
    either a 1 or 0).
    """
    self._echoon = yesno
