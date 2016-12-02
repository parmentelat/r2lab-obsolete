#!/usr/bin/env python3

from argparse import ArgumentParser

from asynciojobs import Scheduler

from apssh import SshNode, LocalNode, SshJob
from apssh import Run, RunString, Pull

import time


##########
gateway_hostname  = 'faraday.inria.fr'
gateway_username  = 'onelab.inria.r2lab.tutorial'
verbose_ssh = False
wireless_driver="ath9k"
wireless_interface="atheros"
ping_count = 12

parser = ArgumentParser()
parser.add_argument("-s", "--slice", default=gateway_username,
                    help="specify an alternate slicename, default={}"
                         .format(gateway_username))
parser.add_argument("-m", "--max", default=5, type=int,
                    help="will run on all nodes beteen 1 and this number")
parser.add_argument("-v", "--verbose-ssh", default=False, action='store_true',
                    help="run ssh in verbose mode")
parser.add_argument("-d", "--debug", default=False, action='store_true',
                    help="run jobs and engine in verbose mode")
args = parser.parse_args()

gateway_username = args.slice
verbose_ssh = args.verbose_ssh
verbose_jobs = args.debug

node_ids = range(1, args.max+1)

##########
faraday = SshNode(hostname = gateway_hostname, username = gateway_username,
                  verbose = verbose_ssh)

def fitname(id):
    return "fit{:02d}".format(id)

node_index = {
    id: SshNode(gateway = faraday,
                hostname = fitname(id),
                username = "root", 
                verbose = verbose_ssh)
    for id in node_ids
}

scheduler = Scheduler(verbose = verbose_jobs)

##########
check_lease = SshJob(
    scheduler = scheduler,
    node = faraday,
#    verbose = verbose_jobs,
    critical = True,
    command = Run("rhubarbe leases --check"),
)

####################
# This is our own brewed script for setting up a wifi network
# it runs on the remote machine - either sender or receiver
# and is in charge of initializing a small ad-hoc network
#
# Thanks to the RunString class, we can just define this as
# a python string, and pass it arguments from python variables
#

turn_on_wireless_script = """#!/bin/bash

# we expect the following arguments
# * wireless driver name (iwlwifi or ath9k)
# * wireless interface name (intel or atheros)
# * the wifi network name to join
# * the wifi frequency to use

driver=$1; shift
ifname=$1; shift
netname=$1; shift
freq=$1;   shift

# load the r2lab utilities - code can be found here:
# https://github.com/parmentelat/r2lab/blob/master/infra/user-env/nodes.sh
source /root/r2lab/infra/user-env/nodes.sh

git-pull-r2lab

turn-off-wireless

byte=$(sed -e 's,^0,,' <<< $(r2lab-id))

ipaddr_mask=10.0.0.$byte/24

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

##########
# setting up the wireless interface on both fit01 and fit02

init_wireless_jobs = [
    SshJob(
        scheduler = scheduler,
        required = check_lease,
        node = node,
        command = RunString(
            turn_on_wireless_script,
            wireless_driver, wireless_interface, "foobar", 2412,
            verbose = verbose_jobs,
            remote_name="turn-on-wireless",
        ))
    for id, node in node_index.items() ]

# print("==================== LIST 1")
# for job in init_wireless_jobs:
#     print(job)

pings = [
    SshJob(
        scheduler = scheduler,
        node = nodei,
        required = init_wireless_jobs,
#        verbose = verbose_jobs,
        commands = [
            Run("echo", "Pinging", j, "from", i, ping_count, "times"),
            Run("ping", "-c", ping_count, "10.0.0.{}".format(j),
                "-I", wireless_interface,
                ">", "PING-{}-{}".format(i, j)),
            Run("echo", "Ping", j, "from", i, "DONE"),
            Pull(remotepaths = "PING-{}-{}".format(i, j),
                 localpath="."),
        ]
    )
    for i, nodei in node_index.items()
    for j, nodej in node_index.items()
    if j > i
]

SshJob(
    node = LocalNode(),
    scheduler = scheduler,
    required = pings,
    commands = [
        Run("ls", "-l", "PING*")
    ]
)

# print("==================== LIST 2")
# for job in pings:
#     print(job)

# print("==================== COMPLETE SCHEDULER")
# scheduler.list(details=True)

success = scheduler.orchestrate()

# return something useful to your OS
exit(0 if success else 1)
