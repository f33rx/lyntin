all:

gendocs:
	/bin/date > GENERATE
	/mud/htmldoc/htmldoc.py *.py -name lyntin -m /home/mouse/lyntin/lyncurr/ >> GENERATE 2>&1
	/bin/rm /home/httpd/html/lyntin/archdocs/*
	/bin/mv *.html /home/httpd/html/lyntin/archdocs/
	/bin/mv GENERATE /home/httpd/html/lyntin/archdocs/

clean:
	rm -i *.pyc *.py~
