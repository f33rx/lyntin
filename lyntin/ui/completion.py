#!/usr/local/bin/python1.4

#
# entry widget with file completion support
#
# fredrik lundh, may 1998
#
# fredrik@pythonware.com
# http://www.pythonware.com
#

from Tkinter import *

import os

#
# completion entry baseclass.

class CompletionEntry(Entry):

    def __init__(self, master, **kw):

        apply(Entry.__init__, (self, master), kw)

        self.bind("<Tab>", self.__tab)
        self.unbind_all()
        self.bind("<Return>", self.store_input)
        self.__state = None, None, None
        self.input = []

    def store_input(self, event):
        val = self.get()
        if not val:
            self.input.append('\n')
        self.input.append(val)
        self.delete(0, 'end')

    def __tab(self, event):

        #import pdb;pdb.set_trace()
        index = self.index(INSERT)
        value = self.get()
        prefix, suffix = value[:index], value[index:]

        # check state
        state, old_index, old_prefix = self.__state
        if index != old_index or prefix != old_prefix:
            state = 0

        try:

            # get next completion
            match = self.complete(state, prefix, suffix)

            if match:

                # insert completion
                if self.select_present():
                    self.delete(SEL_FIRST, SEL_LAST)
                self.insert(index, match)
                self.select_range(index, index+len(match))
                self.icursor(index)

                self.__state = state+1, index, prefix

            else:

                self.__state = 0, index, prefix

        except IndexError:
            pass

        return "break"

    def complete(self, state, prefix, suffix):
        return None # override

#
# file completion

class FileEntry(CompletionEntry):

    def complete(self, state, prefix, suffix):

        #import pdb;pdb.set_trace()

        # workaround os.path.isdir buglet
        path = prefix
        if path[-1:] in ("/", os.sep):
            path = path[:-1] # chop off final /

        # get directory and file prefix
        if os.path.isdir(path):
            path, prefix = prefix, ""
        else:
            path, prefix = os.path.split(prefix)

        if state == 0:

            try:

                # look for matching files in directory
                prefix = os.path.normcase(prefix)
                length = len(prefix)

                # build a list of the candidates
                self.__files = []
                for file in os.listdir(path):
                    file = os.path.normcase(file)
                    if file[:length] == prefix:
                        if os.path.isdir(os.path.join(path, file)):
                            file = file + os.sep
                        self.__files.append(file)

            except os.error:
                self.__files = []

        # return next match
        return self.__files[state][len(prefix):]

    def __init__(self, master, **kw):
        #import pdb;pdb.set_trace()
        apply(CompletionEntry.__init__, (self, master), kw)


#
# test stuff

if __name__ == "__main__":

    e = FileEntry(None)
    e.pack()

    e.focus_set()

    mainloop()

