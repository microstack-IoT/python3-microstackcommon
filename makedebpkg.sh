#!/bin/bash

## docs
# cd docs/
# make html
# cd -

python setup.py --command-packages=stdeb.command sdist_dsc

version=$(cat microstackcommon/version.py | sed 's/.*\([0-9]\.[0-9]\.[0-9]\).*/\1/')
cd deb_dist/microstackcommon-$version/

cp {../../dpkg-files,debian}/control
cp {../../dpkg-files,debian}/copyright
cp {../../dpkg-files,debian}/rules

cp {../../dpkg-files,debian}/python-microstackcommon.install
cp {../../dpkg-files,debian}/python-microstackcommon.udev
cp ../../dpkg-files/post-installation.sh debian/python-microstackcommon.postinst
# cp ../../bin/post-removal.sh debian/python-microstackcommon.postrm

cp {../../dpkg-files,debian}/python3-microstackcommon.install
cp {../../dpkg-files,debian}/python3-microstackcommon.udev
cp ../../dpkg-files/post-installation.sh debian/python3-microstackcommon.postinst
# cp ../../bin/post-removal.sh debian/python3-microstackcommon.postrm


dpkg-buildpackage -us -uc
