#######################################################################
# This file is part of Lyntin.
# copyright (c) Will Guaraldi 2001
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
# $Id$
#######################################################################
"""
This is a tk oriented user interface for lyntin.  Based on
Lyntin, but largely re-coded in various areas.
"""

# from Tkinter import *
import string, os, Tkinter, tkFont
import ui, event, engine

"""
0 -- all off
1 -- bold
5 -- blinking (which we don't support)
7 -- reverse  (which we don't support)
8 -- hidden   (which we don't support)
"""
txtAttribs = { "0": "off", 
               "1": "bold" }

fgColorCodes = {"30": "#000000",
                "31": "#c00000",
                "32": "#008000",
                "33": "#808000",
                "34": "#0000c0",
                "35": "#c000c0",
                "36": "#008080",
                "37": "#c0c0c0",
                "2030": "#808080",
                "2031": "#ff6060",
                "2032": "#00ff00",
                "2033": "#ffff00",
                "2034": "#8080ff",
                "2035": "#ff40ff",
                "2036": "#00ffff",
                "2037": "#ffffff" }

bgColorCodes = { "40": "#000000", 
                 "41": "red", 
                 "42": "#004411",
                 "43": "yellow", 
                 "44": "blue", 
                 "45": "magenta",
                 "46": "cyan", 
                 "47": "white", 
                 "50": "purple" }


class TkGui(ui.BaseUI):
   """
   This is a ui class which handles the complete Tk user interface.
   """
   def __init__(self):
      """ Initializes."""
      ui.BaseUI.__init__(self)
      self._currcolors = (0, 37, 40)
      self._regcolors = (0, 37, 40)
      self._unfinishedcolor = (0, "")
      self._viewhistory = 0
      self._do_i_echo = 1
      self._tk = Tkinter.Tk()
      self._tk.geometry("800x600")
      self._tk.title("Lyntin -- The Hacker's Mudclient")

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
                                        'state': 'disabled', 
                                        'height': 20})

      self._txtbuffer = Tkinter.Text(self._tk, {'fg': 'white', 
                                              'bg': 'black', 
                                              'font': fnt, 
                                              'height': 20})

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

      self.initColorTags()
      engine.myengine.register(engine.ECHOFREQ, self.echo)
      engine.myengine.register(engine.STARTUPFREQ, self.startui)


   def startui(self, args):
      """ Starts up the main thread."""
      engine.myengine.startthread("ui", self._tk.mainloop)


   def settitle(self, title = ''):
      """ Sets the title bar."""
      if title != '':
         self._tk.title("Lyntin -- The Hacker's Mudclient " + title)
      else:
         self._tk.title("Lyntin -- The Hacker's Mudclient")


   def pageUp(self):
      """ Handles prior (Page-Up) events."""
      if self._viewhistory == 0:
         self._txtbuffer.pack({'after': self._txt, 
                              'side': 'bottom', 
                              'fill': 'both', 
                              'expand': 1})
         self._viewhistory = 1
         # self._txtbuffer.configure(state='normal')
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
         # self._txtbuffer.configure(state='disabled')

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


   def escape(self):
      """ Handles escape (Escape) events."""
      if self._viewhistory == 1:
         self._txtbuffer.forget()
         self._viewhistory = 0
      else:
         self._entry.clearInput()


   def echo(self, yesno):
      """ This turns echo on and off on the CommandEntry widget.

      This is overridden from the baseui.
      """
      if yesno==1:
         self._do_i_echo = 1
         self._entry.configure(show='')
      else:
         self._do_i_echo = 0
         self._entry.configure(show='*')


   def write(self, message):
      """ This writes text to the text buffer for viewing by the user.

      This is overridden from the baseui.
      """
      if type(message) == type(''):
         message = ui.Message(message, ui.SBDATA)

      if message.data == '':
         return

      if message.type == ui.ERROR:
         self._txt.configure(state='normal')
         self._txt.insert('end', message.data, "44")
         self._txt.insert('end', "\n")
         self._txt.configure(state='disabled')

         self._txt.yview('moveto', '1')
         if os.name != 'posix':
            self._txt.yview('scroll', '20', 'units')

      elif message.type == ui.SBDATA:
         self._txt.configure(state='normal')
         message.data = "# " + string.replace(message.data, "\n", "\n# ")
         self._txt.insert('end', message.data)
         self._txt.insert('end', "\n")
         self._txt.configure(state='disabled')

         self._txt.yview('moveto', '1')
         if os.name != 'posix':
            self._txt.yview('scroll', '20', 'units')

      elif message.type == ui.TESTDATA:
         self._txt.configure(state='normal')
         self._txt.insert('end', message.data, "42")
         self._txt.insert('end', "\n")
         self._txt.configure(state='disabled')

         self._txt.yview('moveto', '1')
         if os.name != 'posix':
            self._txt.yview('scroll', '20', 'units')

      elif message.type == ui.USERDATA:
         self._txt.configure(state='normal')
         self._txt.insert('end', message.data, "44")
         self._txt.insert('end', "\n")
         self._txt.configure(state='disabled')

         self._txt.yview('moveto', '1')
         if os.name != 'posix':
            self._txt.yview('scroll', '20', 'units')

      elif message.type == ui.MUDDATA:
         index = 0
         start = 0
         end = 0
         line = string.replace(message.data, "\r", "")

         if self._unfinishedcolor[0] == 1:
            cstart = index
            while index < len(line) and line[index] != "m":
               index = index + 1

            self._unfinishedcolor = (self._unfinishedcolor[0], 
                                self._unfinishedcolor[1] + line[cstart:index])
            if index < len(line):
               self.colorchange(self._unfinishedcolor[1]) 
               self._unfinishedcolor = (0, "")
            else:
               self._unfinishedcolor = (1, 
                            self._unfinishedcolor[1] + line[cstart:index - 1])

            start = index + 1

         self._txt.configure(state='normal')
         while index < len(line):
            if line[index] == chr(27):
               cstart = index
               end = index

               if self._currcolors == self._regcolors:
                  self._txt.insert('end', line[start:end])
               else:
                  self._txt.insert('end', line[start:end], self._currcolors[1])

               while index < len(line) and line[index] != "m":
                  index = index + 1

               if index == len(line):
                  self._unfinishedcolor = (1, line[cstart:index])
               else:   
                  self.colorchange(line[cstart:index])

               start = index + 1
            index = index + 1 
         end = index

         if self._currcolors == self._regcolors:
            self._txt.insert('end', line[start:end])
         else:
            self._txt.insert('end', line[start:end], self._currcolors[1])
         self._txt.configure(state='disabled')

         self._txt.yview('moveto', '1')
         if os.name != 'posix':
            self._txt.yview('scroll', '20', 'units')

         self.ClipText()


   def colorchange(self, txt):
      """
      Takes in a string and parses it into a series of numbers,
      then sets the current colors accordingly.
      """
      if txt[0] == chr(27):
      # if txt[0] == chr(27) and txt[len(txt)-1] == "m":
         newcolor = txt[2:(len(txt))]
         # if newcolor == "0":
         if newcolor == "0" or newcolor == "":
            self._currcolors = self._regcolors
         else:
            numbers = string.split(newcolor, ";")
            for num in numbers:
               if fgColorCodes.has_key(num):
                  self._currcolors = (self._currcolors[0], int(num), self._currcolors[2])
               if bgColorCodes.has_key(num):
                  self._currcolors = (self._currcolors[0], self._currcolors[1], int(num))
               if txtAttribs.has_key(num):
                  self._currcolors = (int(num), self._currcolors[1], self._currcolors[2])
                  if num == "0":
                     self._currcolors = self._regcolors

            self._currcolors = (self._currcolors[0], self._currcolors[1] % 2000, self._currcolors[2])
            if self._currcolors[0] == 1:
               self._currcolors = (self._currcolors[0], self._currcolors[1] + 2000, self._currcolors[2])


   def initColorTags(self):
      """ Sets up Tk tags for the text widget (fg/bg)."""
      codes = fgColorCodes
      colorKeys = codes.keys()
      for ck in colorKeys:
         self._txt.tag_config(ck, foreground=codes[ck])
         self._txtbuffer.tag_config(ck, foreground=codes[ck])

      codes = bgColorCodes
      colorKeys = codes.keys()
      for ck in colorKeys:
         self._txt.tag_config(ck, background=codes[ck])
         self._txtbuffer.tag_config(ck, background=codes[ck])


   def ClipText(self):
      """
      Scrolls the text buffer up so that the new text written at
      the bottom of the text buffer can be seen.
      """
      temp = self._txt.index("end")
      ind = string.find(temp, ".")
      temp = temp[:ind]
      try:
         if (int(temp) > 800):
            self._txt.config(state=Tkinter.NORMAL)
            self._txt.delete ("1.0", "100.end")
            self._txt.config(state=Tkinter.DISABLED)
      except:
         pass


class CommandEntry(Tkinter.Entry):
   """ This class handles the user input area."""

   def __init__(self, master, partk, **kw):
      """ Initializes and sets the key-bindings."""
      self._partk = partk
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

      # self.bind("<KeyPress-F1>", self.callBinding) - reserved for help

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


         """
         try: 
            self.bind("<KeyPress-/>", self.callKPSlash)
            self.bind("<KeyPress-*>", self.callKPStar)
            self.bind("<KeyPress-minus>", self.callKPMinus)
            self.bind("<KeyPress-+>", self.callKPPlus)
         except:
            print "Some keys could not be bound."
         """
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
         """
         try: 
            self.bind("<KeyPress-KP_Divide>", self.callKPSlash)
            self.bind("<KeyPress-KP_Multiply>", self.callKPStar)
            self.bind("<KeyPress-KP_Subtract>", self.callKPMinus)
            self.bind("<KeyPress-KP_Add>", self.callKPPlus)
         except:
            print "Some keys could not be bound."
         """


      self.hist_index = -1
      self._partk = partk
      self.inputstack = []
      self.saveinputhighlight = 0
        
   def createInputEvent(self, tkevent):
      """ Handles the <KeyPress-Return> event."""
      val = self.get()
      self._partk.handleinput(val)

      self.inputstack.insert(0, val)
      if len(self.inputstack) > 30:
         self.inputstack = self.inputstack[:-1]

      if self.saveinputhighlight == 1:
         self.selection_range(0, 'end')
      else:
         self.delete(0, 'end')
      self.hist_index = -1

   def _executeBinding(self, binding):
      """ Returns the alias for this keybinding."""
      session = engine.myengine.currentSession()
      action = session.getAliasManager().getAlias(binding)
      if action:
         self._partk.handleinput(action)
         return 1
      else:
         engine.myengine.writeError(binding + 
                         " is currenly not bound to anything.")
         return 0

   def callBinding(self, tkevent):
      """ Handles arbitrary bindings of keypresses."""

      # handle all the function keys except F1
      if tkevent.keycode == 113 and tkevent.keysym == "F2":
         if self._executeBinding("VK_F2") == 1:
            return "break"
      if tkevent.keycode == 114 and tkevent.keysym == "F3":
         if self._executeBinding("VK_F3") == 1:
            return "break"
      if tkevent.keycode == 115 and tkevent.keysym == "F4":
         if self._executeBinding("VK_F4") == 1:
            return "break"
      if tkevent.keycode == 116 and tkevent.keysym == "F5":
         if self._executeBinding("VK_F5") == 1:
            return "break"
      if tkevent.keycode == 117 and tkevent.keysym == "F6":
         if self._executeBinding("VK_F6") == 1:
            return "break"
      if tkevent.keycode == 118 and tkevent.keysym == "F7":
         if self._executeBinding("VK_F7") == 1:
            return "break"
      if tkevent.keycode == 119 and tkevent.keysym == "F8":
         if self._executeBinding("VK_F8") == 1:
            return "break"
      if tkevent.keycode == 120 and tkevent.keysym == "F9":
         if self._executeBinding("VK_F9") == 1:
            return "break"
      if tkevent.keycode == 121 and tkevent.keysym == "F10":
         if self._executeBinding("VK_F10") == 1:
            return "break"
      if tkevent.keycode == 122 and tkevent.keysym == "F11":
         if self._executeBinding("VK_F11") == 1:
            return "break"
      if tkevent.keycode == 123 and tkevent.keysym == "F12":
         if self._executeBinding("VK_F12") == 1:
            return "break"

      """
VK_F2 to VK_F12   - done
VK_NUMPAD0 to VK_NUMPAD9  
VK_MULTIPLY  
VK_ADD  
VK_SUBTRACT  
VK_DECIMAL  
VK_DIVIDE  
VK_NUMLOCK  
VK_SCROLL  
      """

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
      self.insert(INSERT, '\t')
        
   def callPrior(self, tkevent):
      """ Handles the <KeyPress-Prior> event."""
      self._partk.pageUp()
        
   def callNext(self, tkevent):
      """ Handles the <KeyPress-Next> event."""
      self._partk.pageDown()
        
   def callEsc(self, tkevent):
      """ Handles the <KeyPress-Escape> event."""
      self._partk.escape()
    
   def callKillLine(self, tkevent): 
      """ Handles the <Control-KeyPress-u> event."""
      self.delete(0,'end')

   def callPushInputStack(self, tkevent):
      """ Handles the <Control-KeyPress-Up> event."""
      self.inputstack.append((self.index('insert'),self.get()))
      self.delete(0,'end')

   def callPopInputStack(self,tkevent):
      """ Handles the <Control-KeyPress-Down> event."""
      if len(self.inputstack) < 1:
         return
      poppage = self.inputstack.pop()
      self.delete(0,'end')
      self.insert(0,poppage[1])
      self.icursor(poppage[0])
        
   def insertPrevCommand(self, tkevent):
      """ Handles the <KeyPress-Up> event."""
      hist = self.inputstack
      if self.hist_index == -1:
         self.current_input = self.get()
      if self.hist_index < len(hist) - 1:
         self.hist_index = self.hist_index + 1
         self.delete(0, 'end')
         self.insert(0, hist[self.hist_index][:])

   def insertNextCommand(self, tkevent):
      """ Handles the <KeyPress-Down> event."""
      hist = self.inputstack
      if self.hist_index == -1:
         return
      self.hist_index = self.hist_index - 1
      if self.hist_index == -1:
         self.delete(0, 'end')
         self.insert(0, self.current_input)
            
      else:
         self.delete(0, 'end')
         self.insert(0, hist[self.hist_index][:])
