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

# augment ubuntu-16.04 with ntp
bim fit01 ubuntu-16.04-v4-node-env ubuntu-16.04-v5-ntp \
  "imaging.sh ubuntu-setup-ntp" \
  "nodes.sh gitup"

# same on ubuntu-14.04 + node-env
bim fit02 ubuntu-14.04-v3-stamped ubuntu-14.04-v4-ntp-node-env \
  "imaging.sh ubuntu-setup-ntp" \
  "imaging.sh common-setup-user-env" \
  "imaging.sh common-setup-node-ssh-key" \
  "nodes.sh gitup"

# same on fedora-23
bim fit03 fedora-23-node-env fedora-23-v4-ntp \
  "imaging.sh fedora-setup-ntp" \
  "nodes.sh gitup"

# create base image for OAI gateway (infra) on ubuntu-16
bim fit04 ubuntu-16.04 oai16-gw-base "oai-gw.sh image" 

# create base image for OAI gateway (infra) on ubuntu-14
bim fit05 ubuntu-14.04 oai14-gw-base "oai-gw.sh image" 

# try to run apt-upgrade-all on ubuntu-16
bim fit06 ubuntu-16.04 u16-upgrade "nodes.sh apt-upgrade-all"
