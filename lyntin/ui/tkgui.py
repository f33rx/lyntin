##################################################################
# This file is part of Lyntin
# copyright (c) Lyn Headley 1996-2001
#
# Lyntin is distributed under the GNU General Public License.  See
# the file LICENSE in the distribution for details.
# $Id$
##################################################################

"""
Tkgui is a gui interface based on tk.
"""

from Tkinter import *

import tkhistentry, string, mud, sys, os, font, data
from tkgui import *
from basegui import BaseGUI
from exported import lyntin_add_command
from exported import lyntin_command

txtAttribs = { } ## 0 -- all off. 1 -- bold  5 -- blinking
   ## 7 -- reverse 8 hidden

txtAttribs = { "0": "off", "1": "bold" }

fgColorCodes = {
                "30": "#000000",
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

winfont = ("Fixedsys", 12)
posixfont = ("Fixedsys", 12)

# fgColorCodes = { "30": "black", "31": "red", "32": "green",
#                  "33": "yellow", "34": "blue", "35": "magenta",
#                  "36": "cyan", "37": "white"}

bgColorCodes = { "40": "black", "41": "red", "42": "#004411",
                 "43": "yellow", "44": "blue", "45": "magenta",
                 "46": "cyan", "47": "white", "50": "purple" }

def addaliases(words, input, seslist):
    """adds a bunch of aliases to the current session"""
    lyntin_command("#alias tk_kb_num_1 sw")
    lyntin_command("#alias tk_kb_num_2 s")
    lyntin_command("#alias tk_kb_num_3 se")
    lyntin_command("#alias tk_kb_num_4 w")
    lyntin_command("#alias tk_kb_num_6 e")
    lyntin_command("#alias tk_kb_num_7 nw")
    lyntin_command("#alias tk_kb_num_8 n")
    lyntin_command("#alias tk_kb_num_9 ne")

class TkGui(BaseGUI):

   """override function"""
   def setup(self):
      self.viewhistory = 0
      self.do_i_echo = 1
      self.support_hash['echo'] = 1
      self.tk = Tk()
      self.tk.geometry("800x600")
      self.tk.title("Lyntin -- The Hacker's Mud Client")
      self.currcolors = (0, 37, 40)
      self.regcolors = (0, 37, 40)
      self.unfinishedcolor = (0, "")


      # i wrote this because i was sick and tired of re-binding
      # all those aliases
      lyntin_add_command("tkaddaliases", addaliases)

      if os.name != 'posix':
         # require tcl/tk 8.0 on windows
         fnt = font.Font(font=winfont)
         self.entry = tkhistentry.CommandEntry(self.tk, self, 
                                             fg='white', bg='black',
                                             insertbackground='yellow',
                                             font=fnt,
                                             insertwidth='2')

         self.txt = Text(self.tk, {'fg': 'white', 'bg': 'black',
                                   'state': 'disabled', 'font': fnt,
                                   'height': 20})
         self.txtbuffer = Text(self.tk, {'fg': 'white', 'bg': 'black',
                                   'state': 'disabled', 'font': fnt,
                                   'height': 20})
      else:
         self.entry = tkhistentry.CommandEntry(self.tk, self,
                                               fg='white', bg='black',
                                               insertbackground='yellow',
                                               font=font.Font(font=posixfont),
                                               insertwidth='2')

         self.txt = Text(self.tk, {'fg': 'white', 'bg': 'black',
                                   'state': 'disabled',
                                   'font': font.Font(font=posixfont),
                                   'height': 20})
         self.txtbuffer = Text(self.tk, {'fg': 'white', 
                                   'bg': 'black', 'state': 'disabled', 
                                   'height': 20})



      # set up the scrollbar for the txtbuffer widget
      self.scrollVertical = Scrollbar(self.tk,orient=VERTICAL)
      self.txt.configure(yscrollcommand=self.scrollVertical.set)
      self.scrollVertical.config(command=self.txt.yview)
      self.scrollVertical.pack(side=RIGHT, anchor=E, fill=Y)

      self.entry.pack({'side': 'bottom', 'fill': 'both'})
      self.entry.focus_set()

      self.txt.pack({'side': 'bottom', 'fill': 'both', 'expand': 1})

      self.InitColorTags()

   """overriden function"""
   def beep(self):
      self.PutMessage("BEEP!")

   """overriden function--though it might never be called"""
   def scrollback_scroll(self, direction='back'):
      if direction=='back':
         self.pageUp()
      else:
         self.pageDown()

   def pageUp(self):
      if self.viewhistory == 0:
         self.txtbuffer.pack({'after': self.txt, 'side': 'bottom', 
                              'fill': 'both', 'expand': 1})
         self.viewhistory = 1
         self.txtbuffer.configure(state='normal')
         self.txtbuffer.delete ("1.0", "end")
         lotofstuff = self.txt.get ('1.0', 'end')
         self.txtbuffer.insert ('end', lotofstuff)
         for t in self.txt.tag_names():
            taux=None
            tst=0
            for e in self.txt.tag_ranges(t):
               if tst==0:
                  taux=e
                  tst=1
               else:
                  tst=0
                  self.txtbuffer.tag_add(t,str(taux),str(e))
         self.txtbuffer.configure(state='disabled')

         self.txtbuffer.yview('moveto', '1')
         if os.name != 'posix':
            self.txtbuffer.yview('scroll', '20', 'units')
         self.tk.update_idletasks()
         self.txt.yview('moveto','1.0')
         if os.name != 'posix':
            self.txt.yview('scroll', '220', 'units')

      else:
         # yscroll up stuff
         self.txtbuffer.yview('scroll', '-15', 'units')

   def pageDown(self):
      if self.viewhistory == 1:
         # yscroll down stuff
         self.txtbuffer.yview('scroll', '15', 'units')

   def escape(self):
      if self.viewhistory == 1:
         self.txtbuffer.forget()
         self.viewhistory = 0
      else:
         self.entry.clear_input()

   def mainloop(self):
      self.tk.after(100, self.iterate)
      self.tk.mainloop()

   def iterate(self):
      if not self.app.Loop():
         self.tk.quit()
      self.tk.after(50, self.iterate)


   def prompt(self): 
      self.txt.insert('end', "\n")

   def has_echo(self):
      return 1

   """overridden function"""
   def echo(self, yesno):
      if yesno==1:
         self.do_i_echo = 1
         self.entry.configure(show='')
      else:
         self.do_i_echo = 0
         self.entry.configure(show='*')


   """overridden function"""
   def print_string(self, line, modifiers=None, ending='\n', target=None):

      if modifiers=='error':
         if line:
            self.txt.configure(state='normal')
            self.txt.insert('end', line, "44")
            self.txt.insert('end', "\n")
            self.txt.configure(state='disabled')

            self.txt.yview('moveto', '1')
            if os.name != 'posix':
               self.txt.yview('scroll', '20', 'units')

      elif modifiers=='client':
         if line:
            self.txt.configure(state='normal')
            # self.txt.insert('end', line, "42")
            line = "# " + string.replace(line, "\n", "\n# ")
            self.txt.insert('end', line)
            self.txt.insert('end', "\n")
            self.txt.configure(state='disabled')

            self.txt.yview('moveto', '1')
            if os.name != 'posix':
               self.txt.yview('scroll', '20', 'units')

      elif modifiers=='user':
         if line:
            # FIXME?
            line = line[:-1]
            self.txt.configure(state='normal')
            self.txt.insert('end', line, "44")
            self.txt.insert('end', "\n")
            self.txt.configure(state='disabled')

            self.txt.yview('moveto', '1')
            if os.name != 'posix':
               self.txt.yview('scroll', '20', 'units')

      else:
         if line:
            index = 0
            start = 0
            end = 0

            if self.unfinishedcolor[0] == 1:
               cstart = index
               while index < len(line) and line[index] != "m":
                  index = index + 1

               self.unfinishedcolor = (self.unfinishedcolor[0], self.unfinishedcolor[1] + line[cstart:index])
               if index < len(line):
                  self.colorchange(self.unfinishedcolor[1]) 
                  self.unfinishedcolor = (0, "")
               else:
                  self.unfinishedcolor = (1, self.unfinishedcolor[1] + line[cstart:index - 1])

               start = index + 1

            self.txt.configure(state='normal')
            while index < len(line):
               if line[index] == chr(27):
                  cstart = index
                  end = index

                  if self.currcolors == self.regcolors:
                     self.txt.insert('end', line[start:end])
                  else:
                     self.txt.insert('end', line[start:end], self.currcolors[1])

                  while index < len(line) and line[index] != "m":
                     index = index + 1

                  if index == len(line):
                     self.unfinishedcolor = (1, line[cstart:index])
                  else:   
                     self.colorchange(line[cstart:index])

                  start = index + 1

               index = index + 1 

            end = index

            if self.currcolors == self.regcolors:
               self.txt.insert('end', line[start:end])
            else:
               self.txt.insert('end', line[start:end], self.currcolors[1])
            self.txt.configure(state='disabled')


            self.txt.yview('moveto', '1')
            if os.name != 'posix':
               self.txt.yview('scroll', '20', 'units')

            self.ClipText()

      if ending:
         self.txt.insert('end', ending)


   def colorchange(self, txt):
      """colorchange(self, txt) -> None

      Takes in a string and parses it into a series of numbers,
      then sets the current colors accordingly.
      """
      if txt[0] == chr(27):
      # if txt[0] == chr(27) and txt[len(txt)-1] == "m":
         newcolor = txt[2:(len(txt))]
         # if newcolor == "0":
         if newcolor == "0" or newcolor == "":
            self.currcolors = self.regcolors
         else:
            numbers = string.split(newcolor, ";")
            for num in numbers:
               if fgColorCodes.has_key(num):
                  self.currcolors = (self.currcolors[0], int(num), self.currcolors[2])
               if bgColorCodes.has_key(num):
                  self.currcolors = (self.currcolors[0], self.currcolors[1], int(num))
               if txtAttribs.has_key(num):
                  self.currcolors = (int(num), self.currcolors[1], self.currcolors[2])
                  if num == "0":
                     self.currcolors = self.regcolors

            self.currcolors = (self.currcolors[0], self.currcolors[1] % 2000, self.currcolors[2])
            if self.currcolors[0] == 1:
               self.currcolors = (self.currcolors[0], self.currcolors[1] + 2000, self.currcolors[2])

   def InitColorTags(self):
      """InitColorTags(self) -> None

      Sets up Tk tags for the text widget (fg/bg)
      """
      codes = fgColorCodes
      colorKeys = codes.keys()
      for ck in colorKeys:
         self.txt.tag_config(ck, foreground=codes[ck])
         self.txtbuffer.tag_config(ck, foreground=codes[ck])

      codes = bgColorCodes
      colorKeys = codes.keys()
      for ck in colorKeys:
         self.txt.tag_config(ck, background=codes[ck])
         self.txtbuffer.tag_config(ck, background=codes[ck])


   """overriden function"""
   def get_input(self):
      if self.entry.input:
         retval = self.entry.input[0]
         del self.entry.input[0]
         if retval == '\n':
            self.PutUserInput(retval)
         else:
            if self.do_i_echo:
               self.PutUserInput(retval)
         return retval


   def ClipText(self):
      temp = self.txt.index("end")
      ind = string.find(temp, ".")
      temp = temp[:ind]
      if (string.atoi(temp) > 800):
         self.txt.config(state=NORMAL)
         self.txt.delete ("1.0", "100.end")
         self.txt.config(state=DISABLED)


# Local variables:
# mode:python
# py-indent-offset:3
# tab-width:3
# End:
