#!/usr/bin/env python3

# for using print() in python3-style even in python2
from __future__ import print_function

# import nepi library and other required packages
from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState
from nepi.util.sshfuncs import logger

# creating an ExperimentController (EC) to manage the experiment
# the exp_id name should be unique for your experiment
# it will be used on the various resources
# to store results and similar functions
ec = ExperimentController(exp_id="A4-ping")

# we want to run a command right in the r2lab gateway
# so we need to define ssh-related details for doing so
gateway_hostname  = 'faraday.inria.fr'
gateway_key       = '~/.ssh/onelab.private'
# of course: you need to change this to describe your own slice
gateway_username  = 'onelab.inria.mario.tutorial'

# the names used for configuring the wireless network
wifi_interface = 'wlan0'
wifi_channel   = '4'
wifi_name      = 'my-net'
wifi_key       = '1234567890'

# this time we cannot use DHCP, so we provide all the details
# of the IP subnet manually
wifi_netmask   = '24'
wifi_ip_fit01  = '172.16.1.1'
wifi_ip_fit02  = '172.16.1.2'

fit01 = ec.register_resource("linux::Node",
                             username = 'root',
                             hostname = 'fit01',
                             gateway = gateway_hostname,
                             gatewayUser = gateway_username,
                             identity = gateway_key,
                             cleanExperiment = True,
                             cleanProcesses = True,
                             autoDeploy = True)

fit02 = ec.register_resource("linux::Node",
                             username = 'root',
                             hostname = 'fit02',
                             gateway = gateway_hostname,
                             gatewayUser = gateway_username,
                             identity = gateway_key,
                             cleanExperiment = True,
                             cleanProcesses = True,
                             autoDeploy = True)

# define the wifi init script
# that will be uploaded on the node

init_wlan_script = """\
#!/bin/bash
# Usage: $0 wifi_interface wifi_ip wifi_netmask wifi_channel wifi_name wifi_key 
wifi_interface=$1; shift
wifi_channel=$1; shift
wifi_name=$1; shift
wifi_key=$1; shift
wifi_ip=$1; shift
wifi_netmask=$1; shift

ip addr flush dev $wifi_interface
ip link set $wifi_interface down
iwconfig $wifi_interface mode ad-hoc
iwconfig $wifi_interface channel $wifi_channel
iwconfig $wifi_interface essid "$wifi_name"
iwconfig $wifi_interface key $wifi_key
ip link set $wifi_interface up
ip addr add $wifi_ip/$wifi_netmask dev $wifi_interface
"""

# in this tutorial we use an inline script (i.e. a python string)
# this could as easily be stored in an external file of course
# which is what is done in practice;
# init_wlan_script = "./init-wlan.sh"
# would work just as well


# creating an application to
# configure an ad-hoc network on node fit01
# this time the command to run uses the shared shell script
# that gets uploaded on the node thanks to the code= setting on the app
# so we're left with calling this initscript with proper arguments
# note that the uploaded script is always (the executable file)
# in ${APP_HOME}/code
cmd = \
"${APP_HOME}/code {wifi_interface} {wifi_ip_fit01} {wifi_netmask}"
"{wifi_channel} {wifi_name} {wifi_key}"
.format(**locals())

app_fit01 = ec.register_resource("linux::Application",
                                 # to upload the initscript on the node; note that
                                 # we could have used a local filename instead of a string
                                 code = init_wlan_script,
                                 command = cmd,
                                 autoDeploy = True,
                                 connectedTo = fit01)
ec.wait_finished(app_fit01)

# ditto on fit02
cmd = \
"${APP_HOME}/code {wifi_interface} {wifi_ip_fit02} {wifi_netmask}"
"{wifi_channel} {wifi_name} {wifi_key}"
.format(**locals())

app_fit02 = ec.register_resource("linux::Application", code = init_wlan_script,
                                 command = cmd
                                 autoDeploy = True,
                                 connectedTo = fit02)
ec.wait_finished(app_fit02)

# creating an application to ping the wireless
# interface of fit02 from fit01
cmd = 'ping -c5 -I {} {}'.format(wifi_interface, wifi_ip_fit02)
app1 = ec.register_resource("linux::Application",
                            command = cmd,
                            autoDeploy = True,
                            connectedTo = fit01)
ec.wait_finished(app1)

# and the other way around
cmd = 'ping -c5 -I {} {}'.format(wifi_interface, wifi_ip_fit01)
app2 = ec.register_resource("linux::Application",
                            command = cmd,
                            autoDeploy = True,
                            connectedTo = fit02)
ec.wait_finished(app2)

print ("--- INFO : experiment output on fit01:",
       ec.trace(app1, "stdout"))
print ("--- INFO : experiment output on fit02:",
       ec.trace(app2, "stdout"))

ec.shutdown()
