syntax: #read {filename}

Reads in a file running each line as a Lyntin command.  This is the
opposite of #write which allows you to save session settings and
restore them using #read.

You can also read in via the commandline when you start Lyntin:

  lyntin --read 3k

And read can handle HTTP urls:

  lyntin --read http://lyntin.sourceforge.net/lyntinrc

  #read http://lyntin.sourceforge.net/lyntinrc

Note: the first non-whitespace char is used to set the Lyntin
command character.  If you use non Lyntin commands in your file,
make sure the first one is a command char.  If not, use #nop .
