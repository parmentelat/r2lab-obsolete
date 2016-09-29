#/bin/bash

gitroot=$HOME/git/r2lab

###
build=$gitroot/rhubarbe-images/build-image.py
gateway=root@faraday.inria.fr

cd $gitroot/infra/user-env

# ew don't need all this but it makes it easier
alias b="$build $gateway -i oai-common.sh -i nodes.sh -i common.sh"

# augment ubuntu-16.04 with ntp
b fit01 ubuntu-16.04-v4-node-env ubuntu-16.04-v5-ntp \
  "imaging.sh ubuntu-setup-ntp"

# same on ubuntu-14.04 + node-env
b fit02 ubuntu-14.04-v3-stamped ubuntu-14.04-v4-ntp-node-env \
  "imaging.sh ubuntu-setup-ntp" \
  "imaging.sh common-setup-user-env" \
  "imaging.sh common-setup-node-ssh-key"


# same on fedora-23
b fit03 fedora-23-node-env fedora-23-v4-ntp \
  "imaging.sh fedora-setup-ntp" \
