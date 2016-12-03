#!/usr/bin/env python3

from argparse import ArgumentParser

from asynciojobs import Scheduler

from apssh import SshNode, SshJob, Run

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

##########
# the command we want to run in node1 is as simple as it gets
ping = SshJob(
    node = node1,
    # let's be more specific about what to run
    # we will soon see other things we can do on an ssh connection
    command = Run('ping', '-c1',  'google.fr'),
)

##########
# how to run the same directly with ssh - for troubleshooting
print("""--- for troubleshooting: 
ssh -i /dev/null {}@{} ssh root@fit01 ping -c1 google.fr
---""".format(gateway_username, gateway_hostname))

##########
# create an orchestration scheduler with this single job
sched = Scheduler(ping)

# run the scheduler
ok = sched.orchestrate()
# give details if it failed
ok or sched.debrief()

# return something useful to your OS
exit(0 if ok else 1)
