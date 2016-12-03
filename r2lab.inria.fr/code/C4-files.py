#!/usr/bin/env python3

import sys, os

import asyncio

from argparse import ArgumentParser

from asynciojobs import Scheduler, Job, Sequence

from apssh import SshNode, SshJob, LocalNode
from apssh import Run, RunString, Push, Pull

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
parser.add_argument("-l", "--load-images", default=False, action='store_true',
                    help = "enable to load the default image on nodes before the exp")
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
check_lease = SshJob(node = faraday, critical = True,
                     # this is how we can create the job right into the scheduler
                     # so no need to add it later on
                     scheduler = scheduler,
                     command = Run("rhubarbe leases --check"))

########## 1 step, generate a random data file of 1 M bytes

create_random_job = SshJob(
    node = LocalNode(),
    scheduler = scheduler,
    required = check_lease,
    commands = [
        Run("head", "-c", random_size, "<", "/dev/random", ">", "RANDOM"),
        Run("ls", "-l", "RANDOM"),
        Run("shasum", "RANDOM"),
        ])

# gather in this variable the jobs that we need to wait for
# before we go and actually do things on the nodes
green_light_jobs = [ create_random_job ]

# if the user has specified --load on the command line
# we insert this job that is about loading the image on
# our 2 nodes, and wait for them to come up
# note that with big images, you may want to run the load command
# with a higher timeout (default is 300s = 5mn)
if args.load_images:
    # let us not hard wire the node ids, in a more general script
    # where node ids are configurable on the commands line it may
    # be useful to use this basic python technique for passing arguments
    # see the *node_ids below
    node_ids = [1, 2]
    negated_node_ids = [ "~{}".format(id) for id in node_ids ]
    load_nodes_job = SshJob(
        node = faraday,
        # do this only if we have a lease
        required = check_lease,
        # if rhubarbe wait fails, it means the nodes are not good to use
        critical = True,
        scheduler = scheduler,
        # rload and the like are aliases, it is safer to call plain rhubarbe here
        commands = [
            # turn off all other nodes
            Run("rhubarbe", "off", "-a", *negated_node_ids),
            # load the images
            Run("rhubarbe", "load", "-i", "ubuntu", *node_ids),
            # wait for the nodes to come back online
            Run("rhubarbe", "wait", *node_ids)
            ]
        )
    # this is to ensure that push_job will wait for the image loading step
    # when we run with --load
    green_light_jobs.append(load_nodes_job)

########## 2nd step : push this over to node1

push_job = SshJob(
    node = node1,
    scheduler = scheduler,
    # here we wait for both check_lease and load_nodes_job
    required = green_light_jobs,
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

# a Sequence object is a container for jobs, they will have their
# 'requires' relationship organized along the sequence order

transfer_job = Sequence(

    # start the receiver - this of course returns immediately
    SshJob( node = node2,
            commands = [
                Run("netcat", "-l", "data02", netcat_port, ">", "RANDOM", "&"),
            ]),

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

    # check contents on the receiving end
    SshJob( node=node2,
            commands = [
                Run("ls -l RANDOM"),
                Run("sha1sum RANDOM"),
            ]),

    ### these two apply to the Sequence
    # required applies to the first job in the sequence
    required = turn_on_datas,
    # scheduler applies to all jobs in the sequence
    scheduler = scheduler,
)

########## finally : let's complete the loop and
########## retrieve RANDOM from node2 back on local laptop

Sequence(
    SshJob( node = node2,
            commands = [
                Run("echo the Pull command runs on $(hostname)"),
                Pull(remotepaths = "RANDOM",
                     localpath = "RANDOM.loopback"),
            ]),
    # make sure the file we receive at the end of the loop
    # is identical to the original
    SshJob( node = LocalNode(),
            commands = [
                Run("ls -l RANDOM.loopback", verbose=True),
                Run("diff RANDOM RANDOM.loopback && echo RANDOM.loopback identical to RANDOM"),
            ]),
    scheduler = scheduler,
    required = transfer_job
)

##########

# run the scheduler
ok = scheduler.orchestrate()
# give details if it failed
ok or scheduler.debrief()

# return something useful to your OS
exit(0 if ok else 1)
