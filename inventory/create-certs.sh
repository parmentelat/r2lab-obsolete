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
PRIVATE_AREA=/root/certificates-omf
PUBLIC_AREA=/etc/nitos_testbed_rc/trusted_roots

# create the root CA for 10 years
CA_DURATION=$((3600*24*365*10))
# others for 2 years
DURATION=$((3600*24*365*2))

# use option -f to force re-creation of exiting certificates
FORCE_OVERWRITE=

#################### utility for splitting a pem into public and private parts
# extract_key [-o private_key_filename] pem_filename
function split-pem () {
    python3 - "$@" << EOF
#!/usr/bin/env python3

import sys
import os.path

from argparse import ArgumentParser

BEGIN = "-----BEGIN RSA PRIVATE KEY-----"

def split_pem(cert_filename, pub_filename, priv_filename):
    """
    From
    (*) cert_filename : expected to contain one full cert 
                        (i.e. one with a private key) expected to be found
    Creates 2 py-products
    (*) pub_filename : that contains only the public part of said certificate
    (*) priv_filename: that contains the public key
    
    Returns
    Overwrite message when everything goes fine
    or None if no private key is found in input
    """
    # load in memory
    with open(cert_filename) as input:
        full_cert_lines = input.readlines()
    # if no private key is present, do nothing and return None
    found = [ line for line in full_cert_lines if BEGIN in line ]
    if not found:
        return
    # rewrite in 2 separate files
    in_private = False
    with open(pub_filename, 'w') as public:
        with open(priv_filename, 'w') as private:
            for line in full_cert_lines:
                if BEGIN in line:
                    in_private = True
                    private.write(line)
                else:
                    output = public if not in_private else private
                    output.write(line)
    return [ "(Over)wrote {}\n".format(name)
             for name in (pub_filename, priv_filename)]

def main():
    parser = ArgumentParser()
    parser.add_argument("-u", "--public", dest='public', default=None,
                        help="specify output file for public part")
    parser.add_argument("-i", "--private", dest='private', default=None,
                        help="specify output file for private part")
    parser.add_argument('pem_certificate', help='input pem file')
    args = parser.parse_args()
    if not args.public:
        args.public = args.pem_certificate.replace(".pem", ".public.pem")
    if not args.private:
        args.private = args.pem_certificate.replace(".pem", ".private.pem")
    messages = split_pem(args.pem_certificate,
                        args.public,
                        args.private)
    if not messages:
        print("Nothing done (no private key in {})".format(args.pem_certificate))
        return 1
    else:
        for line in messages:
            print(line, end='')
        return 0

sys.exit(main())
EOF
}

### create a certificate if needed
function create-certificate () {
    do_split=""
    if [ "$1" == "-s" ] ; then
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
	echo "Creating $certificate using command:"
	echo -e "\t $command"
	# don't do it
	[ -z "$DRY_RUN" ] && $command
	if [ -n "$do_split" ] ; then
	    command="split-pem $certificate --public $public_only --private $private_key"
	    echo "Extracting using command:"
	    echo -e "\t $command"
	    [ -z "$DRY_RUN" ] && $command
	fi
    fi
}

function create-certificates () {

    mkdir -p ${PRIVATE_AREA} ${PUBLIC_AREA} 

    ## root certificate
    root_pem=${PRIVATE_AREA}/${ROOT}.pem
    if [ -f $root_pem -a -z "$FORCE_OVERWRITE" ]; then
	echo "Preserving $root_pem"
    else
	command="omf_cert.rb --email root@${DOMAIN} -o $root_pem --duration $CA_DURATION create_root"
	echo "Creating root CA certificate $root_pem using command"
	echo -e "\t $command"
	[ -z "$DRY_RUN" ] && $command
	command="split-pem $root_pem --public ${PUBLIC_AREA}/${ROOT}.public.pem"
	echo "Extracting using command:"
	echo -e "\t $command"
	[ -z "$DRY_RUN" ] && $command
    fi
    

    ########## nitos_testbed_rc

    create-certificate create_resource user_factory user_factory user_factory 
    create-certificate create_resource cm_factory cm_factory cm_factory
    create-certificate create_resource frisbee_factory frisbee_factory frisbee_factory

    # omf_cert.rb -o user_factory.pem --email user_factory@${DOMAIN} --resource-type user_factory --resource-id xmpp://user_factory@${XMPP_DOMAIN} --root /root/.omf/trusted_roots/root.pem --duration 50000000 create_resource 
    # omf_cert.rb -o cm_factory.pem --email cm_factory@${DOMAIN} --resource-type cm_factory --resource-id xmpp://cm_factory@${XMPP_DOMAIN} --root /root/.omf/trusted_roots/root.pem --duration 50000000 create_resource
    # omf_cert.rb -o frisbee_factory.pem --email frisbee_factory@${DOMAIN} --resource-type frisbee_factory --resource-id xmpp://frisbee_factory@${XMPP_DOMAIN} --root /root/.omf/trusted_roots/root.pem --duration 50000000 create_resource

    ########## omf_sfa

    create-certificate -s create_resource am am am_controller --geni_uri URI:urn:publicid:IDN+${AM_SERVER_DOMAIN}+user+am 
    # omf_cert.rb -o am.pem  --geni_uri URI:urn:publicid:IDN+${AM_SERVER_DOMAIN}+user+am --email am@${DOMAIN} --resource-id xmpp://am_controller@${XMPP_DOMAIN} --resource-type am_controller --root ${REPO}/trusted_roots/root.pem --duration 50000000 create_resource
    #extract_key_from_pem ${REPO}/am.pem -o ${REPO}/am.pkey
    
    create-certificate create_user user_cert root none --user root --geni_uri URI:urn:publicid:IDN+${AM_SERVER_DOMAIN}+user+root
    # omf_cert.rb -o user_cert.pem --geni_uri URI:urn:publicid:IDN+${AM_SERVER_DOMAIN}+user+root --email root@${DOMAIN} --user root --root ${REPO}/trusted_roots/root.pem --duration 50000000 create_user
    #extract_key_from_pem ${REPO}/user_cert.pem -o ${REPO}/user_cert.pkey
}

FEDERATED=/root/certificates-federated/

function inria-specifics () {
    set -x
    for trusted in $FEDERATED/*.gid; do
	rsync -av $trusted $PUBLIC_AREA/
    done
    set +x
}

function main () {
    while getopts "u:i:nf" opt; do
	case $opt in
	    u) PUBLIC_AREA=$OPTARG;;
	    i) PRIVATE_AREA=$OPTARG;;
	    f) FORCE_OVERWRITE=true;;
	    n) DRY_RUN=true;;
	esac
    done
    create-certificates
    [ -z "$DRY_RUN" ] && inria-specifics
}

main "$@"
