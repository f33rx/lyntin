#
# Tkinter
# $Id: font.py,v 1.3 2000/06/06 18:55:56 james Exp $
#
# font wrapper
#
# written by Fredrik Lundh <fredrik@pythonware.com>, February 1998
#
# FIXME: should add 'displayof' option where relevant
#        (actual, families, measure, and metrics)
# 
# Copyright (c) Secret Labs AB 1998.
#
# info@pythonware.com
# http://www.pythonware.com
#

import Tkinter
import string

NORMAL = "normal"
BOLD = "bold"
ITALIC = "italic"

class Font:

    """Represents a named font.

    Constructor options are either:
    font -- font specifier (name, system font, or (family, size, style)-tuple)
       or any combination of
    family -- font 'family', e.g. Courier, Times, Helvetica
    size -- font size in points
    weight -- font thickness: NORMAL, BOLD
    slant -- font slant: NORMAL, ITALIC
    underline -- font underlining: false (0), true (1)
    overstrike -- font strikeout: false (0), true (1)
    name -- name to use for this font configuration (defaults to a unique name)
    """

    def _set(self, kw):
        options = []
        for k, v in kw.items():
            options.append("-"+k)
            options.append(str(v))
        return tuple(options)

    def _get(self, args):
        options = []
        for k in args:
            options.append("-"+k)
        return tuple(options)

    def __init__(self, root=None, font=None, name=None, **options):
        if not root:
            root = Tkinter._default_root
        if font:
            if type(font) == type(()):
                name = "%s %d" % (font[0], font[1])
                if font[2:]:
                    name = name + " " + string.join(font[2:])
            else:
                name = font
        elif not name:
            name = "font" + str(id(self))
        self.root = root
        self.name = name
        self.call = root.tk.call
        if font:
            return
        apply(self.call, ("font", "create", self.name) + self._set(options))

    def __str__(self):
        return self.name

    def __del__(self):
        try:
            self.call("font", "delete", self.name)
        except Tkinter.TclError:
            pass

    def actual(self, option=None):
        "Return actual font attributes"
        if option:
            return self.call("font", "actual", self.name, "-"+option)
        else:
            res = self.root.tk.splitlist(
                self.call("font", "actual", self.name)
                )
            options = {}
            for i in range(0, len(res), 2):
                options[res[i][1:]] = res[i+1]
            return options

    def cget(self, option):
        "Get font attribute"
        return self.call("font", "config", self.name, "-"+option)

    def config(self, **options):
        "Modify font attributes"
        apply(self.call, ("font", "config", self.name) + self._set(options))

    configure = config
    
    def measure(self, text):
        "Return text width"
        return string.atoi(self.call("font", "measure", self.name, text))

    def metrics(self, *options):
        "Return font metrics"
        if options:
            return string.atoi(
                self.call("font", "metrics", self.name, self._get(options))
                )
        else:
            res = self.root.tk.splitlist(
                self.call("font", "metrics", self.name)
                )
            options = {}
            for i in range(0, len(res), 2):
                options[res[i][1:]] = string.atoi(res[i+1])
            return options

def families(root=None):
    "Get font families (as a tuple)"
    if not root:
        root = Tkinter._default_root
    return root.tk.splitlist(root.tk.call("font", "families"))     

def names(root=None):
    "Get names of defined fonts (as a tuple)"
    if not root:
        root = Tkinter._default_root
    return root.tk.splitlist(root.tk.call("font", "names"))

# --------------------------------------------------------------------
# test stuff
    
if __name__ == "__main__":

    root = Tkinter.Tk()

    f = Font(family="times", size=30, weight=NORMAL)

    print families()

    print f.actual()
    print f.actual("family")
    print f.actual("weight")

    print f.cget("family")
    print f.cget("weight")

    print names()

    print f.measure("hello"), f.metrics("linespace")

    print f.metrics()

    f = Font(font=("Courier", 20, "bold", "italic"))
    print f.measure("hello"), f.metrics("linespace")

    w = Tkinter.Button(root, text="Hello, world", font=f)
    w.pack()

    Tkinter.mainloop()
