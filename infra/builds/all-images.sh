#/bin/bash

case $(hostname) in
    faraday*)
	gateway=localhost
	gitroot=/root/r2lab
	;;
    *)
	gateway=root@faraday.inria.fr
	gitroot=$HOME/git/r2lab
	;;
esac

###
build=$gitroot/rhubarbe-images/build-image.py

# we don't need all these includes everywhere but it makes it easier
function bim () {
    command="$build $gateway -p $gitroot/infra/user-env -i oai-common.sh -i nodes.sh -i r2labutils.sh"
    echo $command "$@"
    $command "$@"
}

# run with an arg to get the command to run manually
[[ -n "$@" ]] && { bim --help; exit; }

####################
# augment ubuntu-16.04 with ntp
#bim fit01 ubuntu-16.04-v4-node-env ubuntu-16.04-v5-ntp \
#  "imaging.sh ubuntu-setup-ntp" \
#  "nodes.sh gitup"

bim 1 ubuntu-16.04-v5-ntp == "imaging.sh common-setup-user-env"
bim 2 ubuntu-16.04-v5-ntp u16-lowlat47 "imaging.sh ubuntu-k47-lowlatency"
bim 3 u16-lowlat47 oai16-gw-base "oai-gw.sh image"
bim 4 u16-lowlat47 oai16-enb-base "oai-enb.sh image"

### running apt-upgrade-all in unattended mode obviously
# requires more work
# try to run apt-upgrade-all on ubuntu-16
# bim fit06 ubuntu-16.04 u16-upgrade "nodes.sh apt-upgrade-all"

exit

####################
# same on ubuntu-14.04 + node-env
#bim fit02 ubuntu-14.04-v3-stamped ubuntu-14.04-v4-ntp-node-env \
#  "imaging.sh ubuntu-setup-ntp" \
#  "imaging.sh common-setup-user-env" \
#  "imaging.sh common-setup-node-ssh-key" \
#  "nodes.sh gitup"
bim 36 ubuntu-14.04-v4-ntp-node-env == "nodes.sh common-setup-user-env"

# same on fedora-23
#bim fit03 fedora-23-node-env fedora-23-v4-ntp \
#  "imaging.sh fedora-setup-ntp" \
#  "nodes.sh gitup"
bim 37 fedora-23-v4-ntp == "nodes.sh common-setup-user-env"


