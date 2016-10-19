source $(dirname $(readlink -f $BASH_SOURCE))/nodes.sh

# this is included (i.e. source'd) from places that all have
# included nodes.sh
# so in this context we have done 
# create-doc-category nodes
# and so doc-nodes and doc-nodes-sep are available

# nominally we'd like to use the data network
# however this is not available on bemol so for now
# we switch to using control
# should not be a big deal..
oai_realm="r2lab.fr"
oai_ifname=data
oai_cn_branch=unstable

case ${oai_ifname} in
    control)
	oai_subnet=3 ;;
    data)
	oai_subnet=2 ;;
    *)
	echo "ERROR cannot set oai_subnet" ;;
esac

####################
function run-in-log() {
    local log=$1; shift
    local command="$@"
    echo ===== $command
    $command 2>&1 | tee $log
}

doc-nodes logs "tail-logs"
function logs() {
    tail-logs
}

####################
doc-nodes capture "expects one arg - capture logs and datas and configs under provided name, suffixed with -\$oai_role"
function capture() { capture-all "$1"-${oai_role}; }

function capture-hss() { oai-as-hss; capture-all "$1"-hss; }
function capture-epc() { oai-as-epc; capture-all "$1"-epc; }
function capture-enb() { oai-as-enb; capture-all "$1"-enb; }
function capture-scr() { oai-as-enb; capture-all "$1"-scr; }

####################
### get git to accept using eurecom's certificates
# option 1: manually fetch the certificate and store it in /etc/ssl
# this however is fragile, we found on ubuntu14 that
# the change could get lost; not 100% clear how, but maybe
# some package installed later on (which one?) is overwriting the global certs
function git-ssl-fetch-eurecom-certificates() {
    echo -n | \
	openssl s_client -showcerts -connect gitlab.eurecom.fr:443 2>/dev/null | \
	sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' \ 
	    >> /etc/ssl/certs/ca-certificates.crt
    echo "Added Eurecom gitlab certificates here:"
    ls -l  /etc/ssl/certs/ca-certificates.crt
}

# this looks more robust even if a bit less secure
# but we don't care that much anyways 
function git-ssl-turn-off-verification() {
    git config --global --add http.sslVerify false
}

####################
# designed for interactive usage; tcpdump stops upon Control-C
doc-nodes tcpdump-sctp "interactive tcpdump of the SCTP traffic on interface ${oai_ifname}
		with one arg, stores into a .pcap"
function tcpdump-sctp() {
    local output="$1"; shift
    command="tcpdump -i ${oai_ifname} ip proto 132"
    [ -n "$output" ] && {
	local file="${output}-${oai_role}.pcap"
	echo "Capturing (unbuffered) into $file"
	command="$command -w $file -U"
    }
    echo Running $command
    $command
}

##############################
function -manage-processes() {
    # use with list or stop
    mode=$1; shift
    pids="$@" 
    if [ -z "$pids" ]; then
	echo "========== No running process"
	return 1
    fi
    echo "========== Found processes"
    ps $pids
    if [ "$mode" == 'stop' ]; then
	echo "========== Killing $pids"
	kill $pids
	echo "========== Their status now"
	ps $pids
	if [ -n "$locks" ]; then
	    echo "========== Clearing locks $locks"
	    rm -f $locks
	fi
	
    fi
}

function status() { -manage-processes status $(-list-processes); }
function stop()   { -manage-processes stop   $(-list-processes); }

##########
doc-nodes restart " = stop [+ sleep] + start; give delay as arg1 - defaults to 1"
function restart() {
    delay=$1; shift
    [ -z "$delay" ] && delay=1
    stop
    echo ===== sleeping for $delay seconds
    sleep $delay
    start
}

##########
doc-nodes-sep

########################################
define-main "$0" "$BASH_SOURCE" 
main "$@"
