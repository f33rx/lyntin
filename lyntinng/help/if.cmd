   syntax: #if {<expr>} {<action>}

   Allows you to do some boolean logic based on Lyntin variables
   or any Python expression.  If this expression returns a non-false
   value, then the action will be performed.

   For example:

     #if {$myhpvar < 100} {#showme PANIC!}

     #if {$myhpvar < 100 && $myspvar < 100} {#showme PANIC!}
