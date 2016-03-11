#!/bin/bash
#
### angle-measure.sh
#
# Usage:
#
# angle-measure.sh init-server channel bandwidth
# e.g. channel=64
# e.g. bandwidth=HT20 (for 20MHz)
#
# angle-measure.sh init-client channel bandwidth
# ditto
#
# angle-measure.sh run-server
#
# angle-measure.sh run-client

set -x

# http://unix.stackexchange.com/questions/41817/linux-how-to-find-the-device-driver-used-for-a-device/225496#225496?newreg=c865c93607124e70b9f530f2733aba05
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

# actually returns first interface using a given driver
# prints interface name on stdout
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
function wait-for-interface-on-driver() {
    driver=$1; shift
    while true; do
	# use the first device that runs on iwlwifi
	_found=$(find-interface-by-driver $driver)
	if [ -n "$_found" ]; then
	    >&2 echo Using wlan device $_found
	    echo $_found
	    return
	else
	    >&2 echo "Waiting for some interface to run on driver $driver"; sleep 1
	fi
    done
}

# wait for device dev to be in state wait_state
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
    
function init-server() {
    ### 2 arguments are required
    channel=$1; shift       # e.g. 64
    bandwidth=$1; shift     # e.g. HT20 

    # unload any wireless driver 
    # useful when the experiment is restarted
    modprobe -r iwlwifi mac80211 cfg80211
    # load our driver
    modprobe iwlwifi debug=0x40000

#    list-interfaces
    
    wlan=$(wait-for-interface-on-driver iwlwifi)

    # create the monitor interface
    iw dev $wlan interface add mon0 type monitor
    # bring it up
    ip link set dev mon0 up
    # init monitor interface
    iw mon0 set channel $channel $bandwidth

    ### define the number of Space time streams and the number of Antenna for transmission
    # original was using tee to broadcast on any number of files
    txs=$(find /sys -name monitor_tx_rate)
    for tx in $txs; do
	echo tweaking $tx
	echo 0x4101 > $tx
    done
}

function init-client() {
    ### 2 arguments are required
    channel=$1; shift       # e.g. 64
    bandwidth=$1; shift     # e.g. HT20 

    modprobe -r iwlwifi mac80211 cfg80211
    modprobe iwlwifi connector_log=0x1

    wlan=$(wait-for-interface-on-driver iwlwifi)

    while true; do
	iwconfig $wlan mode monitor && break # >&/dev/null
	sleep 1
    done

    # turn on 
    ip link set $wlan up
    # set on same channel
    iw $wlan set channel $channel $bandwidth
}

# just a wrapper around the individual functions
function main() {
    command=$1; shift
    case $command in
	init-server|init-client|run-server|run-client)
	    $command "$@" ;;
	*) echo unknown command \"$command\" ;;
    esac
}

main "$@"
   
