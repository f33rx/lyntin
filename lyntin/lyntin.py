#!/usr/local/bin/python
"""
The main script that figures out the args, and instantiates everything.
"""
# -*-python-*-

#
# the lyntin agent framework
#

##################################################################
# do these imports now to minimize perceived startup time
import socket, select, sys, re, time
import os, string, types, traceback

if os.name != 'posix':
    os.environ['LYNTINDIR'] = os.getcwd() + os.sep

##################################################################
# Start Lyntin
##################################################################


def InstallError():
    ltd = os.environ.get('LYNTINDIR')
    print '\nLyntin was not installed correctly'
    if ltd:
        print 'please check that your LYNTINDIR is correctly set'
        print 'its current value is:', ltd
    else:
        print 'your LYNTINDIR is not set'

    print 'remember that some shells require an "export LYNTINDIR"\n'
    sys.exit(1)
    
def InternalError():
    print '\n\n\n\n\nInternal Error'
    print '=============='
    import traceback
    traceback.print_exc()
    print '\n\nPlease submit a bug report describing the circumstances ' +\
          'including the traceback at http://lyntin.sourceforget.net/'
    sys.exit(1)
    
def main():
    ltd = os.environ.get('LYNTINDIR')
    if ltd:
        if ltd[-1] != os.sep:
            ltd = ltd + os.sep
    else:
        InstallError()

    sys.path.append(ltd)
    sys.path.append(ltd + 'ui')
    sys.path.append(ltd + 'libcore')

    import app
    app.set_path(ltd)
    app.run()

debugging = 0
if __name__ == '__main__':
    if debugging:
        main()
    else:
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
