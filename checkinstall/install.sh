#!/bin/sh

INSTDIR=/usr/share/kicadbom2spec
mkdir -p $INSTDIR
mkdir -p $INSTDIR/bitmaps
mkdir -p $INSTDIR/doc
mkdir -p $INSTDIR/doc/images
mkdir -p $INSTDIR/sample
cp -f ../bitmaps/* $INSTDIR/bitmaps
cp -f ../doc/images/* $INSTDIR/doc/images
cp -f ../doc/user_manual.html $INSTDIR/doc
cp -f ../sample/* $INSTDIR/sample
cp -f ../CHANGELOG $INSTDIR
cp -f ../COPYING $INSTDIR
cp -f ../complist.py $INSTDIR
cp -f ../controls.py $INSTDIR
cp -f ../gui.py $INSTDIR
cp -f ../kicadbom2spec.pyw $INSTDIR
cp -f ../kicadsch.py $INSTDIR
cp -f ../pattern.ods $INSTDIR
cp -f ../README $INSTDIR
cp -f ../settings.ini $INSTDIR
cp -f ../version $INSTDIR
cp -f kicadbom2spec.desktop /usr/share/applications/
cp -f ../bitmaps/icon.svg /usr/share/icons/kicadbom2spec.svg
chmod -R a+r $INSTDIR/*
chmod a+x $INSTDIR/kicadbom2spec.pyw
chmod a+r /usr/share/applications/kicadbom2spec.desktop
chmod a+r /usr/share/icons/kicadbom2spec.svg
