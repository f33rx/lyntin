   syntax: #alias [{name}] [{expansion}]

   With no arguments, prints all aliases.
   With one argument, prints all aliases which match the arg.
   With multiple arguments, creates an aliase.

   You can use pattern variables which look like % and a number.
   (ex: %4).  %0 is the entire text.  %n (where n is a number)
   is the nth item after the alias name.
