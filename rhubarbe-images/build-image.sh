#!/bin/bash

COMMAND=$(basename $0)

function die() { echo "$@" "-- exiting" ; exit 1; }

#
# this function assumes that /etc/rhubarbe-history/<to_image>/
# has been populated with a file hierarchy
# as created in build-image.py
# i.e. scripts in scripts/nnn-*
# together with details in args/ and logs/
#
function run-build-image-scripts() {
    set -e
    from_image=$1; shift
    to_image=$1; shift

    ########## extracting tarfile as copied by sshjobpusher
    rhub_dir=/etc/rhubarbe-history
    mkdir -p $rhub_dir
    tarfile=${to_image}.tar
    cd $rhub_dir
    [ -f $tarfile ] || die "Cannot find tarfile $tarfile"

    ##### try to install tar if missing
    type tar || dnf install -y tar || apt-get install -y tar
    
    echo Extracting $tarfile in $(pwd)
    tar -xvf $tarfile

    ########## Running then
    cd $to_image
    for shell in scripts/[0-9][0-9][0-9]*; do
	basename=$(basename $shell)
	args_file=args/$basename
	arguments=$(cat $args_file)
	echo "********"running $shell $arguments
	$shell $arguments 2>&1 | tee logs/$basename.log
    done
}

run-build-image-scripts "$@"
exit 0
