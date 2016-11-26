#!/usr/bin/env python3

from argparse import ArgumentParser

from asynciojobs import Scheduler

from apssh import SshNode, SshJob, Run

##########
gateway_hostname  = 'faraday.inria.fr'
gateway_username  = 'onelab.inria.r2lab.tutorial'
verbose_ssh = False

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

node1 = SshNode(gateway = faraday, hostname = "fit01", username = "root",
                verbose = verbose_ssh)
node2 = SshNode(gateway = faraday, hostname = "fit02", username = "root",
                verbose = verbose_ssh)

##########
check_lease = SshJob(
    # checking the lease is done on the gateway
    node = faraday,
    # this means that a failure in any of the commands
    # will cause the scheduler to bail out immediately
    critical = True,
    command = Run("rhubarbe leases --check"),
)

# setting up the data interface on both fit01 and fit02
init_node_01 = SshJob(node = node1, command = Run("data-up"), required = check_lease)
init_node_02 = SshJob(node = node2, command = Run("data-up"), required = check_lease)

# the command we want to run in faraday is as simple as it gets
ping = SshJob(
    node = node1,
    # let's be more specific about what to run
    # we will soon see other things we can do on an ssh connection
    commands = Run('ping', '-c1', '-I', 'data', 'data02'),
    # this says that we wait for check_lease to finish before we start ping
    required = (init_node_01, init_node_02),
)

##########
# our orchestration scheduler has 4 jobs to run this time
sched = Scheduler(check_lease, ping, init_node_01, init_node_02)

# run the scheduler
ok = sched.orchestrate()

# return something useful to your OS
exit(0 if ok else 1)
