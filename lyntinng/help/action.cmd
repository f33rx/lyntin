syntax: #action [{trigger}] [{response}]

With no arguments, prints all actions.
With one argument, prints all actions which match the arg.
With multiple arguments, creates an action.

When data from the mud matches the trigger clause, the response
will be executed.  Trigger clauses can use anchors (^ and $)
to anchor the text to the beginning and end of the line 
respectively.

Triggers can also contain Lyntin pattern-variables which start
with a % sign and have digits: %0, %1, %10...  When Lyntin sees 
a pattern-variable in an action trigger, it tries to match any 
pattern against it, and saves any match it finds so you can 
use it in the response.  See below for examples.

The response can be any mud command or Lyntin command and can
contain placement-variables and the special variable %a which
means "the whole matched line".

Triggers get converted to regular expressions by converting
placement variables %[0-9]+ to (.+?).  Feel free to use
regular expression matching stuff.

ex:
   #action {^You are hungry} {get bread bag;eat bread}
   #action {EVISCERATES joey} {rescue joey}
   #action {%0 gives you %5} {say thanks for the %5, %0!}
   #action {^%1 tells you %2$} {say %1 just told me %2}
