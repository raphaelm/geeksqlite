#!/bin/sh

# BUILD

# localisation
msgfmt language/de/LC_MESSAGES/geeksqlite.po -o language/de/LC_MESSAGES/geeksqlite.mo
msgfmt language/en/LC_MESSAGES/geeksqlite.po -o language/en/LC_MESSAGES/geeksqlite.mo
msgfmt language/eo/LC_MESSAGES/geeksqlite.po -o language/eo/LC_MESSAGES/geeksqlite.mo

# manpage
gzip geeksqlite.1
