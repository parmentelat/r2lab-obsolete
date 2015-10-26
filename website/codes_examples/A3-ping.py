#!/usr/bin/env python

# including nepi library and other required packages
from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState
from nepi.util.sshfuncs import logger
import os

# setting up the default host, onelab user and shh key credential
host_gateway  = 'faraday.inria.fr'
user_gateway  = 'onelab.inria.mario.tutorial'
user_identity = '~/.ssh/id_rsa'

# setting up the credentials for the nodes 
host01 = 'fit01'
user01 = 'root'

host02 = 'fit02'
user02 = 'root'

# creating a new ExperimentController (EC) to manage the experiment
ec = ExperimentController(exp_id="A3-ping")

# creating the gateway node
gateway = ec.register_resource("linux::Node")
ec.set(gateway, "username", user_gateway)
ec.set(gateway, "hostname", host_gateway)
ec.set(gateway, "identity", user_identity)
ec.set(gateway, "cleanExperiment", True)
ec.set(gateway, "cleanProcesses", True)
# deploying the gateway node
ec.deploy(gateway)

# creating the fit01 node
fit01 = ec.register_resource("linux::Node")
ec.set(fit01, "username", user01)
ec.set(fit01, "hostname", host01)
# to reach the fit01 node it must go through the gateway, so let's assign the gateway infos
ec.set(fit01, "gateway", host_gateway)
ec.set(fit01, "gatewayUser", user_gateway)
ec.set(fit01, "identity", user_identity)
ec.set(fit01, "cleanExperiment", True)
ec.set(fit01, "cleanProcesses", True)
# deploying the fit01 node
ec.deploy(fit01)

# creating the fit02 node 
fit02 = ec.register_resource("linux::Node")
ec.set(fit02, "username", user02)
ec.set(fit02, "hostname", host02)
# to reach the fit02 node it must go through the gateway, so let's assign the gateway infos
ec.set(fit02, "gateway", host_gateway)
ec.set(fit02, "gatewayUser", user_gateway)
ec.set(fit02, "identity", user_identity)
ec.set(fit02, "cleanExperiment", True)
ec.set(fit02, "cleanProcesses", True)
# deploying the fit02 node
ec.deploy(fit02)

# application to setup data interface on fit01 node
app_fit01 = ec.register_resource("linux::Application")
cmd = 'sudo ip link set dev data down; sudo dhclient data;'
ec.set(app_fit01, "command", cmd)
ec.register_connection(app_fit01, fit01)
ec.deploy(app_fit01)
ec.wait_finished(app_fit01)

# application to setup data interface on fit02 node
app_fit02 = ec.register_resource("linux::Application")
cmd = 'sudo ip link set dev data down; sudo dhclient data;'
ec.set(app_fit02, "command", cmd)
ec.register_connection(app_fit02, fit02)
ec.deploy(app_fit02)
ec.wait_finished(app_fit02)

# creating an application to ping the experiment inteface of fit02 from the fit01
app_ping_from_fit01_to_fit02 = ec.register_resource("linux::Application")
cmd = 'ping -c1 192.168.02.02; '
ec.set(app_ping_from_fit01_to_fit02, "command", cmd)
ec.register_connection(app_ping_from_fit01_to_fit02, fit01)
ec.deploy(app_ping_from_fit01_to_fit02)
ec.wait_finished(app_ping_from_fit01_to_fit02)

# recovering the results
print "\n--- INFO: output:"
print ec.trace(app_ping_from_fit01_to_fit02, "stdout")

# shutting down the experiment
ec.shutdown()