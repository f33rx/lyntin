syntax: #gag {<text>}

With no arguments, prints out all gags.
With arguments, creates a gag.

Incoming lines from the mud which contain gagged text will
be removed and not shown on the ui.

Gags get converted to regular expressions.  Feel free to use
regular expression matching syntax as you see fit.

ex: #gag {has missed you.}    <-- will prevent any incoming line
                                  with "has missed you" to be shown.
