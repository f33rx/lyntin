##################################################################
# This file is part of Lyntin
# copyright (c) Lyn Headley 1996-2001
#
# Lyntin is distributed under the GNU General Public License.  See
# the file LICENSE in the distribution for details.
# $Id$
##################################################################

from UserList import UserList

class ActionSet(UserList):
    def __init__(self):
        pass

def new():
    return ActionSet()

