##################################################################
# This file is part of Lyntin
# copyright (c) Lyn Headley 1996-2001
#
# Lyntin is distributed under the GNU General Public License.  See
# the file LICENSE in the distribution for details.
# $Id$
##################################################################
"""
a hander intercepts server output at a primitive level and can
respond to it or change the input for the next handler.
"""

(CONTINUE, STOP) = range(2)

import mud

class Handler:
    def handle(self, session, read):
        """
        return (continue, read) where continue is either STOP
        or CONTINUE and read is the input to pass to the next handler
        """
        pass

class AppHandler:
    """
    the main lyntin app handler
    """
    def handle(self, session, read):
        if not read:
            read = session.ReadMud()

        if read:
            # handle actions and displaying stuff from mud
            mud.handle_mud_output(read, session)

        return (CONTINUE, read)



# Local variables:
# mode:python
# py-indent-offset:3
# tab-width:3
# End:
