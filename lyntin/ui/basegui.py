#!/usr/local/bin/python1.4

"""
The general style of the functions in this file is like the
following and is different from the former style to improve
readability and everyone's ability to not need a reference
as much.  As it is, it would be a problem for Scrollback
and ScrollBack... is it two words and even if it's one,
does it deserve two caps?  Quite the dilemna, I know.  I
would be up all night trying to decide so instead, the new
standard is word_word_word() and no caps.  The old
functions will be supported for a time but seeing that they
did not follow a standard anyway, I picked from the two
choices the one which I believed the most programmer
friendly.  -- James
"""

class BaseGUI:
    def __init__(self):
        self.support_hash = {'echo':0}
        self.status_hash={'echo':1,'scollback':0}
        self.setup()

    def setup(self):
        """
        setup the entire display but do not enter a loop or anything yet
        this would include making widgets and setting the title bar
        but would NOT include HANDLING input from the widgets.  That happens
        when the main loop goes.
        """
        pass


    def supports(self,str):
        answer=None
        try:
            answer=self.support_hash[str]
        except:
            return None
        return answer

    def status(self,var,*arg):
        if len(arg) == 1:
            self.status_hash[var]=arg[0]
        else:
            try:
                return self.status_hash[var]
            except:
                return None

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
        self.status('scrollback',1)
        pass

    def scrollback_backward(self):
        """scrollback_backward(self)->None

        Scrolls back the scrollback.  If the scrollback is not open
        yet, it should be opened by this.
        """
        if self.status('scrollback')==1:
            scrollback_scroll('back')
            pass
        else:
            self.scrollback_open()
        return None

    def scrollback_forward(self):
        """scrollback_forward(self)->None

        Scrolls the scrollback forward if it's open and does nothing
        if it's not.
        """
        if self.status('scrollback')==1:
            self.scrollback_scroll('forward')
            pass
        return None

    def scrollback_scroll(self,direction='back'):
        """scroll_forward(self,direction='back')->None

        Actually does the scrolling.  Override me.
        """
        return None

    def scrollback_close(self):
        """ScrollbackClose(self)->None

        Closes scrollback.
        """
        self.status('scrollback',0)
        return None

    def mainloop(self):
        """mainloop(self)->None
        
        """
        while 1:
            try:
                if not self.app.Loop():
                    return
            except SystemExit:
                return

    def Prompt(self):
        self.prompt()

    def prompt(self): 
        """prompt(self) -> None
        
        Sets a prompt for the user.
        """
        pass

    def has_echo(self):
        """has_echo(self) -> true/false

        Returns if the client has the ability to turn on and off echoing
        for passwords and other stuff (the telnet echo option, mainly)
        """
        return self.supports('echo')

    def WarnNoEcho(self):
        self.warn_no_echo()

    def warn_no_echo(self):
        pass
    
    def echo(self,yesno):
        """echo(self,yesno)->None

        turns echo on or off depending on if the argument is true or false.
        """
        if yesno:
            self.status('echo',1)
        else:
            self.status('echo',0)

    def OnEcho(self):
        """OnEcho(self) -> None

        Turn on echo
        """
        self.echo(1)
    
    def OffEcho(self):
        """OffEcho(self) -> None

        Turn off echo
        """
        self.echo(0)


    def close(self):
        """close(self) -> None

        override me!
        """
        pass


    def CloseUI(self):
        self.close()

    def print_string(self,line,modifiers=None,ending='\n',target=None):
        """print_string(self,line,modifiers=None,ending='\n',window=None)->None

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

        9/29/00
        Added the target argument to be sure that expansion is easily
        possible when it is desired.  The target will be any output
        method but most likely a window (such as the main window...)
        and, once phased in, None will refer to the default window for
        the UI class while other arguments will refer to a specific
        target class of some sort with a print_string method which can
        be used exactly like this one (yeehaw!) to enable multiple
        windows (and possibly logs) to be used for certain output in
        all GUIs.  What a mouthful!  -- James
        """
        pass #because this isn't real

    def Putline(self, line):
        """PutLine(self, line) -> None
        
        Prints a message from the client to the player
        changing the background color to magenta.
        """
        self.print_string(line,modifiers='client')

    def PutUserInput(self, line):
        """PutUserInput(self, line) -> None

        Prints the user input to the screen with a blue background
        color and a white foreground color.  Lets you immediately
        discern what's input vs. what's output.
        """
        self.print_string(line,modifiers='user')

    def PutUntouchedLine(self, line):
        """PutUntouchedLine(self, line) -> None

        Prints a line for the user after adding a newline to the end of it
        """
        self.print_string(line)

    def PutReallyUntouchedLine(self, line):
        """PutReallyUntouchedLine(self, line) -> None

        Prints a line for the user without any preprocessing or trailing
        newline
        """
        self.print_string(line,ending='')

    def get_input(self):
        return None

    def GetUserInput(self):
        """GetUserInput(self)->string

        returns the user input once enter has been hit and None otherwise
        """
        return self.get_input()

if __name__ == '__main__':
    BaseGUI()
