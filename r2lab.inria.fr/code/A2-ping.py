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

# from here we can create a second node object that leverages on this first leg
# to create a 2-leg connection from our laptop to a node
fit1 = SshNode(
    # specifying a gateway means we use a 2-leg ssh connection
    gateway = faraday,
    # we always enter nodes as root from faraday
    hostname = "fit01", username = "root",
)

# the command we want to run in faraday is as simple as it gets
ping = SshJob(
    node = fit1,
    command = [ 'ping', '-c1',  'faraday.inria.fr' ],
    label = "pinging the r2lab gateway from the inside"
)

# how to run the same directly with ssh - for troubleshooting
# in particular the script in this form assumes that fit01 is up and running
print("""---
for troubleshooting: 
ssh {}@{} ssh root@fit01 ping -c1 faraday.inria.fr
---""".format(gateway_username, gateway_hostname))

# create an orchestration engine
# with this single job
e = Engine(ping)

# run it
ok = e.orchestrate()

