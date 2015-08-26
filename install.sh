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

# Remove artifacts from the specified dir, as given relative to this file.
remove_artifacts ()
{
    dir_to_clean=${FILE_DIR}/$1

    if [ ! -d ${dir_to_clean} ]; then
        echo "Warning: Directory does not exist: ${dir_to_clean}"
        return
    fi

    # http://stackoverflow.com/questions/6363441/check-if-a-file-exists-with-wildcard-in-shell-script
    for f in ${dir_to_clean}/*~; do

        ## Check if the glob gets expanded to existing files.
        ## If not, f here will be exactly the pattern above
        ## and the exists test will evaluate to false.
        if [ -e "$f" ]; then
            echo Removing ${dir_to_clean}/*~
            rm ${dir_to_clean}/*~
        fi

        ## This is all we needed to know, so we can break after the first iteration
        break
    done
}

remove_artifacts ${TARGET}
remove_artifacts ${TARGET}/LJM

chmod 666 ${FILE_DIR}/${TARGET}/LJM/ljm.log
chmod 666 ${FILE_DIR}/${TARGET}/LJM/ljm_special_addresses.config

test -d $DESTINATION || mkdir -p $DESTINATION


oldinstall ()
{
	echo "$0 - Attempting to catch and handle an error for older machines (mostly Mac 10.5)..."
	cp -vR "${FILE_DIR}/${TARGET}" "${DESTINATION}/"
	chmod 666 "${DESTINATION}/${TARGET}/LJM/ljm.log"
	echo "$0 - Error caught and handled successfully. Exiting now with success."
	exit 0
}

trap oldinstall EXIT
cp -v --recursive --preserve=mode "${FILE_DIR}/${TARGET}" "${DESTINATION}/"
trap - EXIT

exit 0

