#/bin/bash

gitroot=$HOME/git/r2lab

###
build=$gitroot/rhubarbe-images/build-image.py
gateway=root@faraday.inria.fr

cd $gitroot/infra/user-env

alias b="$build $gateway -i oai-common.sh -i nodes.sh -i common.sh"

##########
# the base for OAI images is as follows

# build for OAI gateway
# oai1609-gw-base is a ubuntu-16 with mysql and phpadmin installed
# these 2 cannot be properly scripted because of the prompting for passwords
b fit04 ubuntu-16.04 oai16-gw-base "oai-gw.sh image" 
b fit05 ubuntu-14.04 oai14-gw-base "oai-gw.sh image" 
