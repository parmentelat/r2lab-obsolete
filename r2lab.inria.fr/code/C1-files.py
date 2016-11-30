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

##########
faraday = SshNode(hostname = gateway_hostname, username = gateway_username,
                  verbose = verbose_ssh)

# saying gateway = faraday means to tunnel ssh through the gateway
node1 = SshNode(gateway = faraday, hostname = "fit01", username = "root",
                verbose = verbose_ssh)

########## 1 step, generate a random data file of 1 M bytes
create_random_job = SshJob(
    node = LocalNode(),
    commands = [
        Run("head", "-c", 2**20, "<", "/dev/random", ">", "RANDOM"),
        Run("ls", "-l", "RANDOM"),
        Run("shasum", "RANDOM"),
        ])

########## 2nd step : push this over to node1

push_job = SshJob(
    node = node1,
    required = create_random_job,
    commands = [
        Push( localpaths = [ "RANDOM" ],
              remotepath = "."),
        Run("ls -l RANDOM"),
        Run("sha1sum RANDOM"),
    ]
)

##########
# create an orchestration scheduler with these 2 jobs
sched = Scheduler(create_random_job, push_job)

# run the scheduler
ok = sched.orchestrate()

# return something useful to your OS
exit(0 if ok else 1)
