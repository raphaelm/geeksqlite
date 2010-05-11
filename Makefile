# geek'SQLite Makefile
all:
	msgfmt language/de/LC_MESSAGES/geeksqlite.po -o language/de/LC_MESSAGES/geeksqlite.mo
	msgfmt language/en/LC_MESSAGES/geeksqlite.po -o language/en/LC_MESSAGES/geeksqlite.mo
	msgfmt language/eo/LC_MESSAGES/geeksqlite.po -o language/eo/LC_MESSAGES/geeksqlite.mo
	gzip geeksqlite.1

clean:
	rm -f language/*/LC_MESSAGES/geeksqlite.mo
	gunzip geeksqlite.1.gz

install:
	./install.sh

uninstall:
	./uninstall.sh
