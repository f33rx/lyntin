##################################################################
# This file is part of Lyntin
# copyright (c) Lyn Headley 1996-2001
#
# Lyntin is distributed under the GNU General Public License.  See
# the file LICENSE in the distribution for details.
# $Id$
##################################################################

"""
a Tk entry which handles a history list of commands
"""

from Tkinter import *

import os, exported, string

class CommandEntry(Entry):
    def __init__(self, master, partk, **kw):
        apply(Entry.__init__, (self, master), kw)

        self.bind("<KeyPress-Return>", self.store_input)
        self.bind("<KeyPress-Up>", self.InsertPrevCommand)
        self.bind("<KeyPress-Down>", self.InsertNextCommand)
        self.unbind("<KeyPress-Tab>")
        self.bind("<KeyPress-Tab>", self.insertTab)
        self.bind("<KeyPress-Prior>", self.callPrior)
        self.bind("<KeyPress-Next>", self.callNext)
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

            try: 
                self.bind("<KeyPress-/>", self.callKPSlash)
                self.bind("<KeyPress-*>", self.callKPStar)
                self.bind("<KeyPress-minus>", self.callKPMinus)
                self.bind("<KeyPress-+>", self.callKPPlus)
            except:
                print "Some keys could not be bound."
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
            try: 
                self.bind("<KeyPress-KP_Divide>", self.callKPSlash)
                self.bind("<KeyPress-KP_Multiply>", self.callKPStar)
                self.bind("<KeyPress-KP_Subtract>", self.callKPMinus)
                self.bind("<KeyPress-KP_Add>", self.callKPPlus)
            except:
                print "Some keys could not be bound."

        self.bind("<Control-KeyPress-u>", self.callKillLine)
        self.bind("<Control-KeyPress-Up>", self.callPushInputStack)
        self.bind("<Control-KeyPress-Down>", self.callPopInputStack)
        self.bind("<KeyPress-Escape>", self.callEsc)
        self.input = []
        self.hist_index = -1
        self.partk = partk
        self.inputstack = []
        self.saveinputhighlight = 0 #JA Change this to store the last input in 
                                    #the line but highlight it like zMUD does.
        
    def callKPSlash(self, event):
        if event.keycode == 111 or os.name=='posix':
           self.input.append("tk_kb_num_slash" + '\n')
           self.hist_index = -1
           return "break"

    def callKPStar(self, event):
        if event.keycode == 106 or os.name=='posix':
           self.input.append("tk_kb_num_star" + '\n')
           self.hist_index = -1
           return "break"

    def callKPMinus(self, event):
        if event.keycode == 109 or os.name=='posix':
           self.input.append("tk_kb_num_minus" + '\n')
           self.hist_index = -1
           return "break"


    def callKPPlus(self, event):
        if event.keycode == 107 or os.name=='posix':
           self.input.append("tk_kb_num_plus" + '\n')
           self.hist_index = -1
           return "break"

    def callKP9(self, event):
        if event.keycode == 105 or os.name=='posix':
           self.input.append("tk_kb_num_9" + '\n')
           self.hist_index = -1
           return "break"

    def callKP8(self, event):
        if event.keycode == 104 or os.name=='posix':
           self.input.append("tk_kb_num_8" + '\n')
           self.hist_index = -1
           return "break"

    def callKP7(self, event):
        if event.keycode == 103 or os.name=='posix':
           self.input.append("tk_kb_num_7" + '\n')
           self.hist_index = -1
           return "break"

    def callKP6(self, event):
        if event.keycode == 102 or os.name=='posix':
           self.input.append("tk_kb_num_6" + '\n')
           self.hist_index = -1
           return "break"

    def callKP5(self, event):
        if event.keycode == 101 or os.name=='posix':
           self.input.append("tk_kb_num_5" + '\n')
           self.hist_index = -1
           return "break"

    def callKP4(self, event):
        if event.keycode == 100 or os.name=='posix':
           self.input.append("tk_kb_num_4" + '\n')
           self.hist_index = -1
           return "break"

    def callKP3(self, event):
        if event.keycode == 99 or os.name=='posix':
           self.input.append("tk_kb_num_3" + '\n')
           self.hist_index = -1
           return "break"

    def callKP2(self, event):
        if event.keycode == 98 or os.name=='posix':
           self.input.append("tk_kb_num_2" + '\n')
           self.hist_index = -1
           return "break"

    def callKP1(self, event):
        if event.keycode == 97 or os.name=='posix':
           self.input.append("tk_kb_num_1" + '\n')
           self.hist_index = -1
           return "break"

    def store_input(self, event):
        val = self.get()
        val=string.replace(val,'\n',';')
        if len(val) < 1:
            val = "#cr"
        val = val + '\n'
        self.input.append(val)
        if self.saveinputhighlight == 1:
            self.selection_range(0,'end')
        else:
            self.delete(0, 'end')
        self.hist_index = -1

    def clear_input(self):
        self.delete(0, 'end')
        
    def insertTab(self, event):
        self.insert(INSERT, '\t')
        
    def callPrior(self, event):
        self.partk.pageUp()
        # self.insert(INSERT, 'keypress prior')
        
    def callNext(self, event):
        self.partk.pageDown()
        # self.insert(INSERT, 'keypress next')
        
    def callEsc(self, event):
        self.partk.escape()
        # self.insert(INSERT, 'keypress esc')
    
    def callKillLine(self, event): #JA Kill line with ^U like normal terminals
        self.delete(0,'end')

    def callPushInputStack(self, event):
        self.inputstack.append((self.index('insert'),self.get()))
        self.delete(0,'end')

    def callPopInputStack(self,event):
        if len(self.inputstack) < 1:
            print('no stack, dork')
            return
        poppage = self.inputstack.pop()
        self.delete(0,'end')
        self.insert(0,poppage[1])
        self.icursor(poppage[0])
        
    # go backward in the history list
    def InsertPrevCommand(self, event):
        hist = exported.get_history()
        if self.hist_index == -1:
            self.current_input = self.get()
        if self.hist_index < len(hist) - 1:
            self.hist_index = self.hist_index + 1
            self.delete(0, 'end')
            self.insert(0, hist[self.hist_index][:-1])

    # go forward in the history list
    def InsertNextCommand(self, event):
        hist = exported.get_history()
        if self.hist_index == -1:
            return
        self.hist_index = self.hist_index - 1
        if self.hist_index == -1:
            self.delete(0, 'end')
            self.insert(0, self.current_input)
            
        else:
            self.delete(0, 'end')
            self.insert(0, hist[self.hist_index][:-1])

