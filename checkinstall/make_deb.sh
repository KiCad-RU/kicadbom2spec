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
    --requires="python3","python3-wxgtk4.0","python3-odf" \
    --nodoc \
    --backup=no \
    ./install.sh
