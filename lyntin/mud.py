##################################################################
# This file is part of Lyntin
# copyright (c) Lyn Headley 1996-1998
#
# Lyntin is distributed under the GNU General Public License.  See
# the file COPYING for details.
#
# module mud
##################################################################
"""
receives output from the connection and calls functions to
interpret and display the output
"""


import regsub, string, regex, sys
import data, player

"""telnet protocol constants"""
IAC  = chr(255) # Interpret '\377' as command
DONT = chr(254) # '\376'
DO   = chr(253) # '\375'
WONT = chr(252) # '\374'
WILL = chr(251) # '\373'


def handle_mud_output(output, ses):
    """handle_mud_output(output, ses) -> None

    See if anything from the mud triggered an action/gag/sub
    if so, handle it.  Then display stuff from the mud to the user.
    """
    if not output:
        return
    if not string.split(output):
        return # just whitespace

    #log(output)

    #import pdb; pdb.set_trace()
    # I st... er 'adopted' this code from 'telnet.py', which comes with
    # the python distribution.
    iac = 0     # Interpret next char as command
    opt = ''    # Interpret next char as option
    # stuff each character in here -- a significant optimization
    charlist = [] 
    for c in output:
	# First, we turn echo on by default
	echo_on()
        # see if we're negotiating an option
        if opt:
            if opt == WILL:
                if c == '\001':
                    echo_off()
            elif opt == WONT:
                if c == '\001':
                    echo_on()
            # we don't take orders
            # FIXME
            elif opt == DO:
                data.currsession.WriteTo(IAC + WONT + c)
                # data.theapp.SendPlainInput(IAC + WONT + c)
            elif opt == DONT:
                data.currsession.WriteTo(IAC + WONT + c)
                # data.theapp.SendPlainInput(IAC + WONT + c)
            opt = ''
            iac = 0

        elif iac:
            iac = 0
            if c in (DO, DONT, WILL, WONT):
                opt = c
            else:
                charlist.append(c)

        elif c == IAC:
            iac = 1
        else:
            charlist.append(c)

    cleandata = string.join(charlist, '')
    if cleandata:
        oldcleandata = cleandata

        # get rid of Ansi crap (so colored stuff will still trigger actions)
        oldcleandata = data.filter_cm(oldcleandata)
        cleandata = data.filter_crud(cleandata)
        ses.log(cleandata)
        if ses.CheckForGaggedText(cleandata):
            # whoa, this text is special; it's been gagged.
            # this is handled by splitting the text into lines, then
            # removing the line with the offending text
            gl = data.split_into_lines(oldcleandata)
            rebuild = []
            joinednewline = ""
            for line in gl:
                if ses.CheckForGaggedText(line):
                    index = 0
                    flag = 0    # 0 if non-ansi; 1 if ansi
                    newline = []
                    while index < len(line):
                        if (flag == 0 and line[index] == chr(27)):
                            newline.append(line[index])
                            flag = 1 
                        elif (flag == 1 and line[index] == "m"):
                            newline.append(line[index])
                            flag = 0
                        elif (flag == 1):
                            newline.append(line[index])
                        index = index + 1 
                    joinednewline = string.joinfields(newline, "")
                else:
                    if (len(joinednewline) > 0):
                        rebuild = rebuild + [joinednewline + line]
                        joinednewline = ""
                    else:
                        rebuild = rebuild + [line]
            oldcleandata = string.joinfields(rebuild, '\n')

        # handle substitutes
        for sub in ses.subs.keys():
            if regex.search(sub, cleandata) != -1:
                oldcleandata = regsub.gsub(sub, ses.subs[sub], oldcleandata)

        # handle reports
        for (file, text) in ses.reports:
            if regex.search(text, cleandata) != -1:
                file.write(cleandata)
                file.write('\n\n')

        # display the text if this is the current session
        if ses is data.currsession and ses.connected:
            log(oldcleandata)
            player.PutRaw(oldcleandata)

        # add output to the session's databuffer
        ses.databuf.add(cleandata)

        # Handle actions
        oldses = data.currsession
        data.currsession = ses
        ses.CheckActions(cleandata)
        data.currsession = oldses


def log(str):
    """log(str) -> None

    Logs data to the mudlog
    """
    if(data.debug > 0 and data.logfile):
        # data.logfile.write("*** Logging ***\n")
        data.logfile.writelines( [str, "\n"] )
        if(data.debug > 5 and data.logfile):
            for c in str:
                data.logfile.write('(%d) %s' % (ord(c), c))
                # data.logfile.write('%s(%d)'%(c, ord(c)))
        data.logfile.flush()
        

def echo_on():
    """echo_on() -> None

    Alerts the ui to turn on echo.
    """
    data.theapp.ui.OnEcho()
    
def echo_off():
    """echo_off() -> None

    Alerts the ui to shut off echo.
    """
    data.theapp.ui.OffEcho()
