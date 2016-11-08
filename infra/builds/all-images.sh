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
build=$(dirname $0)/build-image.py

# we don't need all these includes everywhere but it makes it easier
function bim () {
    command="$build $gateway -p $gitroot/infra/user-env -i oai-common.sh -i nodes.sh -i r2labutils.sh"
    echo $command "$@"
    $command --silent "$@"
}

# run with an arg to get the command to run manually
[[ -n "$@" ]] && { bim --help; exit; }

####################
# one-shot : how we initialized the -v5-ntp images in the first place
# augment ubuntu-16.04 with ntp
#0# bim fit01 ubuntu-16.04-v4-node-env ubuntu-16.04-v5-ntp \
#0#   "imaging.sh ubuntu-setup-ntp" \
#0#   "nodes.sh gitup"

#0#  bim 6 ubuntu-14.04-v3-stamped ubuntu-14.04-v5-ntp \
#0#    "imaging.sh ubuntu-setup-ntp" \
#0#     "imaging.sh common-setup-node-ssh-key" \
#0#     "imaging.sh common-setup-user-env" \
#0#     "nodes.sh gitup"


gw_options="
    -l /root/openair-cn/SCRIPTS/build-hss-deps.log
    -l /root/openair-cn/SCRIPTS/build-mme-deps.log	
    -l /root/openair-cn/SCRIPTS/build-spgw-deps.log
    -b /root/openair-cn/BUILD/MME/BUILD/mme
    -b /root/openair-cn/BUILD/SPGW/BUILD/spgw
"

enb_options="
    -l /root/openairinterface5g/cmake_targets/build-uhd.log
    -l /root/build-uhd-ettus.log -l /root/build-oai5g.log
    -l /root/openairinterface5g/cmake_targets/log/asn1c_install_log.txt
    -l /root/openairinterface5g/cmake_targets/build-oai-1.log
    -l /root/openairinterface5g/cmake_targets/build-oai-2.log
    -l /root/openairinterface5g/cmake_targets/build-oai-3.log
    -b uhd_find_devices
    -b /root/openairinterface5g/cmake_targets/lte_build_oai/build/lte-softmodem
"

function u16-48() {
    #bim 1 ubuntu-16.04-v5-ntp == "imaging.sh common-setup-user-env"
    #bim 2 ubuntu-16.04-v5-ntp u16-lowlat48 "imaging.sh ubuntu-k48-lowlatency"
    bim $gw_options  1 u16-lowlat48 u16.48-oai-gw "oai-gw.sh image"
    bim $enb_options 2 u16-lowlat48 u16.48-oai-enb "oai-enb.sh image"
}

function u16-47() {
    #bim 1 ubuntu-16.04-v5-ntp == "imaging.sh common-setup-user-env"
    #bim 2 ubuntu-16.04-v5-ntp u16-lowlat47 "imaging.sh ubuntu-k47-lowlatency"
    bim $gw_options  3 u16-lowlat47 u16.47-oai-gw "oai-gw.sh image"
    bim $enb_options 5 u16-lowlat47 u16.47-oai-enb "oai-enb.sh image"
}

function u14-48(){
    #bim 6 ubuntu-14.04-v5-ntp == "imaging.sh common-setup-user-env"
    #bim 7 ubuntu-14.04-v5-ntp u14-lowlat48 "imaging.sh ubuntu-k48-lowlatency"
    bim $gw_options  6 u14-lowlat48 u14.48-oai-gw "oai-gw.sh image"
    ###bim $enb_options 7 u14-lowlat48 u14.48-oai-enb "oai-enb.sh image"
}

function u14-319(){
    #bim 1 ubuntu-14.04-v5-ntp u14-lowlat319 "imaging.sh ubuntu-k319-lowlatency"
    ###bim $gw_options  2 u14-lowlat48 u14.48-oai-gw "oai-gw.sh image"
    bim $enb_options 37 u14-lowlat319 u14.319-oai-enb-uhdoai "oai-enb.sh image uhd-oai" 
    #bim $enb_options 36 u14-lowlat319 u14.319-oai-enb-uhdettus "oai-enb.sh image uhd-ettus" 
}

function gnuradio(){
    bim 1 ubuntu-16.04-gnuradio-3.7.10.1-update3 ubuntu-16.04-gnuradio-3.7.10.1-update4 "nodes.sh gitup"
}

#ssh root@faraday.inria.fr rhubarbe off 1-10
#u14-48 &
#u16-48 &
#u16-47 &
#u14-319
gnuradio

### running apt-upgrade-all in unattended mode currently won't work
# and requires more work
# try to run apt-upgrade-all on ubuntu-16
# bim fit06 ubuntu-16.04 u16-upgrade "nodes.sh apt-upgrade-all"


####################
# same on ubuntu-14.04 + node-env
#0#bim fit02 ubuntu-14.04-v3-stamped ubuntu-14.04-v4-ntp-node-env \
#0#  "imaging.sh ubuntu-setup-ntp" \
#0#  "imaging.sh common-setup-user-env" \
#0#  "imaging.sh common-setup-node-ssh-key" \
#0#  "nodes.sh gitup"

#bim 36 ubuntu-14.04-v4-ntp-node-env == "nodes.sh common-setup-user-env"

# same on fedora-23
#0#bim fit03 fedora-23-node-env fedora-23-v4-ntp \
#0#  "imaging.sh fedora-setup-ntp" \
#0#  "nodes.sh gitup"

#bim 37 fedora-23-v4-ntp == "nodes.sh common-setup-user-env"


