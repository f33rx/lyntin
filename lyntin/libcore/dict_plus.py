"""
just like UserDict but with a convenient constructor
"""

from UserDict import UserDict

class c(UserDict):
    def __init__(self, **kw):
        UserDict.__init__(self)
        for key in kw.keys():
            self[key] = kw[key]

