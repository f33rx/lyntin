syntax: #gag {<text>}

With no arguments, prints out all gags.
With arguments, creates a gag.

Any incoming data from the mud which contains a gag match will
be removed and not shown on the ui.

ex: #gag {has missed you.}    <-- will prevent any incoming line
                                  with "has missed you" to be shown.
