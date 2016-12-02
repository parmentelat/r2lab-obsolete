#!/bin/bash

####################
# This is our own brewed script for setting up a wifi network
# it run on the remote machine - either sender or receiver
# and is in charge of initializing a small ad-hoc network
#
# Thanks to the RunString class, we can just define this as
# a python string, and pass it arguments from python variables
#


# we expect the following arguments
# * wireless driver name (iwlwifi or ath9k)
# * the wifi network name to join
# * the wifi frequency to use

function init-ad-hoc-network (){
    driver=$1; shift
    netname=$1; shift
    freq=$1;   shift

    # load the r2lab utilities - code can be found here:
    # https://github.com/parmentelat/r2lab/blob/master/infra/user-env/nodes.sh
    source /root/r2lab/infra/user-env/nodes.sh

    ipaddr_mask=10.0.0.$(r2lab-id)/24

    turn-off-wireless
    
    echo loading module $driver
    modprobe $driver
    
    # some time for udev to trigger its rules
    sleep 1
    
    ifname=$(wait-for-interface-on-driver $driver)

    echo configuring interface $ifname
    # make sure to wipe down everything first so we can run again and again
    ip address flush dev $ifname
    ip link set $ifname down
    # configure wireless
    iw dev $ifname set type ibss
    ip link set $ifname up
    # set to ad-hoc mode
    iw dev $ifname ibss join $netname $freq
    ip address add $ipaddr_mask dev $ifname
}

function my-ping (){
    dest=$1; shift
    maxwait=$1; shift
    
    start=$(date +%s)

    while true; do
	# allow for one second timeout only; try one packet
	if ping -w 1 -c 1 $dest >& /dev/null; then
	    end=$(date +%s)
	    duration=$(($end - $start))
	    echo "SUCCESS after ${duration}s"
	    return 0
	else
	    echo "$dest not reachable"
	    end=$(date +%s)
	    duration=$(($end - $start))
	    if [ "$duration" -ge "$maxwait" ]; then
		echo "FAILURE after ${duration}s"
		return 1
	    fi
	fi
    done
}

########################################
# just a wrapper so we can call the individual functions. so e.g.
# B3-wireless.sh tracable-ping 10.0.0.2 20
# results in calling tracable-ping 10.0.0.2 20

"$@"
