#!/bin/sh

VERSION=$(../kicadbom2spec.pyw -v)
sudo checkinstall -D \
    --default \
    --install=no \
    --pkgname=kicadbom2spec \
    --pkgversion=$VERSION \
    --pkgarch=all \
    --pkgrelease=1 \
    --pkglicense=GPLv3 \
    --pkggroup=utils \
    --pkgsource=http://launchpad.net/kicadbom2spec \
    --pakdir=../.. \
    --maintainer='"Baranovskiy Konstantin <baranovskiykonstantin@gmail.com>"' \
    --requires="python2.7",'"python-wxgtk2.8|python-wxgtk3.0"',"python-odf" \
    --nodoc \
    --backup=no \
    ./install.sh
