##################################################################
# This file is part of Lyntin
# copyright (c) Lyn Headley 1996-2001
#
# Lyntin is distributed under the GNU General Public License.  See
# the file LICENSE in the distribution for details.
# $Id$
##################################################################
"""
just like UserDict but with a convenient constructor
"""

from UserDict import UserDict

class c(UserDict):
   def __init__(self, **kw):
      UserDict.__init__(self)
      for key in kw.keys():
         self[key] = kw[key]
