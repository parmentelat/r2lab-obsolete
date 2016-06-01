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


### do not document : a simple utlity for the oai*.sh stubs
function define_main() {
    function main() {
	if [[ -z "$@" ]]; then
	    help
	    return
	fi
	subcommand="$1"; shift
	# accept only subcommands that match a function
	case $(type -t $subcommand) in
	    function)
		$subcommand "$@" ;;
	    *) 
		echo "$subcommand not a function - exiting" ;;
	esac
    }
}

function run-in-log() {
    local log=$1; shift
    local command="$@"
    echo ===== $command
    $command 2>&1 | tee $log
}

doc-fun logs "tail-logs"
function logs() {
    tail-logs
}
doc-fun capture "expects one arg - capture logs and datas and configs under provided name, suffixed with -\$oai_role"
function capture() {
    capture-all $1-${oai_role}
}

doc-fun sctp "tcpdump the SCTP traffic on interface ${oai_ifname} - with one arg, stores into a .pcap"
function sctp() {
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
doc-fun prepare " = init + build + configure"
function prepare() {
    init
    build
    configure
}

doc-sep
