#!/bin/bash
#
# the purpose of this script is to automate the creation of certificates
# required for running the couple nitos_tesbed + omf_sfa
#
# our scheme is to
# (*) store all sensitive material (what contains private keys) in
#     /root/certificates-omf
#     which, for some reason, is also reachable from symlink
#     /root/.omf -> /root/certificates-omf
# (*) store all public root certificates (without private key) in
#     /etc/nitos_testbed_rc/trusted_roots
# (*) use more meaningful name for the root certificate (and its variants)
#     i.e. use names in r2lab.* 
# SCOPE
#
# (*) root certificate is required in common by both subsystems (nitos_testbed_rc and omf_sfa)
# (*) a first set of 3 certificates is required by nitos_testbed_rc, they are
#     user_factory.pem - cm_factory.pem - frisbee_factory.pem
# (*) second batch of certificates are required by omf_sfa, they are
#     am.pem user_cert.pem
# 
# NOTES
#
# (*) remember to add GIDs describing peering authorities in trusted_roots/
#     although I am not 100% sure this is a requirement any longer, but it won't hurt
#

# our global settings
DOMAIN=r2lab.inria.fr
AM_SERVER_DOMAIN=omf:r2lab
XMPP_DOMAIN=r2lab

# the name for the root certificate
ROOT=r2lab
PRIVATE_AREA=/root/.omf
PUBLIC_AREA=/etc/nitos_testbed_rc/trusted_roots
# any file in .pem or .gid from this location will be rsynced under the public area
FEDERATED=/root/certificates-federated/

# create the root CA for 10 years
CA_DURATION=$((3600*24*365*10))
# others for 2 years
DURATION=$((3600*24*365*2))

# use option -n to run in dry-mode
DRY_RUN=
# use option -o to force overwriting of exiting certificates
FORCE_OVERWRITE=

#################### utility to display/run a command in dry-mode
# show_and_run "some message" the command to be run
# does not support piping or redirecting
function show_and_run () {
    message="$1"; shift
    command="$@"
    echo "$message using command:"
    [ -n "$DRY_RUN" ] && echo -n "(dry)"
    echo -e "\t $command"
    # do it unless dry-run
    [ -z "$DRY_RUN" ] && $command
}    
    
#################### utility for splitting a pem into public and private parts
# split-pem full-cert public-part private-part
function split-pem () {
    full=$1; shift
    public=$1; shift
    private=$1; shift

    MARKER="-----BEGIN RSA PRIVATE KEY-----"
    sed -n "/${MARKER}/q;p" $full > $public
    (echo "${MARKER}" ; sed -n "/${MARKER}/"'{:a;n;p;ba}' $full) > $private
}

### create a certificate if needed
function create-certificate () {
    do_split=""
    if [ "$1" == "--split" ] ; then
	do_split=true
	shift
    fi
    verb=$1; shift
    name=$1; shift
    email=$1; shift
    resource_type=$1; shift
    # rest of the command line is passed to omf_cert.rb
    
    certificate=${PRIVATE_AREA}/${name}.pem
    private_key=${PRIVATE_AREA}/${name}.pkey
    public_only=${PUBLIC_AREA}/${name}.public.pem
    email=${email}@${DOMAIN}
    resource_id=xmpp://${name}@${XMPP_DOMAIN}
    if [ -f $certificate -a -z "$FORCE_OVERWRITE" ] ; then
	echo "Preserving $certificate"
    else
	command="omf_cert.rb -o $certificate $@ --email $email"
	[ "$resource_type" == "none" ] || command="$command --resource-type $resource_type"
	command="$command --resource-id ${resource_id} --root ${PRIVATE_AREA}/${ROOT}.pem --duration $DURATION $verb"
	show_and_run "Creating $certificate" $command
	if [ -n "$do_split" ] ; then
	    command="split-pem $certificate $public_only $private_key"
	    show_and_run "Extracting public/private into $public_only $private_key" $command
	fi
    fi
}

function create-certificates () {

    [ -z "$DRY_RUN" ] && mkdir -p ${PRIVATE_AREA} ${PUBLIC_AREA} 

    ## root certificate
    root_pem=${PRIVATE_AREA}/${ROOT}.pem
    if [ -f $root_pem -a -z "$FORCE_OVERWRITE" ]; then
	echo "Preserving $root_pem"
    else
	command="omf_cert.rb --email root@${DOMAIN} -o $root_pem --duration $CA_DURATION create_root"
	show_and_run "Creating root CA certificate $root_pem" $command
	public_pem=${PUBLIC_AREA}/${ROOT}.public.pem
	command="split-pem $root_pem $public_pem /dev/null"
	show_and_run "Exposing public key into $public_pem" $command
    fi
    

    ########## nitos_testbed_rc

    create-certificate create_resource user_factory user_factory user_factory 
    create-certificate create_resource cm_factory cm_factory cm_factory
    create-certificate create_resource frisbee_factory frisbee_factory frisbee_factory

    # these are the commands the doc says should be issued
    # omf_cert.rb -o user_factory.pem --email user_factory@${DOMAIN} --resource-type user_factory --resource-id xmpp://user_factory@${XMPP_DOMAIN} --root /root/.omf/trusted_roots/root.pem --duration 50000000 create_resource 
    # omf_cert.rb -o cm_factory.pem --email cm_factory@${DOMAIN} --resource-type cm_factory --resource-id xmpp://cm_factory@${XMPP_DOMAIN} --root /root/.omf/trusted_roots/root.pem --duration 50000000 create_resource
    # omf_cert.rb -o frisbee_factory.pem --email frisbee_factory@${DOMAIN} --resource-type frisbee_factory --resource-id xmpp://frisbee_factory@${XMPP_DOMAIN} --root /root/.omf/trusted_roots/root.pem --duration 50000000 create_resource

    ########## omf_sfa

    create-certificate --split create_resource am am am_controller --geni_uri URI:urn:publicid:IDN+${AM_SERVER_DOMAIN}+user+am 
    create-certificate create_user user_cert root none --user root --geni_uri URI:urn:publicid:IDN+${AM_SERVER_DOMAIN}+user+root

    # these are the commands the doc says should be issued
    # omf_cert.rb -o am.pem  --geni_uri URI:urn:publicid:IDN+${AM_SERVER_DOMAIN}+user+am --email am@${DOMAIN} --resource-id xmpp://am_controller@${XMPP_DOMAIN} --resource-type am_controller --root ${REPO}/trusted_roots/root.pem --duration 50000000 create_resource
    # omf_cert.rb -o user_cert.pem --geni_uri URI:urn:publicid:IDN+${AM_SERVER_DOMAIN}+user+root --email root@${DOMAIN} --user root --root ${REPO}/trusted_roots/root.pem --duration 50000000 create_user
}


function publish-federated () {
    # show message when federated not found
    [ -d $FEDERATED ] || {
	echo "Could not find $FEDERATED"
	echo "You could store there .pem or .gid files that are meant to be exposed in $PUBLIC_AREA"
	return
    }
    # restrict to .pem and .gid files only
    echo "--------------------"
    for trusted in $(ls -d $FEDERATED/*.pem $FEDERATED/*.gid 2> /dev/null); do
	command="rsync -av $trusted $PUBLIC_AREA/"
	show_and_run "Syncing federated trusted root $certificate" $command
	echo "--------------------"
    done
    set +x
}

function restart-all () {
    show_and_run "Restarting nitos testbed" restart ntrc
    show_and_run "Restarting omf-sfa broker service" service omf-sfa restart
}

function main () {
    while getopts "u:i:f:on" opt; do
	case $opt in
	    u) PUBLIC_AREA=$OPTARG;;
	    i) PRIVATE_AREA=$OPTARG;;
	    f) FEDERATED=$OPTARG;;
	    o) FORCE_OVERWRITE=true;;
	    n) DRY_RUN=true;;
	esac
    done
    echo Will store private material in $PRIVATE_AREA
    echo Will store public trusted roots in $PUBLIC_AREA
    echo Will also mirror any .pem or .gid file from $FEDERATED with trusted roots
    echo ====================

    create-certificates
    publish-federated
    restart-all
}

main "$@"
