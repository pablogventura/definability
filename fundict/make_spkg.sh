#!/bin/bash

PKG_VERSION=`git rev-parse HEAD`
PKG_NAME="definability"

echo "Packaging $PKG_NAME version $PKG_VERSION"

# remove old
echo "Remove old version"
rm *.spkg

# build dir
echo "Building..."
find . -name '*.pyc' -delete
mv src sagepkg/
echo $PKG_VERSION > sagepkg/package-version.txt
mv sagepkg "$PKG_NAME-$PKG_VERSION"

tar -cvf "$PKG_NAME-$PKG_VERSION.spkg" "$PKG_NAME-$PKG_VERSION"

# restore and cleaning
echo "Cleaning files..."
mv "$PKG_NAME-$PKG_VERSION" sagepkg
mv sagepkg/src ./
rm sagepkg/package-version.txt
#tar -cvf minion-20110325.spkg minion-20110325
