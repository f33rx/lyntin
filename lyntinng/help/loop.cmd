syntax: #loop {<from>,<to>} {<command>}

Executes a given command replacing %0 in the command with
the range of numbers specified in <from> and <to>.

ex:

  #loop {1,5} {reclaim %0.corpse}

will execute:

  reclaim 1.corpse
  reclaim 2.corpse
  reclaim 3.corpse
  reclaim 4.corpse
  reclaim 5.corpse
