#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 1999 - 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id: tkui.py,v 1.25 2002/12/22 23:07:21 willhelm Exp $
#######################################################################
"""
This is a tk oriented user interface for lyntin.  Based on
Lyntin, but largely re-coded in various areas.
"""

import os, Tkinter, tkFont, ScrolledText, copy, types
import ansi, ui, hooks, event, engine, exported, lyntin, utils

UNICODE_ENCODING = "latin-1"

HELP_TEXT = """The tkui uses the Tk widget set and provides a graphical interface 
to Lyntin.  It also has the following additional functionality:

 - numpad bindings (VK_NUMPAD0 through VK_NUMPAD9)
 - function key bindings (VK_F2 through VK_F12)
 - pgup and pgdown scroll back (escape to get rid of the split 
   screen)
 - up and down command line history
 - ctrl-u removal of text
 - ctrl-c copy from the text buffer and ctrl-v paste into the command
   buffer (in Windows)
 - ctrl-t autotyper

To bind function key and numpad bindings, create an alias for the
symbol.  For example:

   #alias {VK_NUMPAD2} {south}
"""

"""
0 -- all off
1 -- bold
5 -- blinking (which we don't support)
7 -- reverse  (which we don't support)
8 -- hidden   (which we don't support)
"""
txt_attribs = {"0": "off",
               "1": "bold"}


# the complete list of foreground color codes and what color they
# map to in RGB.
fg_color_codes = {"30": "#000000",
                  "31": "#aa0000",
                  "32": "#00dd00",
                  "33": "#daa520",
                  "34": "#0000aa",
                  "35": "#bb00bb",
                  "36": "#00dddd",
                  "37": "#aaaaaa",
                  "b30": "#666666",
                  "b31": "#ff3333",
                  "b32": "#00ff3f",
                  "b33": "#ffff00",
                  "b34": "#2222ff",
                  "b35": "#ff33ff",
                  "b36": "#90ffff",
                  "b37": "#ffffff" }

# the complete list of background color codes and what color they
# map to in RGB.
bg_color_codes = {"40": "#000000",
                  "41": "#ff0000",
                  "42": "#00ff00",
                  "43": "#daa520",
                  "44": "#0000aa",
                  "45": "#ff00ff",
                  "46": "#00dddd",
                  "47": "#bbbbbb",
                  "b40": "#777777",
                  "b41": "#fa6072",
                  "b42": "#00ff7f",
                  "b43": "#ffff00",
                  "b44": "#2222ff",
                  "b45": "#ee82ee",
                  "b46": "#90ffff",
                  "b47": "#ffffff" }

# this is the default color--it's what we use when the mud hasn't
# specified a color yet.  this might get a little fishy.
DEFAULT = [0, 37, -1]

myui = None

def get_ui_instance():
  global myui
  if myui == None:
    myui = Tkui()
  return myui

class Tkui(ui.BaseUI):
  """
  This is a ui class which handles the complete Tk user interface.
  """
  def __init__(self):
    """ Initializes."""
    ui.BaseUI.__init__(self)

    # map of session -> (bold, foreground, background)
    self._currcolors = {}

    # ses -> string
    self._unfinishedcolor = {}

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
    exported.hook_register("mudecho_hook", self.echo)
    exported.hook_register("startup_hook", self.startui)
    exported.hook_register("to_user_hook", self.write)


  def startui(self, args):
    """ Starts up the main thread."""
    global HELP_TEXT
    exported.add_help("tkui", HELP_TEXT)
    engine.myengine.startthread("ui", self._tk.mainloop)
    exported.write_message("For tk help type \"#help tkui\".")
    exported.add_command("colorcheck", colorcheck_cmd)


  def settitle(self, title = ''):
    """
    Sets the title bar.

    @param title: the title to set
    @type  title: string
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
    if tkevent.char:
      # we do this little song and dance so as to pass events
      # we don't want to deal with to the entry widget essentially
      # by creating a new event and tossing it in the event list.
      args = ('event', 'generate', self._entry, "<KeyPress>")
      args = args + ('-rootx', tkevent.x_root)
      args = args + ('-rooty', tkevent.y_root)
      args = args + ('-keycode', tkevent.keycode)
      args = args + ('-keysym', tkevent.keysym)

      self._tk.tk.call(args)

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


  def echo(self, args):
    """ This turns echo on and off on the CommandEntry widget."""
    yesno = args[0]
    if yesno==1:
      # echo on
      self._do_i_echo = 1
      self._entry.configure(show='')
    else:
      # echo off
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
    if (temp.isdigit() and int(temp) > 800):
      self._txt.delete ("1.0", "100.end")

  def write(self, args):
    """ This writes text to the text buffer for viewing by the user.

    This is overridden from the 'ui.BaseUI'.
    """
    message = args[0]
    if type(message) == types.StringType:
      message = ui.Message(message, ui.LTDATA)

    line = message.data
    ses = message.session

    if line == '' or self.showTextForSession(ses) == 0:
      return

    if message.type == ui.ERROR:
      if line[-1] == "\n":
        self._txt.insert('end', line[:-1], "44")
        self._txt.insert('end', "\n")
      else:
        self._txt.insert('end', line, "44")

    elif message.type == ui.USERDATA:
      if lyntin.mudecho == 1:
        if line[-1] == "\n":
          self._txt.insert('end', line[:-1], "44")
          self._txt.insert('end', "\n")
        else:
          self._txt.insert('end', line, "44")

    elif message.type == ui.LTDATA:
      if line[-1] == "\n":
        line = "# " + line[:-1].replace("\n", "\n# ") + "\n"
      else:
        line = "# " + line.replace("\n", "\n# ")

      self._txt.insert('end', line)

    elif message.type == ui.MUDDATA:
      index = 0
      start = 0

      # we prepend the session name to the text if this is not the 
      # current session sending text.
      if (ses != None and ses != exported.get_current_session()):
        pretext = "[%s]" % ses.getName()

        if line[-1] == "\n":
          line = (pretext + line[:-1].replace("\n", "\n" + pretext) + "\n")
        else:
          line = pretext + line.replace("\n", "\n" + pretext)


      # we remove all \\r stuff because it's icky.
      line = line.replace("\r", "")

      tokens = ansi.split_ansi_from_text(line)

      # each session has a saved current color for mud data.  we grab
      # that current color--or user our default if we don't have one
      # for the session yet.
      if self._currcolors.has_key(ses):
        color = self._currcolors[ses]
      else:
        color = copy.copy(DEFAULT)

      # some sessions have an unfinished color as well--in case we
      # got a part of an ansi color code in a mud message, and the other
      # part is in another message.
      if self._unfinishedcolor.has_key(ses):
        leftover = self._unfinishedcolor[ses]
      else:
        leftover = ""

      for mem in tokens:
        if ansi.is_color_token(mem):
          color, leftover = ansi.figure_color([mem], color, leftover)

        else:

          if color[1] == -1:
            fg = "37"
          else:
            fg = str(color[1])

          if color[0] == 1:
            fg = "b" + fg

          if color[2] == -1:
            self._txt.insert('end', mem, fg)

          else:
            bg = str(color[2])
            self._txt.insert('end', mem, (fg, bg))


      self._unfinishedcolor[ses] = leftover
      self._currcolors[ses] = color

    self._clipText()
    self._yadjust()

  def convertColor(self, name):
    """
    Tk has this really weird color palatte.  So I switched to using
    color names in most cases and rgb values in cases where I couldn't
    find a good color name.

    This method allows me to specify either an rgb or a color name
    and it converts the color names to rgb.

    arguments:

      'name' -- (string) either an rgb (ex. #000000) or a name (ex. black)

    returns:

      (string) the rgb color value (ex. #000000)
    """
    if name[0] == "#":
      return name

    rgb = self._tk._getints(self._tk.tk.call('winfo', 'rgb', self._txt, name))
    rgb = "#%02x%02x%02x" % (rgb[0]/256, rgb[1]/256, rgb[2]/256) 
    print name, "converted to: ", rgb

    return rgb

  def _initColorTags(self):
    """ Sets up Tk tags for the text widget (fg/bg)."""
    for ck in fg_color_codes.keys():
      color = self.convertColor(fg_color_codes[ck])
      self._txt.tag_config(ck, foreground=color)
      self._txtbuffer.tag_config(ck, foreground=color)

    for ck in bg_color_codes.keys():
      self._txt.tag_config(ck, background=bg_color_codes[ck])
      self._txtbuffer.tag_config(ck, background=bg_color_codes[ck])

  def colorCheck(self):

    fgkeys = ['30','31','32','33','34','35','36','37']
    bgkeys = ['40','41','42','43','44','45','46','47']

    self._txt.insert('end', 'color check:\n')
    for bg in bgkeys:
      for fg in fgkeys:
        self._txt.insert('end', str(fg), (fg, bg))
        self._txt.insert('end', str("b" + fg), ("b" + fg, bg))
      self._txt.insert('end', '\n')

      for fg in fgkeys:
        self._txt.insert('end', str(fg), (fg, "b" + bg))
        self._txt.insert('end', str("b" + fg), ("b" + fg, "b" + bg))
      self._txt.insert('end', '\n')

    self._txt.insert('end', '\n')
    self._txt.insert('end', '\n')


class CommandEntry(Tkinter.Entry):
  """ This class handles the user input area."""

  def __init__(self, master, partk, **kw):
    """ Initializes and sets the key-bindings."""
    self._partk = partk
    self._inputstack = []
    self._autotyper = None
    self._autotyper_ses = None

    apply(Tkinter.Entry.__init__, (self, master), kw)

    self.bind("<KeyPress-Return>", self.createInputEvent)

    self.bind("<KeyPress-Up>", self.insertPrevCommand)
    self.bind("<KeyPress-Down>", self.insertNextCommand)
    self.unbind("<KeyPress-Tab>")
    self.bind("<KeyPress-Tab>", self.insertTab)
    self.bind("<KeyPress-Prior>", self.callPrior)
    self.bind("<KeyPress-Next>", self.callNext)

    self.bind("<Control-KeyPress-t>", self.startAutotyper)
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
    val = fix_unicode(self.get())
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
    ses = exported.get_current_session()
    action = exported.get_manager("alias").getAlias(ses, binding)
    if action:
      self._partk.handleinput(action)
      return 1
    else:
      exported.write_error("%s is currently not bound to anything." % binding)
      return 0

  def callBinding(self, tkevent):
    """ Handles arbitrary bindings of function call keypresses."""

    # handle all the function keys except F1
    if tkevent.keysym == "F1":
      self._partk.handleinput(lyntin.commandchar + "help")
      return "break"
      
    if self._executeBinding("VK_%s" % tkevent.keysym) == 1:
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


  def startAutotyper(self, tkevent):
    """
    This will start the autotyper. It will be called if you type <Ctrl>+<t>.
    There can be only one autotyper at a time. The autotyper cannot be started
    for the common session.
    """
    
    if self._autotyper != None:
      exported.write_error("cannot start autotyper: already started.")
      return
    
    session = exported.get_current_session()
    
    if session.getName() == "common":
      exported.write_error("autotyper cannot be applied to common session.")
      return
    
    self._autotyper = Autotyper(self._partk._tk, self.autotyperDone)
    self._autotyper_ses = session
    
    exported.write_message("autotyper: started.")

  def autotyperDone(self, data):
    """
    This is a callback for the autotyper. It will be called when the autotyper
    is finished.
    
    arguments:
    
      'data' -- (string or None) the autotyper data. None if the user clicked
                on the "Cancel" button or closed the autotyper window.
    
    """
    
    if data != None:
      self._autotyper_ses.writeSocket(data)
    
    self._autotyper = None
    self._autotyper_ses = None
    
    exported.write_message("autotyper: done.")

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

class Autotyper:
  """
  Autotyper class, it generates the autotyper window, waits for entering text
  and then calls a function to work with the text.
  """
  
  def __init__(self, master, sendfunc):
    """
    Initializes the autotyper.
    
    arguments:
    
      'master' -- (Tkinter.Tk instance) the main tk window
      'sendfunc' -- (function) the callback function
    """
    self._sendfunc = sendfunc
    
    self._tk = Tkinter.Toplevel(master)
    
    self._tk.geometry("400x300")
    self._tk.title("Lyntin -- Autotyper")
    
    self._tk.protocol("WM_DELETE_WINDOW", self.cancel)
    
    if os.name == "posix":
      fontname = "Courier"
    else:
      fontname = "Fixedsys"
    fnt = tkFont.Font(family=fontname, size=12)
    
    self._txt = ScrolledText.ScrolledText(self._tk, fg="black", bg="white",
      font=fnt, height=20)
    self._txt.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)
    
    self._send_btn = Tkinter.Button(self._tk, text="Send", command=self.send)
    self._send_btn.pack(side=Tkinter.LEFT, fill=Tkinter.X, expand=1)
    
    self._cancel_btn = Tkinter.Button(self._tk, text="Cancel",
      command=self.cancel)
    self._cancel_btn.pack(side=Tkinter.RIGHT, fill=Tkinter.X, expand=1)
    
    engine.myengine.startthread("autotyper", self._tk.mainloop)
  
  def send(self):
    """
    Will be called when the user clicks on the 'Send' button.
    """
    text = fix_unicode(self._txt.get(1.0, Tkinter.END))
    self._sendfunc(text)
    self._tk.destroy()
  
  def cancel(self):
    """
    Will be called when the user clicks on the 'Cancel' button.
    """
    self._sendfunc(None)
    self._tk.destroy()

def fix_unicode(text):
    """
    Unicode to standard string translation, fixes unicode bug.
    """
    if type(text) == unicode:
        return text.encode(UNICODE_ENCODING)
    else:
        return text

def colorcheck_cmd(ses, args, input):
  """
  Prints out all the colors so you can verify that things are working
  properly.
  """
  myengine = exported.get_engine()
  myengine._ui_lock.acquire(1)
  try:
    myengine._ui.colorCheck()
  finally:
    myengine._ui_lock.release()

# Local variables:
# mode:python
# py-indent-offset:2
# tab-width:2
# End:
