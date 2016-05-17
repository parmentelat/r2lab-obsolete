# nominally we'd like to use the data network
# however this is not available on bemol so for now
# we switch to using control
# should not be a big deal..
oai_realm="r2lab.fr"
oai_ifname=control
oai_subnet=3


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

doc-fun ltail "logs-tail"
function ltail() {
    logs-tail
}

doc-fun ldump "expects one arg - logs-tgz under proper name based on \$oai_role"
function ldump() {
    logs-tgz $1-${oai_role}
}

doc-fun spy-sctp "tcpdump the SCTP traffic on interface ${oai_ifname} - with one arg, stores into a .pcap"
function spy-sctp() {
    local output="$1"; shift
    local args=""
    [ -n "$output" ] && args="-w ${output}-${oai_role}.pcap"
    command="tcpdump -i ${oai_ifname} ip proto 132 $args"
    echo Running $command
    $command
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
    echo "running as a $suffix"
    echo "peer=$(get-peer)"
}

doc-sep
