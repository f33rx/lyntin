badfiles := $(wildcard *~ */*~ *.pyc */*.pyc )

clean:
	rm -f $(badfiles)

count:
	wc -l *.py modules/*.py ui/*.py errata/*.py

changelog:
	echo handling changelog
	cvs2cl.pl -S -P

happydocs:
	/usr/local/bin/happydoc \
	   -t "lyntin mudclient v.3.0" \
	   --author="lyntin development folks" \
	   --no_private_names \
	   formatter_compactHTML=1 \
	   *.py modules/*.py ui/*.py
