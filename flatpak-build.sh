#!/bin/bash

#gets latest build
echo ':: copying latest build to directory...'
cp ../r2modmanPlus/dist/electron/Packaged/*.tar.gz .
#updates manifest and appdata.xml
echo ':: updating manifest...'
python3 update-version.py

#build the Flatpak
echo ':: building flatpak'
flatpak-builder --force-clean build/ com.github.ebkr.r2modman.yaml
#export the result
echo ':: exporting flatpak'
flatpak build-export export build
#export to single-file
echo ':: bundling flatpak to single-file r2modman.flatpak'
flatpak build-bundle export r2modman.flatpak com.github.ebkr.r2modman --runtime-repo=https://flathub.org/repo/flathub.flatpakrepo
echo ':: done!'