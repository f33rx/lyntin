"""
Tkgui is a gui interface based on tk.
"""

from Tkinter import *

import tkhistentry, string, mud, sys, os, font, regex, data

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

# fgColorCodes = { "30": "black", "31": "red", "32": "green",
#                  "33": "yellow", "34": "blue", "35": "magenta",
#                  "36": "cyan", "37": "white"}

bgColorCodes = { "40": "black", "41": "red", "42": "green",
                 "43": "yellow", "44": "blue", "45": "magenta",
                 "46": "cyan", "47": "white", "50": "purple" }

class Gui:
    def __init__(self):
        self.viewhistory = 0
        self.echo = 1
        self.tk = Tk()
        self.tk.geometry("800x600")
        self.tk.title("Lyntin -- The Hacker's Mud Client")
        self.currcolors = (0, 37, 40)
        self.regcolors = (0, 37, 40)
        self.unfinishedcolor = (0, "")
        
        
        if os.name != 'posix':
            # require tcl/tk 8.0 on windows
            fnt = font.Font(font=("Fixedsys", 12))
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
                                                insertwidth='2')

            self.txt = Text(self.tk, {'fg': 'white', 'bg': 'black',
                                      'state': 'disabled',
                                      'height': 20})
            self.txtbuffer = Text(self.tk, {'fg': 'white', 
                                      'bg': 'black', 'state': 'disabled', 
                                      'height': 20})



        # set up the scrollbar for the txtbuffer widget
        self.scrollVertical = Scrollbar(self.tk,orient=VERTICAL)
        self.txt.configure(yscrollcommand=self.scrollVertical.set)
        self.scrollVertical.config(command=self.txt.yview)
        # FIXME changed from LEFT and W
        self.scrollVertical.pack(side=RIGHT, anchor=E, fill=Y)


        self.entry.pack({'side': 'bottom', 'fill': 'both'})
        self.entry.focus_set()

        self.txt.pack({'side': 'bottom', 'fill': 'both', 'expand': 1})
        
        self.InitColorTags()
        
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

    def Prompt(self): self.txt.insert('end', "\n")

    def has_echo(self):
        return 1
    
    # turn on echo
    def OnEcho(self):
        self.echo = 1
        self.entry.configure(show='')
    
    # turn off echo
    def OffEcho(self):
        self.echo = 0
        self.entry.configure(show='*')


    def CloseUI(self):
        pass

    def Putline(self, line):
        """PutLine(self, line) -> None
        
        Prints a message from the client to the player
        changing the background color to magenta.
        """
        if line:
            self.txt.configure(state='normal')
#             self.txt.insert('end', line, "50")
            self.txt.insert('end', '> '+line, "44")
            self.txt.insert('end', "\n")
            self.txt.configure(state='disabled')

            self.txt.yview('moveto', '1')
            if os.name != 'posix':
                self.txt.yview('scroll', '20', 'units')


    def PutUserInput(self, line):
        """PutUserInput(self, line) -> None

        Prints the user input to the screen with a blue background
        color and a white foreground color.  Lets you immediately
        discern what's input vs. what's output.
        """
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


    def PutUntouchedLine(self, line):
        if line:
            self.PutReallyUntouchedLine(line)
            self.PutReallyUntouchedLine('\n')

    def PutReallyUntouchedLine(self, line):
        if line:
            mud.log('really untouched ' + line)
            mud.log('last char: ' + line[-1])
            mud.log("\nlast %d\n"%ord(line[-1]))
            mud.log("\nfirst %d\n"%ord(line[0]))

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

            while index < len(line):
                if line[index] == chr(27):
                    cstart = index
                    end = index

                    self.txt.configure(state='normal')
                    if self.currcolors == self.regcolors:
                        self.txt.insert('end', line[start:end])
                    else:
                        self.txt.insert('end', line[start:end], self.currcolors[1])
                    self.txt.configure(state='disabled')

                    while index < len(line) and line[index] != "m":
                        index = index + 1

                    if index == len(line):
                        # if line[index] != "m":
                        self.unfinishedcolor = (1, line[cstart:index])
                    else:   
                        self.colorchange(line[cstart:index])
                        # index = index + 1

                    start = index + 1

                index = index + 1 


            end = index
            self.txt.configure(state='normal')
            if self.currcolors == self.regcolors:
                self.txt.insert('end', line[start:end])
            else:
                self.txt.insert('end', line[start:end], self.currcolors[1])
            self.txt.configure(state='disabled')


            self.txt.yview('moveto', '1')
            if os.name != 'posix':
                self.txt.yview('scroll', '20', 'units')

            self.ClipText()

    ##
    ## takes in a string, and parses it into a series of numbers, then
    ## sets the current colors accordingly
    ##
    def colorchange(self, txt):
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
             
    ##
    ## set up Tk tags for the text widget (fg/bg)
    ##
    def InitColorTags(self):
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


    # check for stuff from input
    def GetUserInput(self):
        if self.entry.input:
            retval = self.entry.input[0]
            del self.entry.input[0]
            if retval == '\n':
                self.PutUserInput(retval)
                # self.PutReallyUntouchedLine('\n')
            else:
                if self.echo:
                    self.PutUserInput(retval)
                    # self.PutUntouchedLine(retval[:-1])
            return retval
                
    def ClipText(self):
        temp = self.txt.index("end")
        ind = string.find(temp, ".")
        temp = temp[:ind]
        if (string.atoi(temp) > 800):
            self.txt.config(state=NORMAL)
            self.txt.delete ("1.0", "100.end")
            self.txt.config(state=DISABLED)

if __name__ == '__main__':
    Gui()
