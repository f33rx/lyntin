#!/usr/bin/python
"""
The main script that figures out the args, and instantiates everything.
"""
# -*-python-*-

#
# the lyntin agent framework
#

##################################################################
# do these imports now to minimize perceived startup time
import socket, select, sys, regex, time
import os, regsub, string, types, traceback

if os.name != 'posix':
    os.environ['LYNTINDIR'] = os.getcwd() + os.sep

##################################################################
# Start Lyntin
##################################################################


def setPath():
    ltd = os.environ.get('LYNTINDIR')
    if ltd:
        if ltd[-1] != os.sep:
            ltd = ltd + os.sep
    else:
        InstallError()

    sys.path.append(ltd)
    sys.path.append(ltd + 'ui')

def InstallError():
    print '\nLyntin was not installed correctly'
    print 'please check that your LYNTINDIR is correctly set'
    print 'try to reinstall Lyntin before sending a bug report'
    sys.exit(1)
    
def InternalError():
    print '\n\n\n\n\nInternal Error'
    print '=============='
    import traceback
    traceback.print_exc()
    print '\n\nPlease submit a bug report describing the circumstances ' +\
          'including the traceback above to:'
    print 'mouse@varium.com'
    sys.exit(1)
    
def main():
    setPath()
    import app
    app.Run()

if __name__ == '__main__':
    try:
	main()
    except ImportError:
        InstallError()
    except SystemExit:
        pass
    except KeyboardInterrupt:
        pass
    except:
        InternalError()
