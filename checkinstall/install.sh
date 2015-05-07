#!/bin/sh

INSTDIR=/usr/share/kicadbom2spec
mkdir -p $INSTDIR
mkdir -p $INSTDIR/bitmaps
mkdir -p $INSTDIR/doc
mkdir -p $INSTDIR/sample
cp -f ../bitmaps/* $INSTDIR/bitmaps
cp -f ../doc/help_linux.pdf $INSTDIR/doc
cp -f ../sample/* $INSTDIR/sample
cp -f ../CHANGELOG $INSTDIR
cp -f ../COPYING $INSTDIR
cp -f ../gui.py $INSTDIR
cp -f ../kicadbom2spec.pyw $INSTDIR
cp -f ../kicadsch.py $INSTDIR
cp -f ../pattern.ods $INSTDIR
cp -f ../README $INSTDIR
cp -f ../settings.ini $INSTDIR
cp -f ../spec.py $INSTDIR
cp -f kicadbom2spec.desktop /usr/share/applications/
cp -f ../bitmaps/icon.svg /usr/share/icons/kicadbom2spec.svg
