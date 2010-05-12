#!/bin/bash
rm -f source.tar.gz
tar -czvf source.tar.gz geeksqlite language/*/LC_MESSAGES/geeksqlite.po interface/*.glade *.pot Makefile *.py *.sh *.conf *.xpm *.png *.ico *.desktop LICENSE README TODO
