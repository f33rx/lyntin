   syntax: #history
           !number sub=repl

   #history prints the current history buffer.

   ! will call an item in the history indexed by the number after
   the !.  You can also do replacements via the sub=repl syntax.

   ex:
      #history
          prints the history buffer
      !
          executes the last thing you did
      !4
          executes the fourth to last thing you did
      !4 3k=gk
          executes the fourth to last thing you did after replacing
          3k with gk in it
