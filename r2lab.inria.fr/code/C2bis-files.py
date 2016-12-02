#!/usr/bin/env python3

import sys, os

import asyncio

from argparse import ArgumentParser

from asynciojobs import Scheduler, Job, Sequence

from apssh import SshNode, SshJob, LocalNode
from apssh import Run, RunString, Push

##########

gateway_hostname  = 'faraday.inria.fr'
gateway_username  = 'onelab.inria.r2lab.tutorial'
verbose_ssh = False
random_size = 2**10
netcat_port = 10000

# this time we want to be able to specify username and verbose_ssh
parser = ArgumentParser()
parser.add_argument("-s", "--slice", default=gateway_username,
                    help="specify an alternate slicename, default={}"
                         .format(gateway_username))
parser.add_argument("-v", "--verbose-ssh", default=False, action='store_true',
                    help="run ssh in verbose mode")
args = parser.parse_args()

gateway_username = args.slice
verbose_ssh = args.verbose_ssh

########## the nodes involved

faraday = SshNode(hostname = gateway_hostname, username = gateway_username,
                  verbose = verbose_ssh)

# saying gateway = faraday means to tunnel ssh through the gateway
node1 = SshNode(gateway = faraday, hostname = "fit01", username = "root",
                verbose = verbose_ssh)
node2 = SshNode(gateway = faraday, hostname = "fit02", username = "root",
                verbose = verbose_ssh)

nodes = (node1, node2)

########## let us create the scheduler instance upfront

scheduler = Scheduler()

########## 1 step, generate a random data file of 1 M bytes

create_random_job = SshJob(
    node = LocalNode(),
    scheduler = scheduler,
    commands = [
        Run("head", "-c", random_size, "<", "/dev/random", ">", "RANDOM"),
        Run("ls", "-l", "RANDOM"),
        Run("shasum", "RANDOM"),
        ])

########## 2nd step : push this over to node1

push_job = SshJob(
    node = node1,
    scheduler = scheduler,
    required = create_random_job,
    commands = [
        Push( localpaths = [ "RANDOM" ],
              remotepath = "."),
        Run("ls -l RANDOM"),
        Run("sha1sum RANDOM"),
    ]
)

########## step 3 : turn on data interfaces
# a convenient way to create many jobs in a single pass is  
# to build a list of jobs using a python comprehension

turn_on_datas = [ SshJob( node = node,
                          scheduler = scheduler,
                          required = push_job,
                          command = Run("turn-on-data") )
                  for node in nodes ]

########## next : run a sender on node1 and a receiver on node 2
# in order to transfer RANDOM over a netcat session on the data network
#
receiver_manager_script = """#!/bin/bash
source /root/r2lab/infra/user-env/nodes.sh

function start() {
    port=$1; shift
    outfile=$1; shift
    # r2lab-id returns a 2-digit string with the node number
    ipaddr="data"$(r2lab-id)
    echo "STARTING CAPTURE into $outfile"
    # start netcat in listen mode
    netcat -l $ipaddr $port > $outfile &
    # bash's special $! returns pid of the last job sent in background
    # preserve this pid in local file 
    echo $! > netcat.pid
    echo netcat server running on $ipaddr:$port in pid $!
}

function stop() {
    echo "STARTING CAPTURE into $outfile"
    pid=$(cat netcat.pid)
    # not necessary as netcat dies on its own when clent terminates
    echo Would kill process $pid
    rm netcat.pid
}

function monitor () {
    while true; do
        pid=$(pgrep netcat)
        [ -n "$pid" ] && ps $pid || echo no netcat process
# thanks to Ubuntu the shell's sleep can do fractions of seconds
        sleep .2
    done
}
# usual generic laucher
"$@"
"""

# start the receiver - this of course returns immediately
SshJob( node = node2,
        scheduler = scheduler,
        required = turn_on_datas,
        commands = [
            RunString(receiver_manager_script, "start", netcat_port, "RANDOM",
                      remote_name = "receiver-manager"),
        ])

Sequence(
    # start the sender 
    SshJob( node = node1,
            # ignore netcat result
            critical = False,
            commands = [
                # let the server warm up just in case
                Run("sleep 1"),
                Run("netcat", "data02", netcat_port, "<", "RANDOM"),
                Run("echo SENDER DONE"),
            ]),
    # kill the receiver, and
    # check contents on the receiving end
    SshJob( node=node2,
            # set a label for the various representations
            # including the graphical one obtained with export_as_dotfile
            label = "stop receiver",
            commands = [
                RunString(receiver_manager_script, "stop",
                          remote_name="receiver-manager"),
                Run("ls -l RANDOM"),
                Run("sha1sum RANDOM"),
            ]),
    required = turn_on_datas,
    scheduler = scheduler,
)

SshJob( node = node2,
        scheduler = scheduler,
        forever = True,
        # see above
        label = "infinite monitor",
        commands = [
            RunString(receiver_manager_script, "monitor",
                      remote_name="receiver-manager"),
        ])

# we produce the attached png in 2 stages
# first we create a dot file with this call:
scheduler.export_as_dotfile("C2bis-files.dot")
# then we run
# dot -Tpng -o C2bis-files.png C2bis-files.dot

##########

# run the scheduler
ok = scheduler.orchestrate()

# return something useful to your OS
exit(0 if ok else 1)
