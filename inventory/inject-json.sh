#!/bin/bash

# the purpose of this script is to push the contents of a json file,
# as computed from our google spreadheet with configure.py,
# into the OMF system

# ideal workflow would then be
#
#  google spreadsheet
#  ==>
#  export as fit.csv
#  ==>
#  run configure.py and produce fit.json
#  ==>
#  run this script to inject the new definition into faraday
#

COMMAND_PATH=$0
COMMAND=$(basename $0)

HOSTNAME=faraday
FQDN=$HOSTNAME.inria.fr

JSON=fit.json
OMF_DIR=/root/omf_sfa


function die() {
    echo "$@"
    exit 1
}

function run_in_faraday() {

    [ $(hostname) == "faraday" ] || die "$Command.$0 must be run on $FDQN"

    [ $(id -u) == 0 ] || die "$COMMAND must be run as root"

    cd $OMF_DIR

    # check for input file
    [ -f $JSON ] || die "$COMMAND expects $JSON to be present in $OMF_DIR"

    ########## erase DB
    set -x
    rake autoMigrate

    ########## restart DB
    stop omf-sfa
    start omf-sfa

    ########## do it
    cd bin
    ./create_resource -t node -c conf.yaml -i $OMF_DIR/$JSON

    ########## xxx should check everything is fine
    # e.g. using curl on the REST API or something..
}
    

function run_from_git() {

    name="fit"

    [ $(hostname) != "faraday" ] || die "$COMMAND.$0 must not be run on $FDQN"

    [ -f "$name.json" ] || die "$COMMAND expects $JSON"

    if [ -f "$name.csv" ] ; then
	[ "$name.json" -nt "$name.csv" ] || die "JSON file is out of date wrt csv source"
    fi

    # push json file on OMF server
    set -x 
    rsync -a "$name.json" $COMMAND_PATH root@$FQDN:$OMF_DIR

    ssh root@$FQDN $OMF_DIR/$COMMAND
}

function main(){

    if [ $(hostname) == $HOSTNAME ] ; then
	run_in_faraday >& $OMF_DIR/$COMMAND.log
    else
	run_from_git
    fi
}

main "$@"
    
