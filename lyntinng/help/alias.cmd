   syntax: #alias [{name}] [{expansion}]

   With no arguments, prints all aliases.
   With one argument, prints all aliases which match the arg.
   With multiple arguments, creates an alias.

   You can use pattern variables which look like % and a number.
   (ex: %4).  %0 is the entire text.  %n (where n is a number)
   is the nth item after the alias name.

   Note: It should be noted that actions are matched via 
   regular expressions and that %1 will get translated to (.*?)
   for the regular expression match.
