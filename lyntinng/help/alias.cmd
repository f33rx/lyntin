syntax: #alias [{name}] [{expansion}]

With no arguments, prints all aliases.
With one argument, prints all aliases which match the arg.
With multiple arguments, creates an alias.

You can use pattern variables which look like % and a number.
(ex: %4).   %0 is the alias name, %n (where n is a number)
is the nth item after the alias name.  

Ranges can be used by using python colon-syntax, specifying a
half-open slice of the input items, so %0:3 is the first, second and
third elements of the input

Negative numbers count back from the end of the list.  So %-1 is the
last item in the list, %:-1 is everything but the last item in the
list. 

Note: It should be noted that actions are matched via 
regular expressions and that %1 will get translated to (.*?)
for the regular expression match.

