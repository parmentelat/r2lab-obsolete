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
#  run configure.py and produce r2lab*json
#  ==>
#  run this script to inject the new definition into faraday
#

COMMAND_PATH=$0
COMMAND=$(basename $0)
LOG=$(basename $0 .sh).log

# when run outside of an OMF server, the default is to
# push files onto faraday and then invoke ourselves again
# through ssh

DEFAULT_OMF_SERVER=faraday.inria.fr

OMF_DIR=/root/omf_sfa

# for debugging
#DEBUG=echo


function die() {
    echo "$@"
    exit 1
}

function run_in_omf_server() {

    name="$1"; shift
    json="$name"-omf.json
    
    [ -d $OMF_DIR ] || die "$COMMAND.$0 must not be run in an OMF server"

    [ $(id -u) == 0 ] || die "$COMMAND must be run as root"

    cd $OMF_DIR

    # check for input file
    [ -f $json ] || die "$COMMAND expects $json to be present in $OMF_DIR"

    ########## erase DB
    set -x
    # tmp : June 2015 - not working on postgresql
    # rake db:reset
    $DEBUG stop omf-sfa
    $DEBUG psql template1 -c 'drop database inventory'
    createdb --owner omf_sfa --encoding=UTF8 inventory
    rake db:migrate

    ########## restart DB
    $DEBUG start omf-sfa

    echo "Leaving 5s for the server to warm up"
    sleep 5
    
    ########## do it
    # former version was using FRCP but was very slow and is not maintained anymore
    # $DEBUG bin/create_resource -t node -c bin/conf.yaml -i $json

    # use the REST interface instead that is much faster

    curl -k --cert /root/.omf/user_cert.pem \
	 -H "Accept: application/json" -H "Content-Type:application/json" -X POST \
	 -d @$json -i https://localhost:12346/resources/nodes
    
    ########## xxx should check everything is fine
    # e.g. using curl on the REST API or something..
}
    

function main(){

    # default value
    name="fit"
    [[ -n "$@" ]] && { name="$1"; shift; }

    # figure if we are running on an OMF server 
    # or from a remote location
    if [ -d $OMF_DIR ] ; then
	run_in_omf_server $name >& $OMF_DIR/$LOG
    else
	die "Could not find $OMF_DIR - not an OMF server"
    fi
}

main "$@"
    
