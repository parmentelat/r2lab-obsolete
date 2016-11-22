#!/usr/bin/env python3

from asynciojobs import Scheduler

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

# this time we will create an Scheduler instance and add jobs in it as we create them
sched = Scheduler(verbose=True)

# the names used for configuring the wireless network
wifi_interface = 'atheros'
wifi_freq      = 2432
wifi_name      = 'my-net'

# this time we cannot use DHCP, so we provide all the details
# of the IP subnet manually
wifi_netmask   = '24'
wifi_ip_fit01  = '172.16.1.1'
wifi_ip_fit02  = '172.16.1.2'

####################
turn_on_wireless_script = """#!/bin/bash
# this plain bash script will run on the remote machine
# either sender or receiver
# and is in charge of initializing a small ad-hoc network

# we expect 4 arguments which are 
# 1. the wireless interface name (on r2lab : use intel or atheros)
# 2. the IP address to use on that interface
# 3. netmask as an integer - e.g. 24 for a class-C
# 4. the wifi network name to join
# 5. the wifi frequency to use
# see also https://wireless.wiki.kernel.org/en/users/documentation/iw

ifname=$1; shift
ipaddr=$1; shift
mask=$1; shift
netname=$1; shift
freq=$1;   shift

echo configuring $ifname
# make sure to wipe down everything first so we can run again and again
ip address flush dev $ifname
ip link set $ifname down
# configure wireless
iw dev $ifname set type ibss
ip link set $ifname up
# set to ad-hoc mode
iw dev $ifname ibss join $netname $freq
ip address add $ipaddr/$mask dev $ifname
# artificial delay to let things settle
sleep=5
echo sleeping ${sleep}s
sleep $sleep
iw dev $ifname info
# show status
iw dev $ifname info
iw dev $ifname link
"""
####################

# In this case instead of inserting a simple Run in the SshJob's commands list
# we insert a RunString object, which is very similar to Run except its first
# argument must denote a string that contains the command to run remotely
# the other arguments are passed to that script

# a first pair of jobs are needed to start-up the wireless interface on each node
job_init_1 = SshJob(
    node = fit1,
    command = RunString(
        # first argument is a memory string that contains the script to run
        turn_on_wireless_script,
        # remaining arguments are passed to that script
        wifi_interface, wifi_ip_fit01, wifi_netmask,
        wifi_name, wifi_freq),
    label = 'Turn on wireless interface on node 1'
)

job_init_2 = SshJob(
    node = fit2,
    # ditto but with wifi_ip_fit02 instead
    command = RunString(
        turn_on_wireless_script,
        wifi_interface, wifi_ip_fit02, wifi_netmask,
        wifi_name, wifi_freq),
    label = 'Turn on wireless interface on node 2'
)
# a Scheduler is a set of jobs, so as for a builtin set object
# you can use update to add a collection of nodes
sched.update( [job_init_1, job_init_2] )

# then the actual ping is run on node 1 and targets node 2
job_ping = SshJob(
    node = fit1,
    command = Run('ping', '-c1',  '-I', wifi_interface, wifi_ip_fit02),
    label = "pinging node2 from node1 on the wireless interface",
    # this says that job_ping cannot start until these 2 jobs are done
    required = (job_init_1, job_init_2),
)

# or you can one single job in the scheduler using just add
sched.add(job_ping)

print("---------- orchestrating")    

# run the scheduler and return 0 to the OS iff it all goes fine
os_retcod = 0 if sched.orchestrate() else 1
exit(os_retcod)
