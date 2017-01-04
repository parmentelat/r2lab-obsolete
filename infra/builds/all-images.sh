#/bin/bash

case $(hostname) in
    faraday*)
	gateway=localhost
	gitroot=/root/r2lab
	;;
    *)
	gateway=inria_r2lab.tutorial@faraday.inria.fr
	gitroot=$HOME/git/r2lab
	;;
esac

###
bi=$(dirname $0)/build-image.py

# we don't need all these includes everywhere but it makes it easier
function bim () {
    command="$bi $gateway -p $gitroot/infra/user-env -i oai-common.sh -i nodes.sh -i r2labutils.sh"
    echo $command "$@"
    $command --silent "$@"
}

# when run with an arg : just print the command to run manually
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
    bim 1 ubuntu-16.04-gnuradio-3.7.10.1-update3 ubuntu-16.04-gnuradio-3.7.10.1-update4 "nodes.sh git-pull-r2lab"
}

function update-root-bash() {
    bim 1 ubuntu-16.04-v5-ntp ubuntu-16.04-v6-user-env "imaging.sh common-setup" "nodes.sh git-pull-r2lab" &
    bim 2 ubuntu-14.04-v5-ntp ubuntu-14.04-v6-user-env "imaging.sh common-setup" "nodes.sh git-pull-r2lab" &
    bim 3 fedora-23-v4-ntp fedora-23-v6-user-env       "imaging.sh common-setup" "nodes.sh git-pull-r2lab" &
    bim 5 intelcsi-node-env intelcsi-v3-user-env       "imaging.sh common-setup" "nodes.sh git-pull-r2lab" &
    bim 6 ubuntu-16.04-gnuradio-3.7.10.1-update4    \
          ubuntu-16.04-gnuradio-3.7.10.1-v5-user-env   "imaging.sh common-setup" "nodes.sh git-pull-r2lab" &
}

# preserving the oai images for now
function redo-netnames() {
    bim 1  ubuntu-16.04 ubuntu-16.04-v10-wireless-names "imaging.sh network-names-udev" &
    bim 2  ubuntu-14.04 ubuntu-14.04-v10-wireless-names "imaging.sh network-names-udev" &
    bim 3  fedora-23    fedora-23-v10-wireless-names "imaging.sh network-names-udev" &
    bim 5  gnuradio     ubuntu-16.04-gnuradio-3.7.10.1-v10-wireless-names "imaging.sh network-names-udev" &
    bim 11 intelcsi     intelcsi-v10-wireless-names "imaging.sh network-names-udev" &
}

########## template
function template() {
    bim 1 ubuntu-16.04	ubuntu-16.04-vx-some-name			"imaging.sh some-function" &
    bim 2 ubuntu-14.04  ubuntu-14.04-vx-some-name			"imaging.sh some-function" &
    bim 3 fedora-23	fedora-23-vx-some-name				"imaging.sh some-function" &
    bim 5 gnuradio	ubuntu-16.04-gnuradio-3.7.10.1-vx-some-name	"imaging.sh some-function" &
    # these ones have a USRP
    bim 11 intelcsi	intelcsi-vx-some-name				"imaging.sh some-function" &
    # leave the OAI images for now, as we should redo them based on one of the above
}

function node-keys() {
    bim 1 ubuntu-16.04	ubuntu-16.04-v9-node-keys			"imaging.sh common-setup-node-ssh-key" &
    bim 2 ubuntu-14.04  ubuntu-14.04-v9-node-keys			"imaging.sh common-setup-node-ssh-key" &
    bim 3 fedora-23	fedora-23-v9-node-keys				"imaging.sh common-setup-node-ssh-key" &
    bim 5 gnuradio	ubuntu-16.04-gnuradio-3.7.10.1-v9-node-keys	"imaging.sh common-setup-node-ssh-key" &
    # these ones have a USRP
    bim 11 intelcsi	intelcsi-v9-node-keys				"imaging.sh common-setup-node-ssh-key" &
    # leave the OAI images for now, as we should redo them based on one of the above
}

function ubuntu-udev() {
#    bim 1  ubuntu-16.04 ubuntu-16.04-v8-wireless-names "imaging.sh ubuntu-udev" &
#    bim 2  ubuntu-14.04 ubuntu-14.04-v8-wireless-names "imaging.sh ubuntu-udev" &
#    bim 3  fedora-23    fedora-23-v8-wireless-names "imaging.sh ubuntu-udev" &
    bim 5  gnuradio     ubuntu-16.04-gnuradio-3.7.10.1-v8-wireless-names "imaging.sh ubuntu-udev" &
    bim 11 intelcsi     intelcsi-v8-wireless-names "imaging.sh ubuntu-udev" &
}

# preserving the oai images for now
# also stay away from node 4 that is prone to mishaps
function  update-v11() {
    # update OS packages on vanilla images only
    bim 1 ubuntu-16.04-v10-wireless-names \
	ubuntu-16.04-v11-os-update	"nodes.sh git-pull-r2lab" "nodes.sh update-os-packages" &
    bim 2 ubuntu-14.04-v10-wireless-names \
	ubuntu-14.04-v11-os-update	"nodes.sh git-pull-r2lab" "nodes.sh update-os-packages" &
    bim 3 fedora-23-v10-wireless-names \
	fedora-23-v11-os-update		"nodes.sh git-pull-r2lab" "nodes.sh update-os-packages" &
    bim 5 intelcsi-v10-wireless-names \
	intelcsi-v11-os-update		"nodes.sh git-pull-r2lab" "nodes.sh update-os-packages" &
    bim 6 ubuntu-16.04-gnuradio-3.7.10.1-v10-wireless-names \
          gnuradio-v11-os-packages	"nodes.sh git-pull-r2lab" "nodes.sh update-os-packages" &
}

# seems to have worked except for nodes
# 1 : ubuntu-16.04-v10-wireless-names.log - which is odd because it seemed to have worked manually
# 8 : gnuradio-3.7.10.1-v11-os-packages.log
update-v11

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
#0#  "nodes.sh git-pull-r2lab"

#bim 36 ubuntu-14.04-v4-ntp-node-env == "nodes.sh common-setup-user-env"

# same on fedora-23
#0#bim fit03 fedora-23-node-env fedora-23-v4-ntp \
#0#  "imaging.sh fedora-setup-ntp" \
#0#  "nodes.sh git-pull-r2lab"

#bim 37 fedora-23-v4-ntp == "nodes.sh common-setup-user-env"
