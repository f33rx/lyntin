clean:
	rm -f *~
	rm -f help/*~
	rm -f *.pyc
	rm -f ui/*.pyc
	rm -f ui/*~
	rm -f errata/*.pyc
	rm -f errata/*~
	rm -f modules/*.pyc
	rm -f modules/*~

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
