#!/usr/local/bin/python1.4

####
## The general style of the functions in this file is like the
## following and is different from the former style to improve
## readability and everyone's ability to not need a reference
## as much.  As it is, it would be a problem for Scrollback
## and ScrollBack... is it two words and even if it's one,
## does it deserve two caps?  Quite the dilemna, I know.  I
## would be up all night trying to decide so instead, the new
## standard is word_word_word() and no caps.  The old
## functions will be supported for a time but seeing that they
## did not follow a standard anyway, I picked from the two
## choices the one which I believed the most programmer
## friendly.  -- James

####
## import what you need here :)
## from Tkinter import *
## import tkhistentry, string, mud, sys, os, font, regex, data

####
## these could be useful but are X specific
## txtAttribs = { } ## 0 -- all off. 1 -- bold  5 -- blinking
##                 ## 7 -- reverse 8 hidden

## fgColorCodes = { "30": "black", "31": "red", "32": "green",
##                  "33": "yellow", "34": "blue", "35": "magenta",
##                  "36": "cyan", "37": "white"}

## bgColorCodes = { "40": "black", "41": "red", "42": "green",
##                  "43": "yellow", "44": "blue", "45": "magenta",
##                  "46": "cyan", "47": "white", "50": "purple" }

class Gui:
    def __init__(self):
	self.support_hash = {'echo':0}
	self.scrollback_in_use=0
####
## setup the entire display but do not enter a loop or anything yet
## this would include making widgets and setting the title bar
## but would NOT include HANDLING input from the widgets.  That happens
## when the main loop goes.

##         self.viewhistory = 0
##         self.echo = 1
##         self.tk = Tk()
##         self.tk.geometry("800x600")
##         self.tk.title("Lyntin -- The Hacker's Mud Client")
##         self.currcolors = (0, 37, 40)
##         self.regcolors = (0, 37, 40)
##         self.unfinishedcolor = (0, "")
	
        
##         if os.name != 'posix':
##             # require tcl/tk 8.0 on windows
##             fnt = font.Font(font=("Fixedsys", 12))
##             self.entry = tkhistentry.CommandEntry(self.tk, self, 
##                                                 fg='white', bg='black',
##                                                 insertbackground='yellow',
##                                                 font=fnt,
##                                                 insertwidth='2')

##             self.txt = Text(self.tk, {'fg': 'white', 'bg': 'black',
##                                       'state': 'disabled', 'font': fnt,
##                                       'height': 20})
##             self.txtbuffer = Text(self.tk, {'fg': 'white', 'bg': 'black',
##                                       'state': 'disabled', 'font': fnt,
##                                       'height': 20})
##         else:
##             self.entry = tkhistentry.CommandEntry(self.tk, self,
##                                                 fg='white', bg='black',
##                                                 insertbackground='yellow',
##                                                 insertwidth='2')

##             self.txt = Text(self.tk, {'fg': 'white', 'bg': 'black',
##                                       'state': 'disabled',
##                                       'height': 20})
##             self.txtbuffer = Text(self.tk, {'fg': 'white', 
##                                       'bg': 'black', 'state': 'disabled', 
##                                       'height': 20})



##         # set up the scrollbar for the txtbuffer widget
##         self.scrollVertical = Scrollbar(self.tk,orient=VERTICAL)
##         self.txt.configure(yscrollcommand=self.scrollVertical.set)
##         self.scrollVertical.config(command=self.txt.yview)
##         # FIXME changed from LEFT and W
##         self.scrollVertical.pack(side=RIGHT, anchor=E, fill=Y)


##         self.entry.pack({'side': 'bottom', 'fill': 'both'})
##         self.entry.focus_set()

##         self.txt.pack({'side': 'bottom', 'fill': 'both', 'expand': 1})
        
##         self.InitColorTags()

	def supports(self,str):
	    answer=None
	    try:
		answer=self.support_hash[str]
	    except:
		return None
	    return answer

####
## These should all be functions of some sort that are executed by bound keys
## not sure how these sorts of bindings would work but it's necessary that
## there are no hard coded things that will cause problems for future
## expansion

##     def pageUp(self):
##         if self.viewhistory == 0:
##             self.txtbuffer.pack({'after': self.txt, 'side': 'bottom', 
##                                  'fill': 'both', 'expand': 1})
##             self.viewhistory = 1
##             self.txtbuffer.configure(state='normal')
##             self.txtbuffer.delete ("1.0", "end")
##             lotofstuff = self.txt.get ('1.0', 'end')
##             self.txtbuffer.insert ('end', lotofstuff)
##             self.txtbuffer.configure(state='disabled')

##             self.txtbuffer.yview('moveto', '1')
##             if os.name != 'posix':
##                 self.txtbuffer.yview('scroll', '20', 'units')

##             self.txt.yview('moveto', '1')
##             if os.name != 'posix':
##                 self.txt.yview('scroll', '220', 'units')

##         else:
##             # yscroll up stuff
##             self.txtbuffer.yview('scroll', '-15', 'units')

##     def pageDown(self):
##         if self.viewhistory == 1:
##             # yscroll down stuff
##             self.txtbuffer.yview('scroll', '15', 'units')

##     def escape(self):
##         if self.viewhistory == 1:
##             self.txtbuffer.forget()
##             self.viewhistory = 0
##         else:
##             self.entry.clear_input()

    def scrollback_open(self):
	"""scrollback_open(self)->None

	opens the scrollback for the client which is to be maintained
	by the UI because... it's easier that way.  There may be a
	module to handle this for the client which the client may use
	in the future but for now, the way it's done in tkgui is just
	to copy the stuff from the main window into another one and
	display it taking half the screen.  This seems to work well
	and I'm fine with using that method for others until there
	actually is some sort of device separate from the engine but
	also UI independant.
	"""
	self.scrollback_in_use=1
	pass

    def scrollback_backward(self):
	"""scrollback_backward(self)->None

	Scrolls back the scrollback.  If the scrollback is not open
	yet, it should be opened by this.
	"""
	if self.scrollback_in_use==1:
	    #scroll it back here.  not after the else
	    pass
	else:
	    self.scrollback_open()
	return None

    def scrollback_forward(self):
	"""scrollback_forward(self)->None

	Scrolls the scrollback forward if it's open and does nothing
	if it's not.
	"""
	if self.scrollback_in_use==1:
	    #scroll it forward
	    pass
	return None

    def scrollback_close(self):
	"""ScrollbackClose(self)->None

	Closes scrollback.
	"""
	return None

    def mainloop(self):
#        self.tk.after(100, self.iterate)
#        self.tk.mainloop()
        
#    def iterate(self):
#        if not self.app.Loop():
#            self.tk.quit()
#        self.tk.after(50, self.iterate)

    def Prompt(self): 
	"""Prompt(self) -> None
	
	Sets a prompt for the user.
	"""
	pass
#	self.txt.insert('end', "\n")

    def has_echo(self):
	"""has_echo(self) -> true/false

	Returns if the client has the ability to turn on and off echoing
	for passwords and other stuff (the telnet echo option, mainly)
	"""
        return self.supports['echo'] #default is 0 because... this UI doesn't even have a display
    
    def echo_on(self,yesno):
	if yesno:
	    self.OnEcho()
	else:
	    self.OffEcho()
	
    # turn on echo
    def OnEcho(self):
	"""OnEcho(self) -> None

	Turn on echo
	"""
	pass
##        self.echo = 1
##        self.entry.configure(show='')
    
    # turn off echo
    def OffEcho(self):
	"""OffEcho(self) -> None

	Turn off echo
	"""
	pass
##        self.echo = 0
##        self.entry.configure(show='*')


    def close(self): #SFN This function name is more in the python style.
	self.CloseUI()

    def CloseUI(self):
	"""CloseUI(self) -> None

	FIXME
	"""
        pass

    def print_string(self,line,modifiers=None,ending='\n'):
	"""print_string(self,line)->None

	Print a string to the UI after processing for escapes such
	as ANSI colors.  The variable 'ending' can be set to '' to
	accomodate a line which already has a proper ending and
	modifiers can be any of a set of options which will be set
	in the future.  For now, use the strings 'client' or 'user'
	to variate from the default behavior of absolutely nothing.
	When a modifier is used, there will be an option for having
	it change what the current modifiers in the UI are or not
	or if it should simply be used temporarily to facilitate
	strings sent from the client which need special processing
	but should not have an effect on the text from the session.
	The current idea is to have a few predefined standards and
	then to use something like ansi:31;45 for that ANSI color
	option.  Options will be split on comma to make things
	simple (yeah, that's still a main point even though this
	is somewhat involved.)  This is believed (by me, James) to
	be the most all around useful solution.  This
	documentation will obviously need to be trimmed before the
	release because it will be wrong then.
	"""
	pass #because this isn't real

    def Putline(self, line):
        """PutLine(self, line) -> None
        
        Prints a message from the client to the player
        changing the background color to magenta.
        """
	self.Print(line,'client')
##        if line:
##            self.txt.configure(state='normal')
##            self.txt.insert('end', line, "50")
##            self.txt.insert('end', "\n")
##            self.txt.configure(state='disabled')
##
##            self.txt.yview('moveto', '1')
##            if os.name != 'posix':
##                self.txt.yview('scroll', '20', 'units')


    def PutUserInput(self, line):
        """PutUserInput(self, line) -> None

        Prints the user input to the screen with a blue background
        color and a white foreground color.  Lets you immediately
        discern what's input vs. what's output.
        """
	self.Print(line,'user')
##        if line:
##            # FIXME?
##            line = line[:-1]
##            self.txt.configure(state='normal')
##            self.txt.insert('end', line, "44")
##            self.txt.insert('end', "\n")
##            self.txt.configure(state='disabled')

##            self.txt.yview('moveto', '1')
##            if os.name != 'posix':
##                self.txt.yview('scroll', '20', 'units')


    def PutUntouchedLine(self, line):
	"""PutUntouchedLine(self, line) -> None

	Prints a line for the user after adding a newline to the end of it
	"""
##        if line:
##            self.PutReallyUntouchedLine(line)
##            self.PutReallyUntouchedLine('\n')
	self.Print(line)

    def PutReallyUntouchedLine(self, line):
	"""PutReallyUntouchedLine(self, line) -> None

	Prints a line for the user without any preprocessing
	"""
	self.Print(line,ending='')
##         if line:
##             mud.log('really untouched ' + line)
##             mud.log('last char: ' + line[-1])
##             mud.log("\nlast %d\n"%ord(line[-1]))
##             mud.log("\nfirst %d\n"%ord(line[0]))

##             index = 0
##             start = 0
##             end = 0

##             if self.unfinishedcolor[0] == 1:
##                 cstart = index
##                 while index < len(line) and line[index] != "m":
##                     index = index + 1

##                 self.unfinishedcolor = (self.unfinishedcolor[0], self.unfinishedcolor[1] + line[cstart:index])
##                 if index < len(line):
##                     self.colorchange(self.unfinishedcolor[1]) 
##                     self.unfinishedcolor = (0, "")
##                 else:
##                     self.unfinishedcolor = (1, self.unfinishedcolor[1] + line[cstart:index - 1])
                
##                 start = index + 1

##             while index < len(line):
##                 if line[index] == chr(27):
##                     cstart = index
##                     end = index

##                     self.txt.configure(state='normal')
##                     if self.currcolors == self.regcolors:
##                         self.txt.insert('end', line[start:end])
##                     else:
##                         self.txt.insert('end', line[start:end], self.currcolors[1])
##                     self.txt.configure(state='disabled')

##                     while index < len(line) and line[index] != "m":
##                         index = index + 1

##                     if index == len(line):
##                         # if line[index] != "m":
##                         self.unfinishedcolor = (1, line[cstart:index])
##                     else:   
##                         self.colorchange(line[cstart:index])
##                         # index = index + 1

##                     start = index + 1

##                 index = index + 1 


##             end = index
##             self.txt.configure(state='normal')
##             if self.currcolors == self.regcolors:
##                 self.txt.insert('end', line[start:end])
##             else:
##                 self.txt.insert('end', line[start:end], self.currcolors[1])
##             self.txt.configure(state='disabled')


##             self.txt.yview('moveto', '1')
##             if os.name != 'posix':
##                 self.txt.yview('scroll', '20', 'units')

##             self.ClipText()

    ##
    ## takes in a string, and parses it into a series of numbers, then
    ## sets the current colors accordingly
    ##
##    def colorchange(self, txt):
##         if txt[0] == chr(27):
##         # if txt[0] == chr(27) and txt[len(txt)-1] == "m":
##             newcolor = txt[2:(len(txt))]

##             if newcolor == "0":
##                 self.currcolors = self.regcolors
##             else:
##                 numbers = string.split(newcolor, ";")
##                 for num in numbers:
##                     if fgColorCodes.has_key(num):
##                         self.currcolors = (self.currcolors[0], int(num), self.currcolors[2])
##                     if bgColorCodes.has_key(num):
##                         self.currcolors = (self.currcolors[0], self.currcolors[1], int(num))
##                     if txtAttribs.has_key(num):
##                         self.currcolors = (int(num), self.currcolors[1], self.currcolors[2])


             
##     ##
##     ## set up Tk tags for the text widget (fg/bg)
##     ##
##     def InitColorTags(self):
##         codes = fgColorCodes
##         colorKeys = codes.keys()
##         for ck in colorKeys:
##             self.txt.tag_config(ck, foreground=codes[ck])

##         codes = bgColorCodes
##         colorKeys = codes.keys()
##         for ck in colorKeys:
##             self.txt.tag_config(ck, background=codes[ck])

    def get_input(self):
	return None


    # check for stuff from input
    def GetUserInput(self):
    """GetUserInput(self)->string

    returns the user input once enter has been hit and None otherwise
    """
	return self.get_input
##         if self.entry.input:
##             retval = self.entry.input[0]
##             del self.entry.input[0]
##             if retval == '\n':
##                 self.PutUserInput(retval)
##                 # self.PutReallyUntouchedLine('\n')
##             else:
##                 if self.echo:
##                     self.PutUserInput(retval)
##                     # self.PutUntouchedLine(retval[:-1])
##             return retval
                
##     def ClipText(self):
##         temp = self.txt.index("end")
##         ind = string.find(temp, ".")
##         temp = temp[:ind]
##         if (string.atoi(temp) > 800):
##             self.txt.config(state=NORMAL)
##             self.txt.delete ("1.0", "100.end")
##             self.txt.config(state=DISABLED)

if __name__ == '__main__':
    Gui()
