syntax: #session {ses_name} {ip|hostname} {port}

This is the command you use to connect to the muds. The session that 
you startup will become the active session. That is, all commands you 
type, will be sent to this session.

Here's a small example to get you started:
It shows how you can log into GrimneMUD with 2 chars and play a bit 
with them.

ex: #session valgar 129.241.36.229 4000 <= define a session named
                                          'valgar'.
ex: #session eto gytje.pvv.unit.no 4000 <= define session named
                                           'eto'.
You can change the active session, by typing #sessionname 
#eto      <=make the char in the 'eto' session the active one.
...       <= all commands now go to session 'eto'.
#valgar   <=switching now to session 'valgar'.

