   syntax: #highlight {style} {text to highlight}

   With no arguments, prints all highlights.
   With one argument, prints all highlights which match the arg.
   With multiple arguments, creates a highlight.

   Highlights enable you to colorfully "tag" text that's of interest
   to you with the given style.  This may not work or fully work in
   all ui's.

   Styles available are:
      bold     black    grey           b black
      blink    red      light red      b red
      reverse  green    light green    b green
               yellow   light yellow   b yellow
               blue     light blue     b blue
               magenta  light magenta  b magenta
               cyan     light cyan     b cyan
               white    light white    b white

   ex:
      #highlight {green} {Sven arrives.}
      #highlight {reverse,green} {Sven arrives.}
