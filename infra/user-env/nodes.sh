# set of convenience tools to be used on the nodes
# 
# we start with oai-oriented utilities
# on these images, we have a symlink
# /root/.bash_aliases
# that point at
# /root/r2lab/infra/user-env/nodes.sh
# 
#

unalias ls 2> /dev/null

########## micro doc tool
_doc_nodes="#################### commands available on each r2lab node"

# sort of decorator to define the doc-* functions
# the job here is to add to one of the 3 variables
# _doc_* above, in general a single line with function name and explanation
function _doc_helper () {
    msg_varname=$1; shift
    fun=$1; shift;
    docstring="$*"
    [ "$docstring" == 'alias' ] && docstring=$(alias $fun)
    [ "$docstring" == 'function' ] && docstring=$(type $fun)
    length=$(wc -c <<< $fun)
    [ $length -ge 16 ] && docstring="\n\t\t$docstring"
    assign="$msg_varname=\"${!msg_varname}\n$fun\r\t\t$docstring\""
    eval "$assign"
}

function doc-fun()	{ _doc_helper _doc_nodes "$@"; }

function doc-sep() {
    name="$1"; shift
    if [ -z "$name" ] ; then
	_doc_nodes="$_doc_nodes\n---------------"
    else
	_doc_nodes="$_doc_nodes\n============================== $name"
    fi
} 
##########
doc-fun gitup "updates /root/r2lab from git repo (as well as OAI repos if found)"
git_repos="/root/r2lab /root/openair-cn /root/openairinterface5g"
function gitup() {
    [[ -n "$@" ]] && repos="$@" || repos="$git_repos"
    for repo in $repos; do
	[ -d $repo ] || continue;
	echo "========== Updating $repo"
	cd /root/r2lab
	git pull
	cd - >& /dev/null
    done
}

# reload this file after a gitup
doc-fun bashrc "reload ~/.bashrc"
function bashrc() { echo "Reloading ~/.bashrc"; source ~/.bashrc; }

# update and reload
doc-fun refresh "gitup + bashrc"
function refresh() { gitup /root/r2lab; bashrc; }

doc-fun init-clock "Sets date from ntp"
function init-clock() {
    type ntpdate >& /dev/null && {
	echo "Running ntpdate faraday3"
	ntpdate faraday3
    } || {
	echo "ERROR: cannot init clock - ntpdate not found"
	return 1
    }
}

doc-fun apt-update "refresh all packages with apt-get"
function apt-update() {
    apt-get update
    apt-get upgrade -y
}
##########
doc-sep

doc-fun r2lab-id "returns id in the range 01-37; adjusts hostname if needed"
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

doc-fun data-up "turn up the data interface; returns the interface name (should be data)"
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

doc-fun list-interfaces "list the current status of all interfaces"
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

doc-fun details-on-interface "gives extensive details on one interface"
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

doc-fun find-interface-by-driver "returns first interface bound to given driver"
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
doc-fun wait-for-interface-on-driver "locates and waits for device bound to provided driver, returns its name"
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

doc-fun wait-for-device "wait for device to be up or down; example: wait-for-device data up"
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

doc-sep
##########
# the utility to select which function the oai alias should point to
# in most cases, we just want oai to be an alias to e.g.
# /root/r2lab/infra/user-env/oai-gw.sh
# except that while developping we use the version in /tmp
# if present

# the place where the standard (git) scripts are located
oai_scripts=/root/r2lab/infra/user-env

# the mess with /tmp is so that scripts can get tested before they are committed
# it can be dangerous though, as nodes.sh is also loaded at login-time, so beware..

function define-oai() {
    # oai_role should be gw or epc or hss or enb
    export oai_role=$1; shift
    function _oai() {
	local candidates="/tmp $oai_scripts"
	local candidate=""
	local script=""
	for candidate in $candidates; do
	    local path=$candidate/oai-${oai_role}.sh
	    [ -f $path ] && { script=$path; break; }
	done
	[ -n "$script" ] || { echo "Cannot locate oai-${oai_role}.sh" >&2-; return; }
	echo Invoking script $script >&2-
	$script "$@"
    }
    alias oai=_oai
    alias o=_oai
}

doc-fun oai-loadvars "displays and loads env variables related to oai"
function oai-loadvars() {
    _oai dumpvars > /root/oai-vars
    source /root/oai-vars
    echo "=== Following vars now in your env" >&2-
    cat /root/oai-vars
    echo === >&2-
}


doc-fun oai-as-gw "defines the 'oai' command for a HSS+EPC oai gateway, and related env. vars"
function oai-as-gw() { define-oai gw; echo function "'oai'" now defined; oai-loadvars; }

doc-fun oai-as-hss "defines the 'oai' command for a HSS-only oai box, and related env. vars"
function oai-as-hss() { define-oai hss; echo function "'oai'" now defined; oai-loadvars; }

doc-fun oai-as-epc "defines the 'oai' command for an EPC-only oai box, and related env. vars"
function oai-as-epc() { define-oai epc; echo function "'oai'" now defined; oai-loadvars; }

doc-fun oai-as-enb "defines the 'oai' command for an oai eNodeB, and related env. vars"
function oai-as-enb() { define-oai enb; echo function "'oai'" now defined; echo role=$oai_role; oai-loadvars; }

doc-sep

#################### a utility to deal with logs and configs
# this needs to be rewritten - used in the oai-scripts
function locate_logs() {
    if [[ -n "$@" ]] ; then
	echo "$@"
    elif [ -n "$logs" ]; then
	echo $logs
    else
	echo No logs defined - Please define the "'logs'" shell variable  >&2-
    fi
}
	
doc-fun logs "does ls on the logs as defined in \$logs"
function logs() {
    ls $(locate_logs "$@")
}

doc-fun configs "does ls on the config file as defined in \$conf_dir/\$config"
function configs() {
    ls $conf_dir/$config
}

doc-fun logs-tail "runs tail -f on the logs files  (see logs)"
function logs-tail() {
    logfiles=$(locate_logs "$@")
    for logfile in $logfiles; do
	[ -f $logfile ] || { echo "Touching $logfile"; touch $logfile; }
    done
    tail -f $logfiles
}

doc-fun logs-grep "runs grep on the logs files  (see logs)"
function logs-grep() {
    [[ -z "$@" ]] && { echo usage: $0 grep-arg..s; return; }
    logfiles=$(locate_logs)
    grep "$@" $logfiles
}

doc-fun logs-tgz "captures logs (from \$logs) and config (from \$conf_dir/\$config) in a tgz"
function logs-tgz() {
    output=$1; shift
    [ -z "$output" ] && { echo usage: $0 output; return; }
    logfiles=$(locate_logs)
    [ -n "$config" ] && logfiles="$logfiles $conf_dir/$config"
    outpath=$HOME/$output.tgz
    tar -czf $outpath $logfiles
    echo "Captured logs (and config) in $outpath"
}    

doc-sep

peer_id_file=/root/peer.id
doc-fun define-peer "defines the id of a peer - stores it in $peer_id_file; e.g. define-peer 16"
# define-peer allows you to store the identity of the node being used as a gateway
# example: define-peer 16
# this is stored in file $peer_id_file
# it is required by some setups that need to know where to reach another service
function define-peer() {
    id="$1"; shift
    [ -n "$id" ] && echo $id > $peer_id_file
    echo "peer now defined as : " $(cat $peer_id_file)
}

doc-fun get-peer "retrieve the value defined with define-peer"
function get-peer() {
    if [ ! -f $peer_id_file ]; then
	echo "ERRROR: you need to run define-peer first" >&2-
    else
	echo $(cat $peer_id_file)
    fi
}

#################### debugging
doc-fun dump-dmesg "run dmesg every second and stores into /root/dmesg/dmesg-hh-mm-ss"
function dump-dmesg() {
    mkdir -p /root/dmesg
    while true; do
	dmesg > /root/dmesg/dmesg-$(date +"%H-%M-%S")
	echo -n "."
	sleep 1
    done	 
}    

doc-fun unbuf-var-log-syslog "reconfigures rsyslog to write in /var/sys/syslog unbuffered on ubuntu"
function unbuf-var-log-syslog() {
    # 
    local conf=/etc/rsyslog.d/50-default.conf
    sed --in-place -e s,-/var/log/syslog,/var/log/syslog, $conf
    service rsyslog restart
    echo "Writing to /var/log/syslog is now unbeffered"
}

doc-fun demo "set ups nodes for the skype demo - based on their id"
function demo() {
    case $(r2lab-id) in
	38)
	    oai-as-hss
	    define-peer 39 ;;
	39)
	    oai-as-epc
	    define-peer 38 ;;
	23)
	    oai-as-hss
	    define-peer 16 ;;
	16)
	    oai-as-epc
	    define-peer 23 ;;
	11)
	    oai-as-enb
	    define-peer 16 ;;
    esac
    echo "========== Demo setup on node $(r2lab-id)"
    echo "running as a ${oai_role}"
    echo "config uses peer=$(get-peer)"
    echo "using interface ${oai_ifname} on subnet ${oai_subnet}"
}

function help() { echo -e $_doc_nodes; }
