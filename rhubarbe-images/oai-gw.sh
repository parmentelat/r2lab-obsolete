#!/bin/bash

available_subcommands=""

available_subcommands="$available_subcommands base"
function base() {

    echo "========== Installing mysql-server - select apache2 and set password=linux"
    read _
    apt-get install -y mysql-server

    echo "========== Installing phpmyadmin - provide mysql-server password as linux and set password=admin"
    apt-get install -y phpmyadmin

    echo "========== Running git clone for openair-cn and r2lab"
    read _
    cd
    echo -n | \
	openssl s_client -showcerts -connect gitlab.eurecom.fr:443 2>/dev/null | \
	sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' >> \
	    /etc/ssl/certs/ca-certificates.crt
    git clone https://gitlab.eurecom.fr/oai/openair-cn.git
    # this is probably useless, but well
    git clone https://github.com/parmentelat/r2lab.git

    echo "========== Setting up cpufrequtils"
    apt-get install -y cpufrequtils
    echo 'GOVERNOR="performance"' > /etc/default/cpufrequtils
    update-rc.d ondemand disable
    /etc/init.d/cpufrequtils restart
    # this seems to be purely informative ?
    cd
    cpufreq-info > cpufreq.info

    echo "========== Done - save image in oai-epc+hss-base"
}

available_subcommands="$available_subcommands gitup"
function gitup() {
    here=$(pwd)
    echo "========== Pulling git repos"
    cd /root/openair-cn
    git pull

    cd /root/r2lab
    git pull
    cd $here
}

available_subcommands="$available_subcommands build"
function build() {
    
    gitup
    cd /root/openair-cn/SCRIPTS
    echo "========== Building HSS"
    ./build_hss -i 2>&1 | tee build_hss.log
    echo "========== Building EPC"
    ./build_epc -i 2>&1 | tee build_epc.log

    echo "========== Done - save image in oai-epc+hss-builds"
}

available_subcommands="$available_subcommands configure"
function configure {

    gitup
    # when hostname is correctly e.g. fit16
    fitid=$(hostname)
    id=$(sed -e s,fit,, <<< $fitid)
    origin=hostname
    if [ "$fitid" == "$id" ]; then
	# sample output
	#inet 192.168.3.16/24 brd 192.168.3.255 scope global control
	id=$(ip addr show control | \
		    grep 'inet '| \
		    awk '{print $2;}' | \
		    cut -d/ -f1 | \
		    cut -d. -f4)
	fitid=fit$id
	origin="ip addr show"
	echo "Forcing hostname to be $fitid"
	hostname $fitid
    fi
    echo "Using id=$id and fitid=$fitid - from $origin"

    echo "========== Turning on the data interface"
    ifup data
    echo "========== Refreshing the depmod index"
    depmod -a
    if grep -q $fitid /etc/hosts; then
	echo $fitid already in /etc/hosts
    else
	echo "========== Defining $fitid in /etc/hosts"
	echo "127.0.1.1  $fitid.r2lab.fr $fitid" >> /etc/hosts
    fi

    cd /root/openair-cn/BUILD/EPC/
    echo "========== Checking for distrib file epc.conf.in.distrib"
    [ -f epc.conf.in.distrib ] || cp epc.conf.in epc.conf.in.distrib
    echo "========== Patching config file"
    sed -e s,xxx,$id,g <<EOF > epc-r2lab.sed
s,eth0:1 *,data,g
s,192.170.0.1/24,192.168.2.xxx/24,g
s,eth0:2 *,data,g
s,192.170.1.1/24,192.168.2.xxx/24,g
s,eth0,data,g
s,192.168.12.17/24,192.168.2.xxx/24,g
s,127.0.0.1:5656,/root/openair-cn/SCRIPTS/run_epc.out,g
EOF
    sed -f epc-r2lab.sed epc.conf.in.distrib > epc.conf.in

    echo "========== Rebuilding hss and epc configs"
    cd /root/openair-cn/SCRIPTS
    ./build_hss --clean --clean-certificates --local-mme --fqdn fit$fitid.r2lab.fr 2>&1 | tee build_hss-run2.log
    ./build_epc --clean --clean-certificates --local-hss 2>&1 | tee build_epc.run2.log
}

available_subcommands="$available_subcommands start"
function start() {
    cd /root/openair-cn/SCRIPTS
    echo "In $(pwd)"
    echo "Running run_epc in background"
    # --gdb is a possible additional option here
    ./run_epc --set-nw-interfaces --remove-gtpu-kmodule >& run_epc.log &
    echo "Running run_hss in background"
    ./run_hss >& run_hss.log &
}

function _manage() {
    # if $1 is 'stop' then the found processes are killed
    mode=$1; shift
    pids=$(pgrep run_)
    if [ -z "$pids" ]; then
	echo "No running process in run_ - exiting"
	return 1
    fi
    echo "Found processes"
    ps $pids
    if [ "$mode" == 'stop' ]; then
	echo "Killing $pids"
	kill $pids
	echo "Their status now"
	ps $pids
    fi
}

available_subcommands="$available_subcommands status"
function status() { _manage; }
available_subcommands="$available_subcommands stop"
function stop() { _manage stop; }

available_subcommands="$available_subcommands log"
function log() {
    cd /root/openair-cn/SCRIPTS
    targets="run_epc.log run_epc.out run_hss.log"
    for target in $targets; do [ -f $target ] || touch $target; done
    tail -f $targets
    cd -
}

####################
function main() {
    if [[ -z "$@" ]]; then
	echo "========== Available subcommands $available_subcommands"
    fi
    for subcommand in "$@"; do
	echo "========== Running stage $subcommand"
	$subcommand
    done
}

########################################
main "$@"
