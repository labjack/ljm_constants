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

# Remove ljm_special_addresses.config or move it to ljm_specific_ips.config
deprecate_special_addresses()
{
    if [ -f "${DESTINATION}/${TARGET}/LJM/ljm_special_addresses.config" ]; then
        if [ `cat ${DESTINATION}/${TARGET}/LJM/ljm_specific_ips.config | wc -c` -gt 1 ]; then
            echo "[Deprecation warning] Removing deprecated file:"
            echo "        ${DESTINATION}/${TARGET}/LJM/ljm_special_addresses.config"
            echo "    Contents were:"
            cat ${DESTINATION}/${TARGET}/LJM/ljm_special_addresses.config
            echo
            echo
            rm -f ${DESTINATION}/${TARGET}/LJM/ljm_special_addresses.config
        else
            echo "[Deprecation warning] Moving:"
            echo "        ${DESTINATION}/${TARGET}/LJM/ljm_special_addresses.config"
            echo "    to:"
            echo "        ${DESTINATION}/${TARGET}/LJM/ljm_specific_ips.config"
            mv -f \
                ${DESTINATION}/${TARGET}/LJM/ljm_special_addresses.config \
                ${DESTINATION}/${TARGET}/LJM/ljm_specific_ips.config
        fi
    fi
}

# Handle installation on older Macs
oldinstall ()
{
    echo "$0 - Attempting to catch and handle an error for older machines (mostly Mac 10.5)..."
    cp -vR "${FILE_DIR}/${TARGET}" "${DESTINATION}/"
    chmod 666 "${DESTINATION}/${TARGET}/LJM/ljm.log"
    echo "$0 - Error caught and handled successfully. Exiting now with success."
    exit 0
}

# Install empty, valid, and world read/writable auto IPs file
install_auto_ips_file ()
{
    AIPS_FILE='/usr/local/share/LabJack/LJM/ljm_auto_ips.json'
    if [ ! -f ${AIPS_FILE} ]; then
        echo "creating new ${AIPS_FILE}"
        echo '{"autoIPs":[]}' > ${AIPS_FILE}
    fi
    chmod a+rw ${AIPS_FILE}
}

remove_artifacts ${TARGET}
remove_artifacts ${TARGET}/LJM

rm -f ${DESTINATION}/${TARGET}/LJM/readme_ljm_special_addressess.md

test -d ${DESTINATION}/LabJack/LJM || mkdir -p ${DESTINATION}/LabJack/LJM
chmod 777 ${DESTINATION}/LabJack/LJM

chmod 666 ${FILE_DIR}/${TARGET}/LJM/ljm.log

install_auto_ips_file

touch ${DESTINATION}/${TARGET}/LJM/ljm_specific_ips.config
chmod 666 ${DESTINATION}/${TARGET}/LJM/ljm_specific_ips.config

deprecate_special_addresses

trap oldinstall EXIT
cp -v --recursive --preserve=mode "${FILE_DIR}/${TARGET}" "${DESTINATION}/"
trap - EXIT

exit 0

