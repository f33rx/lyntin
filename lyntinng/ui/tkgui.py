#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 1999 - 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: tkgui.py,v 1.31 2002/04/24 04:38:24 willhelm Exp $
#######################################################################
"""
This is a tk oriented user interface for lyntin.  Based on
Lyntin, but largely re-coded in various areas.
"""

import string, os, Tkinter, tkFont
import ui, hooks, event, engine, exported, lyntin

"""
0 -- all off
1 -- bold
5 -- blinking (which we don't support)
7 -- reverse  (which we don't support)
8 -- hidden   (which we don't support)
"""
txt_attribs = {"0": "off",
               "1": "bold"}

fg_color_codes = {"30": "#000000",
                  "31": "#c00000",
                  "32": "#008000",
                  "33": "#808000",
                  "34": "#0000c0",
                  "35": "#c000c0",
                  "36": "#008080",
                  "37": "#c0c0c0",
                  "b30": "#808080",
                  "b31": "#ff6060",
                  "b32": "#00ff00",
                  "b33": "#ffff00",
                  "b34": "#8080ff",
                  "b35": "#ff40ff",
                  "b36": "#00ffff",
                  "b37": "#ffffff" }

bg_color_codes = {"40": "#000000",
                  "41": "#c00000",
                  "42": "#008000",
                  "43": "#808000",
                  "44": "#0000c0",
                  "45": "#c000c0",
                  "46": "#008080",
                  "47": "#c0c0c0",
                  "b40": "#808080",
                  "b41": "#ff6060",
                  "b42": "#00ff00",
                  "b43": "#ffff00",
                  "b44": "#8080ff",
                  "b45": "#ff40ff",
                  "b46": "#00ffff",
                  "b47": "#ffffff" }


class TkGui(ui.BaseUI):
  """
  This is a ui class which handles the complete Tk user interface.
  """
  def __init__(self):
    """ Initializes."""
    ui.BaseUI.__init__(self)

    # (bold, foreground, background)
    self._currcolors = [0, "37", "40"]

    # (bold, foreground, background)
    self._regcolors = [0, "37", "40"]

    self._unfinishedcolor = (0, "")
    self._viewhistory = 0
    self._do_i_echo = 1
    self._tk = Tkinter.Tk()
    self._tk.geometry("800x600")
    self.settitle()

    if os.name == 'posix':
      fnt = tkFont.Font(family="Courier", size=12)
    else:
      fnt = tkFont.Font(family="Fixedsys", size=12)

    self._entry = CommandEntry(self._tk, 
                               self,
                               fg='white', 
                               bg='black',
                               insertbackground='yellow',
                               font=fnt, 
                               insertwidth='2')

    self._txt = Tkinter.Text(self._tk, {'fg': 'white', 
                                        'bg': 'black',
                                        'font': fnt,
                                        'height': 20})

    # handles improper keypresses
    self._txt.bind("<KeyPress>", self._ignoreThis)

    self._txtbuffer = Tkinter.Text(self._tk, {'fg': 'white', 
                                              'bg': 'black', 
                                              'font': fnt, 
                                              'height': 20})


    # these deal with catching improper keypresses
    self._txtbuffer.bind("<KeyPress-Escape>", self.escape)
    self._txtbuffer.bind("<KeyPress>", self._ignoreThis)

    # set up the scrollbar for the txtbuffer widget
    self._scrollVertical = Tkinter.Scrollbar(self._tk, 
                                             orient=Tkinter.VERTICAL)
    self._txt.configure(yscrollcommand=self._scrollVertical.set)
    self._scrollVertical.config(command=self._txt.yview)
    self._scrollVertical.pack(side=Tkinter.RIGHT, 
                              anchor=Tkinter.E, 
                              fill=Tkinter.Y)

    self._entry.pack({'side': 'bottom', 'fill': 'both'})
    self._entry.focus_set()

    self._txt.pack({'side': 'bottom', 'fill': 'both', 'expand': 1})

    self._initColorTags()
    hooks.echo_hook.register(self.echo)
    hooks.startup_hook.register(self.startui)


  def startui(self, args):
    """ Starts up the main thread."""
    hooks.to_user_hook.register(self.write)
    engine.myengine.startthread("ui", self._tk.mainloop)


  def settitle(self, title = ''):
    """ Sets the title bar.

    arguments:

      'title' -- (string) the title to set

    """
    if title:
      self._tk.title(lyntin.LYNTINTITLE + title)
    else:
      self._tk.title(lyntin.LYNTINTITLE)


  def _ignoreThis(self, tkevent):
    """ This catches keypresses from the history buffer."""
    # kludge so that ctrl-c doesn't get caught allowing windows
    # users to copy the buffer....
    if tkevent.keycode == 17 or tkevent.keycode == 67:
      return

    self._entry.focus()
    return "break"


  def pageUp(self):
    """ Handles prior (Page-Up) events."""
    if self._viewhistory == 0:
      self._txtbuffer.pack({'after': self._txt, 
                            'side': 'bottom', 
                            'fill': 'both', 
                            'expand': 1})

      self._viewhistory = 1
      self._txtbuffer.delete ("1.0", "end")
      lotofstuff = self._txt.get ('1.0', 'end')
      self._txtbuffer.insert ('end', lotofstuff)
      for t in self._txt.tag_names():
        taux=None
        tst=0
        for e in self._txt.tag_ranges(t):
          if tst==0:
            taux=e
            tst=1
          else:
            tst=0
            self._txtbuffer.tag_add(t,str(taux),str(e))

      self._txtbuffer.yview('moveto', '1')
      if os.name != 'posix':
        self._txtbuffer.yview('scroll', '20', 'units')
      self._tk.update_idletasks()
      self._txt.yview('moveto','1.0')
      if os.name != 'posix':
        self._txt.yview('scroll', '220', 'units')

    else:
      # yscroll up stuff
      self._txtbuffer.yview('scroll', '-15', 'units')


  def pageDown(self):
    """ Handles next (Page-Down) events."""
    if self._viewhistory == 1:
      # yscroll down stuff
      self._txtbuffer.yview('scroll', '15', 'units')


  def escape(self, tkevent):
    """ Handles escape (Escape) events."""
    if self._viewhistory == 1:
      self._txtbuffer.forget()
      self._viewhistory = 0
    else:
      self._entry.clearInput()


  def echo(self, yesno):
    """ This turns echo on and off on the CommandEntry widget."""
    if yesno==1:
      self._do_i_echo = 1
      self._entry.configure(show='')
    else:
      self._do_i_echo = 0
      self._entry.configure(show='*')


  def _yadjust(self):
    """ Handles y scrolling after text insertion."""
    self._txt.yview('moveto', '1')
    # if os.name != 'posix':
    self._txt.yview('scroll', '20', 'units')

  def _clipText(self):
    """
    Scrolls the text buffer up so that the new text written at
    the bottom of the text buffer can be seen.
    """
    temp = self._txt.index("end")
    ind = temp.find(".")
    temp = temp[:ind]
    if (int(temp) > 800):
      self._txt.delete ("1.0", "100.end")

  def write(self, message):
    """ This writes text to the text buffer for viewing by the user.

    This is overridden from the 'ui.BaseUI'.
    """
    if type(message) == type(''):
      message = ui.Message(message, ui.LTDATA)

    if message.data == '':
      return

    if message.type == ui.ERROR:
      if message.data[-1] == "\n":
        self._txt.insert('end', message.data[:-1], "44")
        self._txt.insert('end', "\n")
      else:
        self._txt.insert('end', message.data, "44")

    elif message.type == ui.USERDATA:
      if lyntin.echo == 1:
        if message.data[-1] == "\n":
          self._txt.insert('end', message.data[:-1], "44")
          self._txt.insert('end', "\n")
        else:
          self._txt.insert('end', message.data, "44")

    elif message.type == ui.LTDATA:
      if message.data[-1] == "\n":
        message.data = "# " + message.data[:-1].replace("\n", "\n# ") + "\n"
      else:
        message.data = "# " + message.data.replace("\n", "\n# ")

      self._txt.insert('end', message.data)

    elif message.type == ui.TESTDATA:
      self._txt.insert('end', message.data, "42")

    elif message.type == ui.MUDDATA:
      index = 0
      start = 0

      if (message.session != None 
          and message.session != exported.get_current_session()):
        pretext = "[" + message.session.getName() + "] "

        if message.data[-1] == "\n":
          message.data = (pretext + 
                          message.data[:-1].replace("\n", "\n" + pretext) + 
                          "\n")
        else:
          message.data = pretext + message.data.replace("\n", "\n" + pretext)

      # first we remove all \\r stuff
      line = message.data.replace("\r", "")

      # then we handle unfinished colors--ansi color codes can
      # be split between calls to write.
      if self._unfinishedcolor[0] == 1:
      
        index = line.find("m")

        if index == -1:
          self._unfinishedcolor = (1,
                                   self._unfinishedcolor[1] + line[:index])
        else:
          self._colorChange(self._unfinishedcolor[1] + line[:index]) 
          self._unfinishedcolor = (0, "")

        start = index + 1


      # now we handle all the text
      index = line.find(chr(27), index)
      while index > -1:
        cstart = index

        self._txt.insert('end', 
                         line[start:cstart], 
                         (self._currcolors[1], self._currcolors[2]))

        temp = line.find("m", index)
        if temp == -1:
          self._unfinishedcolor = (1, line[cstart:])
          line = line[:cstart]
        else:   
          self._colorChange(line[cstart:temp])
          start = temp + 1

        index = line.find(chr(27), index+1)


      if self._unfinishedcolor[0] == 0:
        self._txt.insert('end', 
                         line[start:], 
                         (self._currcolors[1], self._currcolors[2]))

    self._clipText()
    self._yadjust()


  def _colorChange(self, text):
    """
    Takes in a string and parses it into a series of numbers,
    then sets the current colors accordingly.
    """
    if text[0] == chr(27):
      # we strip off the ESC and the [
      newcolor = text[2:]

      # check to see if there's no actual color, or if
      # it's ^[0m which resets the colors
      if newcolor == '' or newcolor == "0":
        self._currcolors[:] = self._regcolors[:]
        return

      numlist = newcolor.split(";")
      numlist.sort()

      for num in numlist:
        if txt_attribs.has_key(num):
        
          if num == "1":
            self._currcolors[0] = 1

        elif fg_color_codes.has_key(num):
          if self._currcolors[0] == 1:
            self._currcolors[1] = "b" + num
          else:
            self._currcolors[0] = 0
            self._currcolors[1] = num

        elif bg_color_codes.has_key(num):
          if self._currcolors[0] == 1:
            self._currcolors[2] = "b" + num
          else:
            self._currcolors[0] = 0
            self._currcolors[2] = num


  def _initColorTags(self):
    """ Sets up Tk tags for the text widget (fg/bg)."""

    for ck in fg_color_codes.keys():
      self._txt.tag_config(ck, foreground=fg_color_codes[ck])
      self._txtbuffer.tag_config(ck, foreground=fg_color_codes[ck])

    for ck in bg_color_codes.keys():
      self._txt.tag_config(ck, background=bg_color_codes[ck])
      self._txtbuffer.tag_config(ck, background=bg_color_codes[ck])




class CommandEntry(Tkinter.Entry):
  """ This class handles the user input area."""

  def __init__(self, master, partk, **kw):
    """ Initializes and sets the key-bindings."""
    self._partk = partk
    self._inputstack = []

    apply(Tkinter.Entry.__init__, (self, master), kw)

    self.bind("<KeyPress-Return>", self.createInputEvent)

    self.bind("<KeyPress-Up>", self.insertPrevCommand)
    self.bind("<KeyPress-Down>", self.insertNextCommand)
    self.unbind("<KeyPress-Tab>")
    self.bind("<KeyPress-Tab>", self.insertTab)
    self.bind("<KeyPress-Prior>", self.callPrior)
    self.bind("<KeyPress-Next>", self.callNext)

    self.bind("<Control-KeyPress-u>", self.callKillLine)
    self.bind("<Control-KeyPress-Up>", self.callPushInputStack)
    self.bind("<Control-KeyPress-Down>", self.callPopInputStack)
    self.bind("<KeyPress-Escape>", self.callEsc)

    self.bind("<KeyPress-F1>", self.callBinding) # reserved for help

    self.bind("<KeyPress-F2>", self.callBinding)
    self.bind("<KeyPress-F3>", self.callBinding)
    self.bind("<KeyPress-F4>", self.callBinding)
    self.bind("<KeyPress-F5>", self.callBinding)
    self.bind("<KeyPress-F6>", self.callBinding)
    self.bind("<KeyPress-F7>", self.callBinding)
    self.bind("<KeyPress-F8>", self.callBinding)
    self.bind("<KeyPress-F9>", self.callBinding)
    self.bind("<KeyPress-F10>", self.callBinding)
    self.bind("<KeyPress-F11>", self.callBinding)
    self.bind("<KeyPress-F12>", self.callBinding)

    if os.name!="posix":
      self.bind("<KeyPress-8>", self.callKP8)
      self.bind("<KeyPress-6>", self.callKP6)
      self.bind("<KeyPress-4>", self.callKP4)
      self.bind("<KeyPress-2>", self.callKP2)
      self.bind("<KeyPress-9>", self.callKP9)
      self.bind("<KeyPress-7>", self.callKP7)
      self.bind("<KeyPress-5>", self.callKP5)
      self.bind("<KeyPress-3>", self.callKP3)
      self.bind("<KeyPress-1>", self.callKP1)

    else:
      self.bind("<KeyPress-KP_Up>", self.callKP8)
      self.bind("<KeyPress-KP_Right>", self.callKP6)
      self.bind("<KeyPress-KP_Left>", self.callKP4)
      self.bind("<KeyPress-KP_Down>", self.callKP2)
      self.bind("<KeyPress-KP_Prior>", self.callKP9)
      self.bind("<KeyPress-KP_Home>", self.callKP7)
      self.bind("<KeyPress-KP_Begin>", self.callKP5)
      self.bind("<KeyPress-KP_Next>", self.callKP3)
      self.bind("<KeyPress-KP_End>", self.callKP1)

    self.hist_index = -1
    self._partk = partk
    self.saveinputhighlight = 0
        
  def createInputEvent(self, tkevent):
    """ Handles the <KeyPress-Return> event."""
    val = self.get()
    self._partk.handleinput(val)

    # self._inputstack.insert(0, val)
    # if len(self._inputstack) > 30:
    #   self._inputstack = self._inputstack[:-1]

    if self.saveinputhighlight == 1:
      self.selection_range(0, 'end')
    else:
      self.delete(0, 'end')
    self.hist_index = -1

  def _executeBinding(self, binding):
    """ Returns the alias for this keybinding."""
    session = engine.myengine.currentSession()
    action = session.getManager("alias").getAlias(binding)
    if action:
      self._partk.handleinput(action)
      return 1
    else:
      exported.write_error(binding + " is currently not bound to anything.")
      return 0

  def callBinding(self, tkevent):
    """ Handles arbitrary bindings of function call keypresses."""

    # handle all the function keys except F1
    if tkevent.keysym == "F1":
      self._partk.handleinput(lyntin.commandchar + "help")
      return "break"
      
    if self._executeBinding("VK_" + tkevent.keysym) == 1:
      return "break"

    # these two lines help in debugging stuff we bound
    # but don't know how to handle because I can't seem to
    # find a solid listing of Tk keysyms (grrrrrrr).
    # print repr(tkevent)
    # print repr(tkevent.__dict__)


  def callKP9(self, tkevent):
    if tkevent.keycode == 105 or os.name=='posix':
      if self._executeBinding("VK_NUMPAD9") == 1:
        return "break"

  def callKP8(self, tkevent):
    if tkevent.keycode == 104 or os.name=='posix':
      if self._executeBinding("VK_NUMPAD8") == 1:
        return "break"

  def callKP7(self, tkevent):
    if tkevent.keycode == 103 or os.name=='posix':
      if self._executeBinding("VK_NUMPAD7") == 1:
        return "break"

  def callKP6(self, tkevent):
    if tkevent.keycode == 102 or os.name=='posix':
      if self._executeBinding("VK_NUMPAD6") == 1:
        return "break"

  def callKP5(self, tkevent):
    if tkevent.keycode == 101 or os.name=='posix':
      if self._executeBinding("VK_NUMPAD5") == 1:
        return "break"

  def callKP4(self, tkevent):
    if tkevent.keycode == 100 or os.name=='posix':
      if self._executeBinding("VK_NUMPAD4") == 1:
        return "break"

  def callKP3(self, tkevent):
    if tkevent.keycode == 99 or os.name=='posix':
      if self._executeBinding("VK_NUMPAD3") == 1:
        return "break"

  def callKP2(self, tkevent):
    if tkevent.keycode == 98 or os.name=='posix':
      if self._executeBinding("VK_NUMPAD2") == 1:
        return "break"

  def callKP1(self, tkevent):
    if tkevent.keycode == 97 or os.name=='posix':
      if self._executeBinding("VK_NUMPAD1") == 1:
        return "break"


  def clearInput(self):
    """ Clears the text widget."""
    self.delete(0, 'end')
        
  def insertTab(self, tkevent):
    """ Handles the <KeyPress-Tab> event."""
    # self.insert(INSERT, '\t')
    pass
        
  def callPrior(self, tkevent):
    """ Handles the <KeyPress-Prior> event."""
    self._partk.pageUp()
        
  def callNext(self, tkevent):
    """ Handles the <KeyPress-Next> event."""
    self._partk.pageDown()
        
  def callEsc(self, tkevent):
    """ Handles the <KeyPress-Escape> event."""
    self._partk.escape(tkevent)
    
  def callKillLine(self, tkevent): 
    """ Handles the <Control-KeyPress-u> event."""
    self.delete(0,'end')

  def callPushInputStack(self, tkevent):
    """ Handles the <Control-KeyPress-Up> event."""
    self._inputstack.append((self.index('insert'),self.get()))
    self.delete(0,'end')

  def callPopInputStack(self,tkevent):
    """ Handles the <Control-KeyPress-Down> event."""
    if len(self._inputstack) < 1:
      return
    poppage = self._inputstack.pop()
    self.delete(0,'end')
    self.insert(0,poppage[1])
    self.icursor(poppage[0])
        
  def insertPrevCommand(self, tkevent):
    """ Handles the <KeyPress-Up> event."""
    hist = exported.get_history()
    if self.hist_index == -1:
      self.current_input = self.get()
    if self.hist_index < len(hist) - 1:
      self.hist_index = self.hist_index + 1
      self.delete(0, 'end')
      self.insert(0, hist[self.hist_index])

  def insertNextCommand(self, tkevent):
    """ Handles the <KeyPress-Down> event."""
    hist = exported.get_history()
    if self.hist_index == -1:
      return
    self.hist_index = self.hist_index - 1
    if self.hist_index == -1:
      self.delete(0, 'end')
      self.insert(0, self.current_input)
            
    else:
      self.delete(0, 'end')
      self.insert(0, hist[self.hist_index])
