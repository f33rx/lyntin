syntax: #variable {name} {value}

Creates a variable for that session of said name with said value.
Variables can then be used in #if commands and any predicates
of #alias or #action.

ex:
   #variable {hps} {100}
   #action {HP: %0/%1 } {#variable {hps} {%0}}

Variables can later be accessed via the variable character
(which defaults to $) and the variable name.  In the case of the
above, the variable name would be $hps.
