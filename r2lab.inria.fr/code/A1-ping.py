#!/usr/bin/env python3

from asynciojobs import Scheduler

from apssh import SshNode, SshJob

##########
# globals - how to reach the gateway
gateway_hostname  = 'faraday.inria.fr'
gateway_username  = 'inria_r2lab.tutorial'
# to get feedback on the ssh-connection and see why it fails
verbose_ssh = True

##########
# this SshNode object holds the details of
# the first-leg ssh connection to the gateway
faraday = SshNode(hostname = gateway_hostname, username = gateway_username,
                  verbose = verbose_ssh)

##########
# the command we want to run in faraday is as simple as it gets
ping = SshJob(
    # on what node do we want to run this:
    node = faraday,
    # what to run
    command = [ 'ping', '-c1',  'google.fr' ],
)

##########
# how to run the same directly with ssh - for troubleshooting
print("""--- for troubleshooting:
ssh -i /dev/null {}@{} ping -c1 google.fr
---""".format(gateway_username, gateway_hostname))

##########
# create an orchestration scheduler with this single job
sched = Scheduler(ping)

# run the scheduler
ok = sched.orchestrate()

print("orchestrate -", ok)
