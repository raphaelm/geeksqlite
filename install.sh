#!/bin/sh
for arg; do
  case $arg in
    DESTDIR=*) DESTDIR=${arg#DESTDIR=};;
  esac;
done

# program
install -bC --mode=0755 geeksqlite.conf $DESTDIR/etc/geeksqlite
install -bC --mode=0755 geeksqlite $DESTDIR/usr/bin/geeksqlite
install -bC --mode=0755 geeksqlite.py $DESTDIR/usr/lib/geeksqlite/geeksqlite.py
install -bC --mode=0755 dist.py $DESTDIR/usr/lib/geeksqlite/dist.py
install -bC --mode=0755 version.py $DESTDIR/usr/lib/geeksqlite/version.py
install -bC --mode=0755 filedialog.py $DESTDIR/usr/lib/geeksqlite/filedialog.py
install -bC --mode=0744 interface/*.glade $DESTDIRusr/lib/geeksqlite/
# docs
install -bC --mode=0744 README $DESTDIR/usr/share/doc/geeksqlite/README
gzip geeksqlite.1
install -bC --mode=0744 ./cookiepascal.1.gz $DESTDIR/usr/man/man1/geeksqlite.1.gz
# desktop
install -bC --mode=0744 geeksqlite.desktop $DESTDIR/usr/share/applications/geeksqlite.desktop
# localization
install -bC --mode=0744 language/de/LC_MESSAGES/geeksqlite.mo $DESTDIR/usr/share/locale/de/LC_MESSAGES/geeksqlite.mo
install -bC --mode=0744 language/en/LC_MESSAGES/geeksqlite.mo $DESTDIR/usr/share/locale/en/LC_MESSAGES/geeksqlite.mo
install -bC --mode=0744 language/eo/LC_MESSAGES/geeksqlite.mo $DESTDIR/usr/share/locale/eo/LC_MESSAGES/geeksqlite.mo

# Future:
#install -bC --mode=0755 ./geeksqlite.xpm $DESTDIR/usr/share/pixmaps/geeksqlite.xpm
