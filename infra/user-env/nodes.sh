# set of convenience tools to be used on the nodes
# 
# we start with oai-oriented utilities
# on these images, we have a symlink
# /root/.bash_aliases
# that point at
# /root/r2lab/infra/userenv/nodes.sh
# 
#

unalias ls >& /dev/null

available=""


git_repos="/root/r2lab /root/openair-cn /root/openairinterface5g"

##########
available="$available gitup"
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
available="$available bashrc"
function bashrc() { echo "Reloading ~/.bashrc"; source ~/.bashrc; }

# update and reload
available="$available refresh"
function refresh() { gitup /root/r2lab; bashrc; }

##########
available="$available r2lab_id"
function r2lab_id() {
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

available="$available data-up"
data_ifnames="data eth1"
function data-up() {
    for ifname in $data_ifnames; do
	ip addr sh dev $ifname >& /dev/null && {
	    echo Turning on data network on interface $ifname >&2-
	    ifup $ifname >&2-
	    break
	}
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

available="$available oai-as-gw"
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
available="$available oai-as-enb"
function oai-as-enb() { define-oai enb.sh; echo function "'oai'" now defined; }
available="$available oai-as-gw"
function oai-as-gw() { define-oai gw.sh; echo function "'oai'" now defined; }

available="$available oai-env"
function oai-env() {
    _oai places > /tmp/oai-env
    source /tmp/oai-env
    echo "Following vars now in your env" >&2-
    echo ========== >&2-
    cat /tmp/oai-env
}

#################### a utility to deal with logs
function locate_logs() {
    if [ -n "$logs" ]; then
	echo $logs
    else
	echo No logs defined - Please define the "'logs'" shell variable  >&2-
    fi
}
	
available="$available logs-tail"
function logs-tail() {
    logfiles=$(locate_logs)
    for logfile in $logfiles; do [ -f $logfile ] || { echo "Touching $logfile"; touch $logfile; } done
    tail -f $logfiles
}

available="$available logs-grep"
function logs-grep() {
    [[ -z "$@" ]] && { echo usage: $0 grep-arg..s; return; }
    logfiles=$(locate_logs)
    grep "$@" $logfiles
}

available="$available logs-tgz"
function logs-tgz() {
    output=$1; shift
    [ -z "$output" ] && { echo usage: $0 output; return; }
    logfiles=$(locate_logs)
    tar -czf $output.tgz $logfiles
    echo "Captured logs in $output.tgz"
}    
####################
available="$available spy-sctp"
function spy-sctp() {
    ifname=$1; shift
    [ -z "$ifname" ] && ifname=data
    echo $spying for SCTP packets on interface $ifname
    tcpdump -i $ifname ip proto 132
}

function define_main() {
    function main() {
	if [[ -z "$@" ]]; then
	    echo "========== Available subcommands $available"  >&2-
	fi
	for subcommand in "$@"; do
	    echo "Running stage $subcommand"  >&2-
	    case $subcommand in
		env)
		    echo "Use oai-env; not oai env" ;;
		*)
		    $subcommand ;;
	    esac
	done
    }
}


function help() { echo Available commands; echo "$available"; }
