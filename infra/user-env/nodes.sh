# set of convenience tools to be used on the nodes
# 
# we start with oai-oriented utilities
# on these images, we have a symlink
# /root/.bash_aliases
# that point at
# /root/r2lab/infra/userenv/nodes.sh
# 
#

unalias ls 2> /dev/null

########## micro doc tool
_help_message=""

function doc-fun () {
  fun=$1; shift;
  docstring=$1; shift
  [ "$docstring" == 'alias' ] && docstring=$(alias $fun)
  [ "$docstring" == 'alias1' ] && docstring="\t$(alias $fun)"
  [ "$docstring" == 'function' ] && docstring=$(type $fun)
  _help_message="$_help_message\n$fun\t$docstring"
}

function doc-sep() {
    name="$1"; shift
    if [ -z "$name" ] ; then
	_help_message="$_help_message\n---------------"
    else
	_help_message="$_help_message\n============================== $name"
    fi
} 
##########
doc-fun gitup "\tUpdate /root/r2lab from git repo (as well as OAI repos if found)"
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
doc-fun bashrc "\treload ~/.bashrc"
function bashrc() { echo "Reloading ~/.bashrc"; source ~/.bashrc; }

# update and reload
doc-fun refresh "\tgitup + bashrc"
function refresh() { gitup /root/r2lab; bashrc; }

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

doc-fun data-up "\tTurn up the data interface; returns the interface name (should be data)"
# xxx should maybe better use wait-forinterface-on-driver e1000e
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

doc-fun list-interfaces "List the current status of all interfaces"
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

doc-fun details-on-interface "\n\t\tGives extensive details on one interface"
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

doc-fun find-interface-by-driver "\n\t\treturns first interface bound to given driver"
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
doc-fun wait-for-interface-on-driver "\n\t\tlocates and waits for device bound to provided driver, returns its name"
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

doc-fun wait-for-device "Wait for device to be up or down; example: wait-for-device data up"
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

##########
# the utility to select which function the oai alias should point to
# in most cases, we just want oai to be an alias to e.g.
# /root/r2lab/infra/user-env/oai-gw.sh
# except that while developping we use the version in /tmp
# if present

# the place where the standard (git) scripts are located
oai_scripts=/root/r2lab/infra/user-env

function define-oai() {
    # suffix should be gw.sh or enb.sh
    suffix=$1; shift
    function _oai() {
	candidates="/tmp $oai_scripts"
	for candidate in $candidates; do
	    script=$candidate/oai-$suffix
	    [ -f $script ] && break;
	done
	echo Invoking script $script >&2-
	$script "$@"
    }
    alias oai=_oai
}

doc-sep

doc-fun oai-as-gw "Defines the 'oai' command to work on an oai gateway, and related env. vars"
function oai-as-gw() { define-oai gw.sh; echo function "'oai'" now defined; oai-env; }

doc-fun oai-as-gw "Defines the 'oai' command to work on an oai eNodeB, and related env. vars"
function oai-as-enb() { define-oai enb.sh; echo function "'oai'" now defined; oai-env; }

doc-fun oai-env "\tDisplays and loads env variables related to oai"
function oai-env() {
    _oai places > /tmp/oai-env
    source /tmp/oai-env
    echo "Following vars now in your env" >&2-
    echo ========== >&2-
    cat /tmp/oai-env
}

####################
doc-fun spy-sctp "expects an interface name and then runs tcpdump on the SCTP traffic"
function spy-sctp() {
    ifname=$(data-up)
    echo $spying for SCTP packets on interface $ifname
    tcpdump -i $ifname ip proto 132
}

doc-sep
#################### a utility to deal with logs and configs
function locate_logs() {
    if [[ -n "$@" ]] ; then
	echo "$@"
    elif [ -n "$logs" ]; then
	echo $logs
    else
	echo No logs defined - Please define the "'logs'" shell variable  >&2-
    fi
}
	
doc-fun logs "\tdoes ls on the logs as defined in \$logs"
function logs() {
    ls $(locate_logs "$@")
}

doc-fun configs "\tdoes ls on the config file as defined in \$conf_dir/\$config"
function configs() {
    ls $conf_dir/$config
}

doc-fun logs-tail "Runs tail -f on the logs files  (see logs)"
function logs-tail() {
    logfiles=$(locate_logs "$@")
    for logfile in $logfiles; do
	[ -f $logfile ] || { echo "Touching $logfile"; touch $logfile; }
    done
    tail -f $logfiles
}

doc-fun logs-grep "Runs grep on the logs files  (see logs)"
function logs-grep() {
    [[ -z "$@" ]] && { echo usage: $0 grep-arg..s; return; }
    logfiles=$(locate_logs)
    grep "$@" $logfiles
}

doc-fun logs-tgz "Captures logs (from \$logs) and config (from \$conf_dir/\$config) in a tgz"
function logs-tgz() {
    output=$1; shift
    [ -z "$output" ] && { echo usage: $0 output; return; }
    logfiles=$(locate_logs)
    [ -n "$config" ] && logfiles="$logfiles $conf_dir/$config"
    tar -czf $output.tgz $logfiles
    echo "Captured logs (and config) in $output.tgz"
}    

### do not document : a simple utlity for the oai*.sh stubs
function define_main() {
    function main() {
	if [[ -z "$@" ]]; then
	    help
	fi
	subcommand="$1"; shift
	case $subcommand in
	    env)
		echo "Use oai-env; not oai env" ;;
	    *)
		$subcommand "$@" ;;
	esac
    }
}

function help() { echo -e $_help_message; }
