#!/usr/bin/env python3

from asynciojobs import Engine

from apssh import SshNode, SshJob

# we want to run a command right in the r2lab gateway
# so we need to define ssh-related details for doing so :

gateway_hostname  = 'faraday.inria.fr'
gateway_username  = 'onelab.inria.r2lab.tutorial'
gateway_key       = '~/.ssh/onelab.private'

# we create a SshNode object that holds the details of
# the first-leg ssh connection to the gateway

# remember to make sure the right ssh key is known to your ssh agent
faraday = SshNode(hostname = gateway_hostname, username = gateway_username)

# the command we want to run in faraday is as simple as it gets
ping = SshJob(
    # on what node do we want to run this:
    node = faraday,
    # what to run
    command = [ 'ping', '-c1',  'google.fr' ],
    # you have to provide a label, it's going to be very helpful
    # when running many things in parallel
    label = "pinging google France"
)

# how to run the same directly with ssh - for troubleshooting
print("""---
for troubleshooting: 
ssh {}@{} ping -c1 google.fr
---""".format(gateway_username, gateway_hostname))

# create an orchestration engine
# with this single job
e = Engine(ping)

# run it
ok = e.orchestrate()

