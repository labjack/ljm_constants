#! /bin/sh
#
# Installs the LabJack constant files for Linux and Mac. Run with sudo.
#

# So that you can call this script from a different directory
FILE_DIR=`dirname $0`

DESTINATION=/usr/local/share
TARGET=LabJack
OS=`uname -s`

if [ "$OS" != 'Linux' ] && [ "$OS" != 'Darwin' ]; then
	echo "Unknown operating system $OS"
	exit 1
fi

echo "Installing LabJack constant files..."

test -z $DESTINATION || mkdir -p $DESTINATION
cp -R "${FILE_DIR}/${TARGET}" $DESTINATION

echo "Done"

exit 0
