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
e = Engine(verbose=True)

# the names used for configuring the wireless network
wifi_interface = 'wlan1'
wifi_freq      = 2432
wifi_name      = 'my-net'

# this time we cannot use DHCP, so we provide all the details
# of the IP subnet manually
wifi_netmask   = '24'
wifi_ip_fit01  = '172.16.1.1'
wifi_ip_fit02  = '172.16.1.2'

# Note that an SshJob can be created with a command (singular)
# but also commands (plural) arguments,
# in which case they are run in sequence
cmds1 = []
cmds1.append( ["echo", "configuring", wifi_interface] )
# make sure to wipe down everything first so we can run again and again
cmds1.append( ["ip", "address", "flush", "dev", wifi_interface] )
cmds1.append( ["ip", "link", "set", wifi_interface, "down"] )
# configure wireless
cmds1.append( ["iw", "dev", wifi_interface, "set", "type", "ibss"] )
cmds1.append( ["ip", "link", "set", wifi_interface, "up"] )
cmds1.append( ["iw", "dev", wifi_interface, "ibss", "join", wifi_name, wifi_freq] )
cmds1.append( ["ip", "address", "add", "{}/{}".format(wifi_ip_fit01, wifi_netmask),
               "dev", wifi_interface] )
# show wireless
import sys
sleep = 5
cmds1.append( ["echo sleeping", sleep, "; sleep", sleep] )
cmds1.append( ["iw dev", wifi_interface, "info"] )
cmds1.append( ["iw dev", wifi_interface, "link"] )
# assign ip address and netmask

# this first version is a little tedious of course
# so here instead of duplicating the commands for node2, we just 'patch'
# the ones we have for node1, and replace wifi_ip_fit01 with wifi_ip_fit02
# note that we'll see how to do this better in furter releases
cmds2 = [ [x.replace(wifi_ip_fit01, wifi_ip_fit02) if isinstance(x, str) else x
           for x in command] for command in cmds1]
    

# a first pair of jobs are needed to start-up the wireless interface on each node
job_init_1 = SshJob(
    node = fit1,
    commands = cmds1,
    label = 'Turn on wireless interface on node 1'
)
job_init_2 = SshJob(
    node = fit2,
    commands = cmds2,
    label = 'Turn on wireless interface on node 2'
)
# an Engine is a set of jobs, so as for a builtin set object
# you can use update to add a collection of nodes
e.update( [job_init_1, job_init_2] )

# then the actual ping is run on node 1 and targets node 2
job_ping = SshJob(
    node = fit1,
    commands = [
        ['ping', '-c1',  '-I', wifi_interface, wifi_ip_fit02 ],
        ['true'],
    ],
    label = "pinging node2 from node1 on the wireless interface",
    # this says that job_ping cannot start until these 2 jobs are done
    required = (job_init_1, job_init_2),
)

# or you can one single job in the engine using just add
e.add(job_ping)

print("---------- orchestrating")    

# run the engine
ok = e.orchestrate()
