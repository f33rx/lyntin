syntax: #read {filename}

Reads in a file running each line as a Lyntin command.  This is the
opposite of #write which allows you to save session settings and
restore them using #read.

You can also read in via the commandline when you start Lyntin:

  lyntin --read 3k

And read can handle HTTP urls:

  lyntin --read http://lyntin.sourceforge.net/lyntinrc

  #read http://lyntin.sourceforge.net/lyntinrc
