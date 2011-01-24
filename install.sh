#!/bin/sh
for arg; do
  case $arg in
    DESTDIR=*) DESTDIR=${arg#DESTDIR=};;
  esac;
done

# program
install -bC --mode=0644 geeksqlite.conf $DESTDIR/etc/geeksqlite
install -bC --mode=0755 geeksqlite $DESTDIR/usr/bin/geeksqlite
mkdir -p $DESTDIR/usr/lib/geeksqlite
install -bC --mode=0755 geeksqlite.py $DESTDIR/usr/lib/geeksqlite
install -bC --mode=0755 dist.py $DESTDIR/usr/lib/geeksqlite
install -bC --mode=0755 filedialog.py $DESTDIR/usr/lib/geeksqlite
mkdir -p $DESTDIR/usr/lib/geeksqlite/interface
install -bC --mode=0644 interface/*.glade $DESTDIR/usr/lib/geeksqlite/interface
# docs
install -bC --mode=0644 README $DESTDIR/usr/share/doc/geeksqlite/README
install -bC --mode=0644 ./geeksqlite.1.gz $DESTDIR/usr/man/man1/geeksqlite.1.gz
# desktop
install -bC --mode=0755 geeksqlite.desktop $DESTDIR/usr/share/applications/geeksqlite.desktop
install -bC --mode=0644 ./geeksqlite.xpm $DESTDIR/usr/share/pixmaps/geeksqlite.xpm
# localization
install -bC --mode=0644 language/de/LC_MESSAGES/geeksqlite.mo $DESTDIR/usr/share/locale/de/LC_MESSAGES/geeksqlite.mo
install -bC --mode=0644 language/en/LC_MESSAGES/geeksqlite.mo $DESTDIR/usr/share/locale/en/LC_MESSAGES/geeksqlite.mo
install -bC --mode=0644 language/eo/LC_MESSAGES/geeksqlite.mo $DESTDIR/usr/share/locale/eo/LC_MESSAGES/geeksqlite.mo
