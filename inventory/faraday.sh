unalias ls 2> /dev/null

########## pseudo docstrings
_doc_nodes="#################### commands that work on a selection of nodes"
_doc_alt="#################### other commands"
_doc_admin="#################### admin commands"

function doc-nodes () {
  fun=$1; shift;
  docstring=$1; shift
  [ "$docstring" == 'alias' ] && docstring=$(alias $fun)
  [ "$docstring" == 'function' ] && docstring=$(type $fun)
  _doc_nodes="$_doc_nodes\n$fun\t$docstring"
}

function doc-alt () {
  fun=$1; shift;
  docstring=$1; shift
  [ "$docstring" == 'alias' ] && docstring=$(alias $fun)
  _doc_alt="$_doc_alt\n$fun\t$docstring"
}

function doc-admin () {
  fun=$1; shift;
  docstring=$1; shift
  [ "$docstring" == 'alias' ] && docstring=$(alias $fun)
  _doc_admin="$_doc_admin\n$fun\t$docstring"
}

function help-nodes () { echo -e $_doc_nodes; }
function help-alt () { echo -e $_doc_alt; }
function help () { help-nodes; help-alt; }
function help-admin () { echo -e $_doc_admin; }
doc-alt help-admin "list admin-oriented commands"
function help-all () { help; help-admin; }
doc-admin help-all "list all known commands : help + help-admin"

#################### contextual data
function bemol () { hostname | grep -q bemol; }

control_dev=control

function igmp-watch () {
    set -x
    tcpdump -i $control_dev igmp
    set +x
}
doc-admin igmp-watch "tcpdump igmp packets on the $control_dev interface"

####################
#### some stuff is just too hard / too awkward in shell...
# py normalize fit 1 03 fit09 
# py ranges 1-37-2 ~1-20-4
function py () {
    python3 - "$@" << EOF
import sys
def host_pxe(nodename):
    import subprocess
    try:
        dnsmasq = subprocess.check_output(['grep', nodename, '/etc/dnsmasq.d/testbed.conf'],
                                          universal_newlines=True)
        return dnsmasq.split(',')[1].replace(':', '-')
    except:
        pass
    try:
        arp = subprocess.check_output(['arp', nodename], universal_newlines=True)
        mac = arp.split('\n')[1].split()[2].replace(':', '-')
        return mac
    except:
        return ""

# XXX todo : apparently the first strategy here does not work as it should
def pxe_host(pxe):
    import subprocess
    bytes = pxe.split('-')
    if len(bytes) == 7: 
        bytes = bytes[1:]
    mac = ':'.join(bytes)
    try:
        dnsmasq = subprocess.check_output(['grep', mac, '/etc/dnsmasq.d/testbed.conf'],
					  universal_newlines=True)
        fields = dnsmasq.strip().split(',')
        return "{} ({})".format(fields[2], fields[3])
    except:
        pass
    try:
        arp = subprocess.check_output(['arp', '-a'], universal_newlines=True)
        for line in arp.split('\n'):
            try:
                args = line.split(' ')
                if args[3] == mac:
                    return "{hn} ({ip})".format(hn=args[0], ip=args[1])
            except:
                continue
        return "unknown-MAC"
    except:
        return "unknown-MAC"

def _rangetoset(rngspec):
    "translate something like 1-12 into a set"
    if ',' in rngspec:
        result = set()
        for part in rngspec.split(','):
            result |= _rangetoset(part)
        return result
    if rngspec.count('-') == 0:
        return set( [ int(rngspec) ] )
    elif rngspec.count('-') == 1:
        low, high = [ int(x) for x in rngspec.split('-') ]
        step = 1
    elif rngspec.count('-') == 2:
        low, high, step = [ int(x) for x in rngspec.split('-') ]
    else:
        sys.stderr.write("rangetoset: {} not understood\n".format(rngspec))
        return set()
    return set(range(low, high + 1, step))

def _ranges(*rngspecs):
#    print('_ranges',rngspecs)
    numbers = set()
    for rngspec in rngspecs:
        if rngspec.startswith('~'):
            numbers -= _rangetoset(rngspec[1:])
        else:
            numbers |= _rangetoset(rngspec)
    return sorted(list(numbers))

def ranges (*rngspecs):
#    print('ranges', rngspecs)
    return " ".join( [ "{:02d}".format(arg) for arg in _ranges(*rngspecs) ] )

def _normalize (sep, *args):
#    print('normalize', args)
    constant = args[0]
    rngspecs = [ arg.replace(constant, "") for arg in args[1:] if arg ]
    return sep.join( [ "{}{:02d}".format(constant, arg) for arg in _ranges(*rngspecs) ] )

def normalize (*args):
    return _normalize(' ', *args)

def comma_normalize (*args):
    return _normalize(',', *args)

# normalize2 fit reboot 1-3 fit04 reboot05 -> 
def normalize2 (*args):
#    print('normalize', args)
    constant = args[0]
    output = args[1]
    rngspecs = [ arg.replace(constant, "").replace(output, "") for arg in args[2:] if arg ]
    return " ".join( [ "{}{:02d}".format(output, arg) for arg in _ranges(*rngspecs) ] )

def main():
    _ = sys.argv.pop(0)
    command = sys.argv.pop(0)
    args = sys.argv
    function = globals()[command]
    print(function(*args))

main()
EOF
}

# normalization
# the intention is you can provide any type of inputs, and get the expected format
# norm 1 03 fit04 5-8 ~7 -> fit01 fit03 fit04 fit05 fit06 fit08
function norm () { py normalize fit "$@" ; }
# norm 1 03 fit04 -> fit01,fit03,fit04
function cnorm () { py comma_normalize fit "$@" ; }
# normreboot 1 03 fit04 reboot05 -> reboot01 reboot03 reboot04 reboot05
function normreboot () { py normalize2 fit reboot "$@" ; }

# set and/or show global NODES var
# nodes
# -> show NODES
# nodes 1 3 5
# -> set NODES to fit01 fit03 fit05 and display it too
function nodes () {
    [ -n "$1" ] && export NODES=$(norm "$@")
    echo "export NODES=\"$NODES\""
    echo "export NBNODES=$(nbnodes)"
}
doc-nodes nodes "\tshow or define currently selected nodes; eg nodes 1-10,12 13 ~5"


function nbnodes () {
    [ -n "$1" ] && nodes="$@" || nodes="$NODES" 
    echo $(for node in $nodes; do echo $node; done | wc -l)
}

# add to global NODES
# nodes_add 4 12-15 fit33
function nodes-add () {
    export NODES="$(norm $NODES $@)"
    nodes
}
alias n+=nodes-add
doc-nodes nodes-add "(alias n+) add nodes to current selection"
function nodes-sub () {
    subspec=""
    for rngspec in "$@"; do
	subspec="$subspec ~$rngspec"
    done
    export NODES="$(norm $NODES $subspec)"
    nodes
}
alias n-=nodes-sub
doc-nodes nodes-sub "(alias n-) remove nodes from current selection"

# snapshot current set of nodes for later
# nodes_save foo
function nodes-save () {
    name=$1; shift
    export NODES$name="$NODES"
    echo "Saved NODES$name=$NODES"
}
doc-alt nodes-save "name current selection"

# nodes-restore foo : goes back to what NODES was when you did nodes-save foo
function nodes-restore () {
    name=$1; shift
    preserved=NODES$name
    export NODES="${!preserved}"
    nodes
}
doc-alt nodes-restore "use previously named selection"

bemol && export _all_nodes=38-42 || export _all_nodes=1-37

function all-nodes () { nodes $_all_nodes; }
function nodes-all () { all-nodes; }
doc-nodes all-nodes "select all available nodes"

# releases
# -> show fedora/debian releases for $NODES
# releases 12 14
# -> show fedora/debian releases for fit12 fit14 - does not change NODES
function releases () {
    [ -n "$1" ] && nodes="$@" || nodes="$NODES" 
    for node in $(norm $nodes); do
	echo ==================== $node
	ssh root@$node "cat /etc/lsb-release /etc/fedora-release /etc/gnuradio-release 2> /dev/null | grep -i release; gnuradio-config-info --version 2> /dev/null || echo NO GNURADIO"
    done
}

alias rel=releases
doc-nodes releases "(alias rel) use ssh to display current release (ubuntu or fedora + gnuradio)"

# map command [args]
# -> run command on $NODES
# e.g. map hostname
function map () {
    [ -z "$1" ] && { echo "usage: map command [args] - map command on $NODES"; return; }
    for node in $NODES; do
	echo ==================== $node
	ssh root@$node "$@"
    done
}
doc-nodes map "\trun an ssh command on all selected nodes"

#
alias rload="rhubarbe load"
doc-nodes rload "load image (specify with -i) on selected nodes"
alias rsave="rhubarbe save"
doc-nodes rsave "save image from one node"
alias rwait="rhubarbe wait"
doc-nodes rwait "wait for nodes to be reachable through ssh"
alias rstat="rhubarbe status"
doc-nodes rstat "show if nodes are turned on or off"
alias rimages="rhubarbe images"
doc-nodes rimages "display available images"
alias rleases="rhubarbe leases"
doc-nodes rleases "display current leases"

alias load-fedora="rload -i fedora"
doc-nodes load-fedora alias
alias load-ubuntu="rload -i ubuntu"
doc-nodes load-ubuntu alias
alias load-f21="rload -i fedora-21"
doc-nodes load-f21 alias
alias load-f22="rload -i fedora-22"
doc-nodes load-f22 alias
alias load-f23="rload -i fedora-23"
doc-nodes load-f23 alias
alias load-u1410="rload -i ubuntu-14.10"
doc-nodes load-u1410 alias
alias load-u1504="rload -i ubuntu-15.04"
doc-nodes load-u1504 alias
alias load-u1510="rload -i ubuntu-15.10"
doc-nodes load-u1510 alias

function load-gr-u1410 () { load-image gnuradio-ubuntu-14.10.ndz "$@" ; }
function load-gr-u1504 () { load-image gnuradio-ubuntu-15.04.ndz "$@" ; }
function load-gr-f21 ()   { load-image gnuradio-fedora-21.ndz "$@" ; }

alias load-ubuntu=load-u1510
alias load-fedora=load-f23
alias load-gnuradio=load-gr-u1410

doc-nodes load-ubuntu "upload latest ubuntu image on all nodes"
doc-nodes load-fedora "... latest fedora image"
doc-nodes load-gnuradio "... latest recommended gnuradio image"

# utility; run curl
function -curl () {
    mode="$1"; shift
    [ -n "$1" ] && nodes="$@" || nodes="$NODES" 
    for node in $(normreboot $nodes); do
	# make sure we echo a newline even if curl returns nothing
	echo -n $node " " ; echo $(curl --silent http://$node/$mode)
    done
}

# showstatus
# display status on arguments, or $NODES if not provided
alias st="rhubarbe status"
doc-nodes st "\tshow node CMC status (rhubarbe status)"
# idem for actually doing stuff
function reset () { -curl reset "$@" ; }
doc-nodes reset "\treset node through its CMC"
function off () { -curl off "$@" ; }
doc-nodes off "\tturn off node through its CMC"
function on () { -curl on "$@" ; }
doc-nodes on "\tturn on node through its CMC"

# function 'wn' is part of the 'miscell' bash component
function wait () {
    [ -n "$1" ] && nodes="$@" || nodes="$NODES" 
    for node in $(norm $nodes); do
	wn $node
    done
}
doc-nodes wait "\twait for all nodes to respond to ping on their control interface"

# nodes-on : filter nodes that are on from args, or NODES if not provided
function show-nodes-on () {
    [ -n "$1" ] && nodes="$@" || nodes="$NODES"
    rhubarbe status $nodes | grep 'on' | cut -d: -f1 | sed -e s,reboot,fit,
}
doc-nodes show-nodes-on "display only selected nodes that are ON - does not change selection"
function focus-nodes-on () {
    nodes $(show-nodes-on)
}
doc-nodes focus-nodes-on "restrict current selection to nodes that are ON"

####################
# reload these tools
alias reload="source /home/faraday/r2lab/inventory/faraday.sh"
# git pull and then reload; not allowed to everybody
alias refresh="/home/faraday/r2lab/auto-update.sh; chown -R faraday:faraday ~faraday/r2lab; reload"
doc-alt refresh "install latest version of these utilities"

####################
# faraday has p2p1@switches and bemol has eth1 - use control_dev 
# spy on frisbee traffic
function t7000 () {
    [ -n "$1" ] && options="-c $1"
    set -x
    tcpdump $options -i $control_dev port 7000
    set +x
}
doc-admin t7000 "\ttcpdump on port 7000 on the control interface"

function nitos-restart () {
    service omf-sfa stop
    service ntrc stop
    service ntrc start
    service omf-sfa start
}
doc-admin nitos-restart "restart the omf-sfa and nitos (ntrc) services)"

function nitos-running-frisbees () {
    pids=$(pgrep frisbee)
    [ -z "$pids" ] && echo No running frisbee || ps $pids
}
doc-admin nitos-running-frisbees "\n\t\tlist running instances of the frisbee server"

function nitos-frisbee-bandwidth () {
    grep bandwidth /etc/nitos_testbed_rc/frisbee_proxy_conf.yaml
}
doc-admin nitos-frisbee-bandwidth "\n\t\tshow configured bandwidth"

####################
### utilities to switch the frisbee binaries
# not needed anymore now that we use new frisbee, but just in case
# this is to use the 'old' binaries as shipped with OMF
function pxe-old () {
#    bemol || { echo "designed for bemol only" ; return 1; }
    rsync -a /usr/sbin/frisbee-old-64 /usr/sbin/frisbee
    rsync -a /usr/sbin/frisbeed-old-64 /usr/sbin/frisbeed
    rsync -a /tftpboot/irfs-pxefrisbee.igz.old /tftpboot/irfs-pxefrisbee.igz
    echo old pxe-frisbee config
    pxe-config
}
doc-admin pxe-old "\tDO NOT USE THIS - Configure the system to use old frisbee binaries!"

# this is to use ours
function pxe-new () {
#    bemol || { echo "designed for bemol only" ; return 1; }
    rsync -a /usr/sbin/frisbee-new-64 /usr/sbin/frisbee
    rsync -a /usr/sbin/frisbeed-new-64 /usr/sbin/frisbeed
    rsync -a /tftpboot/irfs-pxefrisbee.igz.new /tftpboot/irfs-pxefrisbee.igz
    echo new pxe-frisbee config
    pxe-config
}
doc-admin pxe-new "\tDO NOT USE THIS - Configure the system to use new frisbee binaries!"

# and this lists the current config
function pxe-config () {
    ls -l /usr/sbin/frisbee* /tftpboot/irfs*
}
doc-admin pxe-config "Displays various files related to using old or new frisbee"

####################
# prepare a node to boot on the standard pxe image - or another variant
# *) 2 special forms are
# -nextboot list
# -nextboot clean
# *) otherwise when invoked with
# -nextboot foo 32-34
# this script creates a symlink to /tftpboot/pxelinux.cfg/foo
function -nextboot () {
    command="$1"; shift
    [ -n "$1" ] && nodes="$@" || nodes="$NODES" 
    for node in $(norm $nodes); do
	pxe=/tftpboot/pxelinux.cfg/"01-"$(py host_pxe $node)
	echo -n ABOUT $node " "
	case $command in
	    list)
		if [ -h $pxe ]; then
		    stat -c '%N' $pxe
		elif [ -f $pxe ]; then
		    ls -l $symlink
		else
		    echo no symlink found
		fi
		;;
	    clean)
		[ -f $pxe ] && { rm -f $pxe; echo CLEARED; } || echo absent
                ;;
            *) # specify config name as argument (e.g. the default is omf-6)
		dest=/tftpboot/pxelinux.cfg/$command
		[ -f $dest ] || { echo INVALID $dest - skipped; return; }
		[ -f $pxe ] && echo -n overwriting " "
		ln -sf $dest $pxe
		echo done
		;;
	esac
    done
}

alias nextboot-list="-nextboot list"
doc-nodes nextboot-list "display pxelinux symlink, if found"
alias nextboot-clean="-nextboot clean"
doc-nodes nextboot-clean "remove any pxelinux symlink for selected nodes"
alias nextboot-frisbee="-nextboot pxefrisbee"
doc-admin nextboot-frisbee "\n\t\tcreate pxelinux symlink so that node reboots on the pxefrisbee image"
alias nextboot-vivid="-nextboot pxevivid"
doc-admin nextboot-vivid "create pxelinux symlink so that node reboots on the vivid image - temporary"
alias nextboot-mini="-nextboot pxemini"
doc-admin nextboot-mini "create pxelinux symlink so that node reboots on the mini image - temporary"

# for double checking only
function nextboot-ll () {
    ls -l /tftpboot/pxelinux.cfg/
}
doc-admin nextboot-ll "use ll to list all pxelinux.cfg contents - for doublechecking"

# list pending next boot config files
# -nextboot list or -nextboot clean
function -nextboot-all () {
    command=$1; shift
    hex="[0-9a-f]"
    byte="$hex$hex"
    pattern=$byte
    for i in $(seq 6); do pattern=$pattern-$byte; done
    for symlink in $(ls /tftpboot/pxelinux.cfg/$pattern 2> /dev/null); do
	name=$(basename $symlink)
	hostname=$(py pxe_host $name)
	echo -n ABOUT $hostname " " 
	case $command in
	    list*)
		[ -h $symlink ] && stat -c '%N' $symlink || ls -l $symlink ;;
	    clean*)
		echo ABOUT $hostname: clearing $symlink; rm -f $symlink ;;
	esac
    done
}

function nextboot-listall () { -nextboot-all list; }
doc-alt nextboot-listall "\n\t\tlist all pxelinux symlinks" 
function nextboot-cleanall () { -nextboot-all clean; }
doc-alt nextboot-cleanall "\n\t\tremove all pxelinux symlinks" 

####################
# for now we use a different port for bemol and faraday

# mostly meant as a means to check the broker is alive and well configured
function omf-nodes() { curl -k https://localhost:12346/resources/nodes; echo; }
doc-admin omf-nodes function
function omf-leases() { curl -k https://faraday.inria.fr:12346/resources/leases; echo; }
doc-alt omf-leases function
function omf-accounts() { curl -k https://faraday.inria.fr:12346/resources/accounts; echo; }
doc-alt omf-accounts function
    
# XXX todo : a tool for turning on and off debug mode in omf6 commands
# omf-debug : says what is in action
# omf-debug on : turn it on
# omf-debug off : turn it off
function omf-debug () { echo not implemented; }

# do ssh to the first node in our list
# nodes 4
# ss -> ssh fit04
# ss 5 -> ssh fit05
# tn -> telnet fit04
#
function -do-first () {
    command="$1"; shift
    if [ -n "$1" ] ; then
	node=$(norm $1)
    else
	[ -z "$NODES" ] && { echo you need to set at least one node; return 1; }
	node=$(echo $NODES | awk '{print $1;}')
    fi
    echo "Running $command $node"
    $command $node
}
alias ss="-do-first ssh"
alias tn="-do-first telnet"

doc-nodes ss "\tEnter first selected node using ssh\n\t\targ if present is taken as a node, not a command" 
doc-nodes tn "\tEnter first selected node using telnet - ditto" 

#################### manually run a old or new frisbee server
function serve_ubuntu_old () {
    bemol || { echo "designed for bemol only"; return 1; }
    command="/root/images/frisbee-binaries-uth/frisbeed-old-64 -i 192.168.3.200 -m 224.0.0.1 -p 10000 -W 90000000 /var/lib/omf-images-6/ubuntu14.10-ext2.ndz"
    echo $command
    $command
}
function serve_ubuntu_new () {
    bemol || { echo "designed for bemol only"; return 1; }
    command="/root/images/frisbee-binaries-inria/frisbeed -i 192.168.3.200 -m 224.0.0.1 -p 10000 -W 90000000 /var/lib/omf-images-6/ubuntu14.10-ext2.ndz"
    echo $command
    $command
}

####################
alias nitos-gem-203="cd /var/lib/gems/1.9.1/gems/nitos_testbed_rc-2.0.3/lib/nitos_testbed_rc"
alias nitos-gem-204="cd /var/lib/gems/1.9.1/gems/nitos_testbed_rc-2.0.4/lib/nitos_testbed_rc"

# look at logs
alias logs-dns="tail -f /var/log/dnsmasqfit.log"
doc-admin logs-dns alias
alias logs-nitos="tail -f /var/log/upstart/ntrc*.log"
doc-admin logs-nitos alias
alias logs-omf-sfa="tail -f /var/log/upstart/omf-sfa.log"
doc-admin logs-omf-sfa alias

alias nitos-frisbeed-calls="grep frisbeed /var/log/upstart/ntrc_frisbee.log | grep command"
doc-admin nitos-frisbeed-calls "\n\t\textract previously invoked frisbeed commands from logs"

# talk to switches
function sw-c007 () { ssh switch-c007; }
function sw-data () { ssh switch-data; }
function sw-reboot () { ssh switch-reboot; }
function sw-control () { ssh switch-control; }
function ping-switches () { for i in c007 data reboot control; do pnv switch-$i; done ; }
alias sw=ping-switches
doc-admin sw "\tping all 4 faraday switches"

##########
function net-names () {
    [ -n "$1" ] && nodes="$@" || nodes="$NODES"
    nodes=$(cnorm $nodes)
    for node in $nodes; do
	ssh root@$node ip addr show | grep UP | grep -v 'lo:'
    done
}
doc-nodes net-names "display network interface names"

function chmod-private-key () {
    chmod 600 ~/.ssh/id_rsa
}
doc-alt chmod-private-key "\n\t\tChmod private key so that ssh won't complain anymore"

##########
# we had to create a crontab-oriented proper shell-script to do this in ./restart-all.sh
# to avoid code duplication we call that script here
function restart-all () {
    /root/r2lab/infra/scripts/restart-all.sh interactive
}
doc-admin restart-all "Restart all 4 services omf-sfa, ntrc, openfire and dnsmasq"

alias images="cd /var/lib/rhubarbe-images/"
doc-admin images alias

alias r2lab-users="ls -d /home/onelab.inria.r2lab*"
doc-admin r2lab-users alias

####################
# user environment

function init-user-env () {

    SLICE=$(id --user --name 2>/dev/null || id -un)

    MY_CERT=$HOME/.omf/user_cert.pem
    MY_KEY=$HOME/.ssh/id_rsa
    # turns out regular users cannot use CJ; sigh..
    #CURL_CERT="--cert $MY_CERT --key $MY_KEY"
    CURL_CERT=""
    # root user does has a plain pem with private key embedded
    if [ "$SLICE" == root ]; then
	MY_KEY=$HOME/.omf/user_cert.pkey
	CURL_CERT="--cert $MY_CERT"
    fi

    CURL="curl -k $CURL_CERT"

    CURL_JSON='-H "Accept: application/json" -H "Content-Type:application/json"'

    CJ="$CURL $CURL_JSON"

    RU=https://localhost:12346/resources/

}

init-user-env

doc-alt CURL "\tenv. variable: CURL=$CURL"
doc-alt CJ "\tenv. variable: CJ=$CJ"
doc-alt RU "\tenv. variable: RU=$RU"

function slice () {
    [ -n "$1" ] && SLICE=$1
    echo Using SLICE=$SLICE
}
doc-alt slice "\tDisplay current slice (and optionnally set it)"

function GET () {
    request=$1; shift
    $CURL $RU/$request
}
doc-alt GET "\tIssue a REST GET api call - expects one arguments like 'accounts' or 'accounts?name=onelab.inria.r2lab.admin'"

function get-my-account () { GET accounts?name=$SLICE ; }
doc-alt get-my-account "Displays current account $SLICE as obtained by REST"

ADMIN=onelab.inria.r2lab.admin

alias admin-account="su - $ADMIN"
doc-admin admin-account alias

alias logs-monitor="tail -f /var/log/monitor.log"
doc-admin logs-monitor alias

alias sidecar-log="tail -f /var/log/sidecar.log"
doc-admin sidecar-log alias

alias rhubarbe-update='pip3 install --upgrade rhubarbe; rhubarbe version'
doc-admin rhubarbe-update alias

alias pull-bashrc="su faraday /home/faraday/r2lab/auto-update.sh"
doc-admin pull-bashrc alias
