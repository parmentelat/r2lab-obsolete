# set of convenience tools to be used on the nodes
# 
# we start with oai-oriented utilities
# on these images, we have a symlink
# /root/.bash_aliases
# that point at
# /root/r2lab/infra/user-env/nodes.sh
# 
#

# use the micro doc-help tool
source $(dirname $(readlink -f $BASH_SOURCE))/r2labutils.sh

create-doc-category nodes "#################### commands available on each r2lab node"
augment-help-with nodes

####################
unalias ls 2> /dev/null

##########
doc-nodes gitup "updates /root/r2lab from git repo (as well as OAI repos if found)"
git_repos="/root/r2lab /root/openair-cn /root/openairinterface5g"
function gitup() {
    [[ -n "$@" ]] && repos="$@" || repos="$git_repos"
    for repo in $repos; do
	[ -d $repo ] || continue;
	echo "========== Updating $repo"
	cd $repo
	git reset --hard HEAD
	git pull 
	cd - >& /dev/null
    done
}

# reload this file after a gitup
doc-nodes bashrc "reload ~/.bashrc"
function bashrc() { echo "Reloading ~/.bashrc"; source ~/.bashrc; }

# update and reload
doc-nodes refresh "gitup + bashrc"
function refresh() { gitup /root/r2lab; bashrc; }

doc-nodes init-clock "Sets date from ntp"
function init-clock() {
    if type ntpdate >& /dev/null; then
	echo "Running ntpdate faraday3"
	ntpdate faraday3
    else
	echo "ERROR: cannot init clock - ntpdate not found"
	return 1
    fi
}

doc-nodes apt-upgrade-all "refresh all packages with apt-get"
function apt-upgrade-all() {
    apt-get update
    # for grub-pc
    debconf-set-selections <<< 'grub-pc	grub-pc/install_devices_disks_changed multiselect /dev/sda'
    debconf-set-selections <<< 'grub-pc	grub-pc/install_devices	multiselect /dev/sda'
    apt-get upgrade -y
}
##########
doc-nodes-sep

doc-nodes r2lab-id "returns id in the range 01-37; adjusts hostname if needed"
function r2lab-id() {
    # when hostname is correctly set, e.g. fit16
    fitid=$(hostname)
    id=$(sed -e s,fit,, <<< $fitid)
    origin="from hostname"
    if [ "$fitid" == "$id" ]; then
	# sample output
	#inet 192.168.3.16/24 brd 192.168.3.255 scope global control
	id=$(ip addr show control | \
		    grep 'inet '| \
		    awk '{print $2;}' | \
		    cut -d/ -f1 | \
		    cut -d. -f4)
	fitid=fit$id
	origin="from ip addr show"
	echo "Forcing hostname to be $fitid" >&2-
	hostname $fitid
    fi
    echo "Using id=$id and fitid=$fitid - $origin" >&2-
    echo $id
}    

doc-nodes data-up "turn up the data interface; returns the interface name (should be data)"
# should maybe better use wait-forinterface-on-driver e1000e
data_ifnames="data"
# can be used with ifname=$(data-up)
function data-up() {
    for ifname in $data_ifnames; do
	ip addr sh dev $ifname >& /dev/null && {
	    ip link show $ifname | grep -q UP || {
		echo Turning on data network on interface $ifname >&2-
		ifup $ifname >&2-
	    }
	    echo $ifname
	    break
	}
    done
}

doc-nodes list-interfaces "list the current status of all interfaces"
function list-interfaces () {
    set +x
    for f in /sys/class/net/*; do
	dev=$(basename $f)
	driver=$(readlink $f/device/driver/module)
	[ -n "$driver" ] && driver=$(basename $driver)
	addr=$(cat $f/address)
	operstate=$(cat $f/operstate)
	flags=$(cat $f/flags)
	printf "%10s [%s]: %10s flags=%6s (%s)\n" "$dev" "$addr" "$driver" "$flags" "$operstate"
    done
}

doc-nodes details-on-interface "gives extensive details on one interface"
function details-on-interface () {
    dev=$1; shift
    echo ==================== ip addr sh $dev
    ip addr sh $dev
    echo ==================== ip link sh $dev
    ip link sh $dev
    echo ==================== iwconfig $dev
    iwconfig $dev
    echo ==================== iw dev $dev info
    iw dev $dev info
}    

doc-nodes find-interface-by-driver "returns first interface bound to given driver"
function find-interface-by-driver () {
    set +x
    search_driver=$1; shift
    for f in /sys/class/net/*; do
	_if=$(basename $f)
	driver=$(readlink $f/device/driver/module)
	[ -n "$driver" ] && driver=$(basename $driver)
	if [ "$driver" == "$search_driver" ]; then
	    echo $_if
	    return
	fi
    done
}

# wait for one interface to show up using this driver
# prints interface name on stdout
doc-nodes wait-for-interface-on-driver "locates and waits for device bound to provided driver, returns its name"
function wait-for-interface-on-driver() {
    driver=$1; shift
    while true; do
	# use the first device that runs on iwlwifi
	_found=$(find-interface-by-driver $driver)
	if [ -n "$_found" ]; then
	    >&2 echo Using device $_found
	    echo $_found
	    return
	else
	    >&2 echo "Waiting for some interface to run on driver $driver"; sleep 1
	fi
    done
}

doc-nodes wait-for-device "wait for device to be up or down; example: wait-for-device data up"
function wait-for-device () {
    set +x
    dev=$1; shift
    wait_state="$1"; shift
    
    while true; do
	f=/sys/class/net/$dev
	operstate=$(cat $f/operstate 2> /dev/null)
	if [ "$operstate" == "$wait_state" ]; then
	    2>& echo Device $dev is $wait_state
	    break
	else
	    >&2 echo "Device $dev is $operstate - waiting 1s"; sleep 1
	fi
    done
}

doc-nodes-sep

##########
# the utility to select which function the oai alias should point to
# in most cases, we just want oai to be an alias to e.g.
# /root/r2lab/infra/user-env/oai-gw.sh
# except that while developping we use the version in /tmp
# if present

# the place where the standard (git) scripts are located
oai_scripts=$(dirname $(readlink -f "$BASH_SOURCE"))
#echo oai_scripts=$oai_scripts

# the mess with /tmp is so that scripts can get tested before they are committed
# it can be dangerous though, as nodes.sh is also loaded at login-time, so beware..

function oai-as() {
    # oai_role should be gw or epc or hss or enb
    export oai_role=$1; shift
    local candidates="/tmp $oai_scripts"
    local candidate=""
    local script=""
    for candidate in $candidates; do
	local path=$candidate/oai-${oai_role}.sh
	[ -f $path ] && { script=$path; break; }
    done
    [ -n "$script" ] || { echo "Cannot locate oai-${oai_role}.sh" >&2-; return; }
    source $path
}

doc-nodes oai-as-gw "load additional functions for dealing with an OAI gateway"
function oai-as-gw() { oai-as gw; }

doc-nodes oai-as-hss "defines the 'oai' command for a HSS-only oai box, and related env. vars"
function oai-as-hss() { oai-as hss; }

doc-nodes oai-as-epc "defines the 'oai' command for an EPC-only oai box, and related env. vars"
function oai-as-epc() { oai-as epc; }

doc-nodes oai-as-enb "defines the 'oai' command for an oai eNodeB, and related env. vars"
function oai-as-enb() { oai-as enb; }

doc-nodes-sep

# this will define add-to-logs and get-logs and grep-logs and tail-logs
create-file-category log
# other similar categories
create-file-category data
create-file-category config
create-file-category lock


doc-nodes ls-logs     "list (using ls) the log files defined with add-to-logs"
doc-nodes grep-logs   "run grep on logs, e.g grep-logs -i open"
doc-nodes ls-configs  "lists config files declared with add-to-configs"
doc-nodes ls-datas    "you got the idea; you have also grep-configs and similar combinations"

doc-nodes capture-all "captures logs and datas and configs in a tgz"
function capture-all() {
    output=$1; shift
    echo "++++++++++++++++++++++++++++++++++++++++"
    echo "capture-all: output = $output"
    [ -z "$output" ] && { echo usage: capture-all output; return; }
    allfiles="$(ls-logs) $(ls-configs) $(ls-datas)"
    outpath=$HOME/$output.tgz
    tar -czf $outpath $allfiles
    echo "Captured in $outpath the following files:"
    ls -l $allfiles
    echo "++++++++++++++++++++++++++++++++++++++++"
}    

doc-nodes-sep

peer_id_file=/root/peer.id
doc-nodes define-peer "defines the id of a peer - stores it in $peer_id_file; e.g. define-peer 16"
# define-peer allows you to store the identity of the node being used as a gateway
# example: define-peer 16
# this is stored in file $peer_id_file
# it is required by some setups that need to know where to reach another service
function define-peer() {
    id="$1"; shift
    [ -n "$id" ] && echo $id > $peer_id_file
    echo "peer now defined as : " $(cat $peer_id_file)
}

doc-nodes get-peer "retrieve the value defined with define-peer"
function get-peer() {
    if [ ! -f $peer_id_file ]; then
	echo "ERRROR: you need to run define-peer first" >&2-
    else
	echo $(cat $peer_id_file)
    fi
}

#################### debugging
doc-nodes dump-dmesg "run dmesg every second and stores into /root/dmesg/dmesg-hh-mm-ss"
function dump-dmesg() {
    mkdir -p /root/dmesg
    while true; do
	dmesg > /root/dmesg/dmesg-$(date +"%H-%M-%S")
	echo -n "."
	sleep 1
    done	 
}    

doc-nodes unbuf-var-log-syslog "reconfigures rsyslog to write in /var/sys/syslog unbuffered on ubuntu"
function unbuf-var-log-syslog() {
    # 
    local conf=/etc/rsyslog.d/50-default.conf
    sed --in-place -e s,-/var/log/syslog,/var/log/syslog, $conf
    service rsyslog restart
    echo "Writing to /var/log/syslog is now unbeffered"
}

#################### tcpdump
# 2 commands to start and stop tcpdump on the data interface
# output is in /root/data-<name>.pcap
# with <name> provided as a first argument (defaults to r2lab-id)
# it is desirable to set a different name on each host, so that when collected
# data gets merged into a single file tree they don't overlap each other

# Usage -start-tcpdump data|control some-distinctive-name tcpdump-arg..s
function -start-tcpdump() {
    interface="$1"; shift
    name="$1"; shift
    [ -z "$name" ] && name=$(r2lab-id)
    cd 
    pcap="${interface}-${name}.pcap"
    pidfile="tcpdump-${interface}.pid"
    command="tcpdump -n -U -w $pcap -i ${interface}" "$@"
    echo "${interface} traffic tcpdump'ed into $pcap with command:"
    echo "$command"
    nohup $command >& /dev/null < /dev/null &
    pid=$!
    ps $pid
    echo $pid > $pidfile
}
    
# Usage -stop-tcpdump data|control some-distinctive-name
function -stop-tcpdump() {
    interface="$1"; shift
    name="$1"; shift
    [ -z "$name" ] && name=$(r2lab-id)
    cd
    pcap="${interface}-${name}.pcap"
    pidfile="tcpdump-${interface}.pid"
    if [ ! -f $pidfile ]; then
	echo "Could not spot tcpdump pid from $pidfile - exiting"
    else
	pid=$(cat $pidfile)
	echo "Killing tcpdump pid $pid"
	kill $pid
	rm $pidfile
    fi
}

doc-nodes start-tcpdump-data "Start recording pcap data about traffic on the data interface"
function start-tcpdump-data() { -start-tcpdump data "$@"; }
doc-nodes stop-tcpdump-data "Stop recording pcap data about SCTP traffic"
function stop-tcpdump-data() { -stop-tcpdump data "$@"; }

####################
doc-nodes demo "set ups nodes for the skype demo - based on their id"
function demo() {
    case $(r2lab-id) in
	38)
	    oai-as-hss
	    define-peer 39
	    ;;
	39)
	    oai-as-epc
	    define-peer 38
	    ;;

	37)
	    oai-as-hss
	    define-peer 36
	    ;;
	36)
	    oai-as-epc
	    define-peer 37
	    ;;
	19)
	    oai-as-enb
	    define-peer 36
	    ;;
	11)
	    oai-as-enb
	    define-peer 36
	    ;;
    esac
    echo "========== Demo setup on node $(r2lab-id)"
    echo "running as a ${oai_role}"
    echo "config uses peer=$(get-peer)"
    echo "using interface ${oai_ifname} on subnet ${oai_subnet}"
}

# long names are tcp-segmentation-offload udp-fragmentation-offload
# generic-segmentation-offload generic-receive-offload
# plus, udp-fragmentation-offload is fixed on our nodes
doc-nodes "offload-(on|off)" "turn on or off various offload features on specified wired interface" 
function offload-off () { -offload off "$@"; }
function offload-on () { -offload on "$@"; }

function -offload () {
    mode="$1"; shift
    ifname=$1; shift
    for feature in tso gso gro ; do
	command="ethtool -K $ifname $feature $mode"
	echo $command
	$command
    done
}

doc-nodes enable-nat-data "Makes the data interface NAT-enabled to reach the outside world"
function enable-nat-data() {
    id=$(r2lab-id)
    ip route add default via 192.168.2.100 dev data table 200
    ip rule add from 192.168.2.2/24 table 200 priority 200
}

####################
doc-nodes usrp-reset "Reset the URSP attached to this node"
function usrp-reset() {
    id=$(r2lab-id)
    # WARNING this might not work on a node that
    # is not in its nominal location,
    # like if node 42 sits in slot 4
    cmc="192.168.1.$id"
    echo "Turning off USRP # $id"
    curl http://$cmc/usrpoff
    sleep 1
    echo "Turning on USRP # $id"
    curl http://$cmc/usrpon
}

doc-nodes scramble "shortcuts for scrambling the skype demo; use -blast to use max. gain"
function scramble() {
    mode=$1; shift
    command="uhd_siggen --freq=2.53G --gaussian --amplitude=0.9"
    case "$mode" in
	"")        command="$command -g 73" ; message="perturbating" ;;
	"-blast")  command="$command -g 90" ; message="blasting" ;;
	*)         echo unknown option "$mode"; return ;;
    esac
    echo "Running $command in foreground - press Enter at the prompt to exit"
    $command
}

doc-nodes watch-uplink "Run uhd_fft on band7 uplink"
function watch-uplink() {
    uhd_fft -f2560M -s 25M
}

doc-nodes watch-downlink "Run uhd_fft on band7 downlink"
function watch-downlink() {
    uhd_fft -f2680M -s 25M
}
########################################
define-main "$0" "$BASH_SOURCE"
main "$@"
