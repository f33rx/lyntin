syntax: #action [{trigger}] [{response}]

With no arguments, prints all actions.
With one argument, prints all actions which match the arg.
With multiple arguments, creates an action.

When Lyntin sees text that fits the trigger, the response is 
executed.  When defining, braces '{' and '}' should be used 
around the trigger and response.  

Actions can be 'anchored' to the beginning of a line by prepending 
the trigger with '^'.  Then, the action will not be triggered 
unless it occurs at the beginning of a line.

Actions can contain Lyntin pattern-variables, which look like
%<integer>  When Lyntin sees a pattern-variable in an action 
trigger, it tries to match any pattern against it, and saves any 
match it finds so you can use it in the response.  See below for 
examples.  'response' can contain the special variable %a, which 
means "the whole matched line."

ex:
   #action {^You are hungry} {get bread bag;eat bread}
   #action {EVISCERATES joey} {rescue joey}
   #action {%0 gives you %5} {say thanks for the %5, %0!}
   #action {%1 tells you %2} {say %1 just told me %2}
