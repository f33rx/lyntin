syntax: #diagnostics <filename>

This is very useful for finding out all the information about Lyntin
while it's running.  This will print out operating system information,
Python version, what threads are running (assuming they're registered
with the ThreadManager), hooks, functions connected to hooks, and
#info for every session.  It's very helpful in debugging problems that
are non-obvious or are platform specific.  It's also invaluable in
bug-reporting.

It can take a filename argument and will copy the #diagnostics output
to that file.  This allows you easier method of submitting diagnostics
output along with bug reports.
