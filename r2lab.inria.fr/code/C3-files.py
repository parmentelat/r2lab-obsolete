#!/usr/bin/env python3

import sys, os

import asyncio

from argparse import ArgumentParser

from asynciojobs import Scheduler, Job

from apssh import SshNode, SshJob, LocalNode, Run
from apssh import Push

##########

gateway_hostname  = 'faraday.inria.fr'
gateway_username  = 'onelab.inria.r2lab.tutorial'
verbose_ssh = False
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
        Run("head", "-c", 2**20, "<", "/dev/random", ">", "RANDOM"),
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

########## step 4 : run a sender on node1 and a receiver on node 2

receiver_job = SshJob( node = node2,
                       scheduler = scheduler,
                       required = turn_on_datas,
                       # the server will never return, so don't wait for it
                       forever = True,
                       commands = [ Run("sleep 2"),
                                    Run("netcat", "-l", "fit02", netcat_port,
                                        ">", "RANDOM")])

sender_job = SshJob( node = node1,
                     scheduler = scheduler,
                     required = turn_on_datas,
                     command = Run("netcat", "fit02", netcat_port,
                                   "<", "RANDOM"))

########## step 5 : retrieve RANDOM from node2 back on local laptop

pull_job = SshJob( node = node2,
                   scheduler = scheduler,
                   # do *NOT* wait for receiver_job
                   required = sender_job,
                   # name this copy RANDOM.loopback
                   # which of course is expected to be identical
                   commands = Pull(remotepaths = [ "RANDOM" ],
                                   localpath = "RANDOM.loopback"))

########## last step : compare RANDOM and RANDOM loopback

compare_job = SshJob( node = LocalNode(),
                      scheduler = scheduler,
                      required = pull_job,
                      command = Run("diff RANDOM RANDOM.loopback"))

##########

# run the scheduler
ok = sched.orchestrate()

# return something useful to your OS
exit(0 if ok else 1)
