syntax: #tick

Displays the number of seconds left before this session's
ticker ticks.

When a tick happens, it will look for a TICK!!! alias.  Finding none,
it will print TICK!!! to the ui.

This allows you to perform an event every x number of seconds.
