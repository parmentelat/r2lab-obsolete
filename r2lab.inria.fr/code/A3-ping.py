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

fit1 = SshNode(gateway = faraday,  hostname = "fit01", username = "root")
fit2 = SshNode(gateway = faraday,  hostname = "fit02", username = "root")

# this time we will create an Engine instance and add jobs in it as we create them
e = Engine()

# a first pair of jobs are needed to start-up the data interface on each node
job_init_1 = SshJob(
    node = fit1,
    command = [ 'ifup', 'data' ],
    label = 'Turn on data interface on node 1'
)
job_init_2 = SshJob(
    node = fit2,
    command = [ 'ifup', 'data' ],
    label = 'Turn on data interface on node 2'
)
# an Engine is a set of jobs, so as for a builtin set object
# you can use update to add a collection of nodes
e.update( [job_init_1, job_init_2] )

# then the actual ping is run on node 1 and targets node 2
job_ping = SshJob(
    node = fit1,
    # we use 'data02' as the hostname to reach the right interface of node 2
    # and specify -I data to be safe
    command = [ 'ping', '-c1',  '-I', 'data', 'data02' ],
    label = "pinging node2 from node1 on the wired interface",
    # this says that job_ping cannot start until these 2 jobs are done
    required = (job_init_1, job_init_2),
)

# or you can one single job in the engine using just add
e.add(job_ping)

# run the engine
ok = e.orchestrate()

