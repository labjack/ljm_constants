#! /usr/bin/env bash
#
# Installs the LabJack constant files on a Linux or Mac system.

set -e
set -u

FILE_DIR=`dirname $0`
DESTINATION=/usr/local/share
TARGET=LabJack
OS=`uname -s`

if [ $UID != 0 ]; then
	echo "Warning: This script should probably be run as root or using sudo."
fi

if [ "$OS" != 'Linux' ] && [ "$OS" != 'Darwin' ]; then
	echo "Unknown operating system $OS"
	exit 1
fi

chmod 666 ${FILE_DIR}/${TARGET}/LJM/ljm.log

test -z $DESTINATION || mkdir -p $DESTINATION
cp --recursive --preserve=mode "${FILE_DIR}/${TARGET}" "$DESTINATION/${TARGET}"

exit 0

