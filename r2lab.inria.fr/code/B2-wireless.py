#!/usr/bin/env python3

from argparse import ArgumentParser

from asynciojobs import Scheduler

# also import the Run class
from apssh import SshNode, SshJob, Run, RunString

gateway_hostname  = 'faraday.inria.fr'
gateway_username  = 'onelab.inria.r2lab.tutorial'
gateway_key       = '~/.ssh/onelab.private'

# this time we want to be able to specify the slice on the command line
parser = ArgumentParser()
parser.add_argument("-s", "--slice", default=gateway_username,
                    help="specify an alternate slicename, default={}"
                         .format(gateway_username))
args = parser.parse_args()

# we create a SshNode object that holds the details of
# the first-leg ssh connection to the gateway

# remember to make sure the right ssh key is known to your ssh agent
faraday = SshNode(hostname = gateway_hostname, username = args.slice)

node1 = SshNode(gateway = faraday, hostname = "fit01", username = "root")
node2 = SshNode(gateway = faraday, hostname = "fit02", username = "root")

check_lease = SshJob(
    # checking the lease is done on the gateway
    node = faraday,
    # this means that a failure in any of the commands
    # will cause the scheduler to bail out immediately
    critical = True,
    command = Run("rhubarbe leases --check"),
)

####################
turn_on_wireless_script = """#!/bin/bash
# this plain bash script will run on the remote machine
# either sender or receiver
# and is in charge of initializing a small ad-hoc network

# we expect the following arguments
# 1. wireless driver name (iwlwifi or ath9k)
# 2. IP-address/mask for that interface 
# 3. the wifi network name to join
# 4. the wifi frequency to use

driver=$1; shift
ifname=$1; shift
ipaddr_mask=$1; shift
netname=$1; shift
freq=$1;   shift

# load the r2lab utilities - code can be found here:
# https://github.com/parmentelat/r2lab/blob/master/infra/user-env/nodes.sh
source /root/r2lab/infra/user-env/nodes.sh

turn-off-wireless

echo loading module $driver
modprobe $driver

# some time for udev to trigger its rules
sleep 1

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
"""
####################

#### with the Intel card
driver="iwlwifi"
ifname="intel"
#### with the Atheros card
driver="ath9k"
ifname="atheros"

# setting up the data interface on both fit01 and fit02
init_node_01 = SshJob(
    node = node1,
    required = check_lease,
    command = RunString(
        turn_on_wireless_script,
        driver, ifname, "10.0.0.1/24", "foobar", 2412,
#        verbose=True,
    ))
init_node_02 = SshJob(
    node = node2,
    required = check_lease,
    command = RunString(
        turn_on_wireless_script,
        driver, ifname, "10.0.0.2/24", "foobar", 2412))

####################
repetitive_ping_script = """#!/bin/bash
dest=$1; shift
ping_options="$@"; shift

for i in $(seq 20); do
    echo -n $(date +%H:%M:%S) TEST $i " "
    if ping -c1 -W1 $ping_options $dest >& /dev/null; then
        echo OK
        exit 0
    else
        echo KO
    fi
done

exit 1
"""

# the command we want to run in faraday is as simple as it gets
ping = SshJob(
    node = node1,
    required = (init_node_01, init_node_02),
    # let us be more specific about what to run
    # we will soon see other things we can do on an ssh connection
    command = RunString(
        repetitive_ping_script, '10.0.0.2', '-I', ifname,
#        verbose=True,
    ))

# forget about the troubleshooting from now on

# we have 4 jobs to run this time
sched = Scheduler(check_lease, ping, init_node_01, init_node_02)

# run the scheduler
ok = sched.orchestrate()

# we say this is a success if the ping command succeeded
# the result() of the SshJob is the value that the command
# returns to the OS
# so it's a success if this value is 0
success = ok and ping.result() == 0

# return something useful to your OS
exit(0 if success else 1)
