#!/bin/sh

# Detects and parses the architecture
ARCH=$(uname -m)
case "$ARCH" in
 "i686") ARCH="i386";;
 "i586") ARCH="i386";;
 "i486") ARCH="i386";;
esac

echo "Target architecture: $ARCH"
OS="linux"
echo "Target operating system: $OS"

# BUILD
# localisation
msgfmt language/de/LC_MESSAGES/geeksqlite.po -o language/de/LC_MESSAGES/geeksqlite.mo
msgfmt language/en/LC_MESSAGES/geeksqlite.po -o language/en/LC_MESSAGES/geeksqlite.mo
msgfmt language/eo/LC_MESSAGES/geeksqlite.po -o language/eo/LC_MESSAGES/geeksqlite.mo
