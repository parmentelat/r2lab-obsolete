REPO=/root/certificates-omf

DOMAIN=r2lab.inria.fr
AM_SERVER_DOMAIN=omf:r2lab
XMPP_DOMAIN=r2lab

# extract_key [-o private_key_filename] pem_filename
function extract-key-from-pem () {
    python3 - "$@" << EOF
import sys
import os.path

from argparse import ArgumentParser

BEGIN = "-----BEGIN RSA PRIVATE KEY-----"

def extract_key_from_pem(in_filename, output_file):
    in_zone = False
    with open(in_filename) as f:
        for line in f:
            if BEGIN in line:
                in_zone = True
                output_file.write(line)
            elif in_zone:
                output_file.write(line)

def main():
    parser = ArgumentParser()
    parser.add_argument("-o", "--out", dest='output', default=None,
                        help="specify output file")
    parser.add_argument('pem_certificate', help='input pem file')
    args = parser.parse_args()
    if not args.output:
        extract_key_from_pem(args.pem_certificate, sys.stdout)
    else:
        verb="Overwrote" if os.path.isfile(args.output) else "Wrote"
        with open(args.output, 'w') as output:
            extract_key_from_pem(args.pem_certificate, output)
        print("{} {}".format(verb, args.output))
    return 0

sys.exit(main())
EOF
}

# NOTES
#
# (*) root certificate is required in common by both subsystems (nitos_testbed_rc and omf_sfa)
# (*) a first set of 3 certificates is required by nitos_testbed_rc, they are
#     user_factory.pem - cm_factory.pem - frisbee_factory.pem
# (*) second batch of certificates are required by omf_sfa, they are
#     am.pem user_cert.pem
#
# *PLUS*
# 
# (*) the certificates directory needs to contain an etc/ subdir with file omf_script_conf.yaml
# (*) remember to add GIDs describing peering authorities in trusted_roots/


### create a certificate if needed
function create-certificate () {
    name=$1; shift
    resource_type=$1; shift
    verb=$1; shift
    
    certificate=${REPO}/${name}.pem
    private_key=${REPO}/${name}.pkey
    email=${name}@${DOMAIN}
    resource_id=xmpp://${name}@${XMPP_DOMAIN}
    if [ -f $certificate ] ; then
	echo "Preserving $certificate"
    else
	command="omf_cert.rb -o $certificate $@ --email $email"
	[ $resource_type == "none" ] || command="$command --resource-type $resource_type"
	command="$command --resource-id ${resource_id} --root ${REPO}/trusted_roots/root.pem --duration 50000000 $verb"
	echo "Creating $certificate using command:"
	echo -e "\t $command"
	$command
	echo "Extracting private key into $private_key"
	extract-key-from-pem $certificate -o $private_key
    fi
}

########## root certificate

function create-certificates () {
    mkdir -p ${REPO}/trusted_roots
    cd ${REPO}/trusted_roots
    if [ -f root.pem ]; then
	echo "Preserving $(pwd)/root.pem"
    else
	command="omf_cert.rb --email root@$DOMAIN -o root.pem --duration 50000000 create_root"
	echo "Creating root certificate root.pem using command"
	echo -e "\t $command"
	$command
    fi

    ########## nitos_testbed_rc

    create-certificate user_factory user_factory create_resource
    create-certificate cm_factory cm_factory create_resource
    create-certificate frisbee_factory frisbee_factory create_resource

    # omf_cert.rb -o user_factory.pem --email user_factory@${DOMAIN} --resource-type user_factory --resource-id xmpp://user_factory@${XMPP_DOMAIN} --root /root/.omf/trusted_roots/root.pem --duration 50000000 create_resource 
    # omf_cert.rb -o cm_factory.pem --email cm_factory@${DOMAIN} --resource-type cm_factory --resource-id xmpp://cm_factory@${XMPP_DOMAIN} --root /root/.omf/trusted_roots/root.pem --duration 50000000 create_resource
    # omf_cert.rb -o frisbee_factory.pem --email frisbee_factory@${DOMAIN} --resource-type frisbee_factory --resource-id xmpp://frisbee_factory@${XMPP_DOMAIN} --root /root/.omf/trusted_roots/root.pem --duration 50000000 create_resource

    ########## omf_sfa

    create-certificate am am_controller create_resource  --geni_uri URI:urn:publicid:IDN+${AM_SERVER_DOMAIN}+user+am 
    # omf_cert.rb -o am.pem  --geni_uri URI:urn:publicid:IDN+${AM_SERVER_DOMAIN}+user+am --email am@${DOMAIN} --resource-id xmpp://am_controller@${XMPP_DOMAIN} --resource-type am_controller --root ${REPO}/trusted_roots/root.pem --duration 50000000 create_resource
    #extract_key_from_pem ${REPO}/am.pem -o ${REPO}/am.pkey
    
    create-certificate user_cert none create_user --user root  --geni_uri URI:urn:publicid:IDN+${AM_SERVER_DOMAIN}+user+root
    # omf_cert.rb -o user_cert.pem --geni_uri URI:urn:publicid:IDN+${AM_SERVER_DOMAIN}+user+root --email root@${DOMAIN} --user root --root ${REPO}/trusted_roots/root.pem --duration 50000000 create_user
    #extract_key_from_pem ${REPO}/user_cert.pem -o ${REPO}/user_cert.pkey
}

PREVIOUS_REPO=/root/working-certificates-omf

function inria-specifics () {
    set -x
    rsync -av $PREVIOUS_REPO/etc $REPO
    mkdir -p $REPO/trusted_roots
    for trusted in myslicedev.gid ple.gid; do
	rsync -av $PREVIOUS_REPO/trusted_roots/$trusted $REPO/trusted_roots
    done
    set +x
}

create-certificates
inria-specifics
