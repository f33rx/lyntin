   syntax: #highlight {style} {text to highlight}

   With no arguments, prints all highlights.
   With one argument, prints all highlights which match the arg.
   With multiple arguments, creates a highlight.

   Highlights enable you to colorfully "tag" text that's of interest
   to you with the given style.  This may not work or fully work in
   all ui's.

   Styles available are: reverse, bold, blink, or black, red, green
   yellow, blue, magenta, and cyan.

   ex:
      #highlight {green} {Sven arrives.}
      #highlight {reverse} {Sven arrives.}
