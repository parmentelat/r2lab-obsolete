#!/usr/bin/env python

# including nepi library and other required packages
from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState
from nepi.util.sshfuncs import logger
import os

# setting up the default host, onelab user and shh key credential
host_gateway  = 'faraday.inria.fr'
user_gateway  = 'mario'
user_identity = '~/.ssh/id_rsa'
gateway_dir = '/home/mario/'

# setting up the credentials for the nodes 
host01 = 'fit01'
user01 = 'root'
host01_dir = '/home/'

host02 = 'fit02'
user02 = 'root'
port 	 =  1236
host02_dir = '/home/'

file      = 'file.txt'
local_dir = '/Users/nano/'

# creating a new ExperimentController (EC) to manage the experiment
ec = ExperimentController(exp_id="B1-send-file")

# creating local
local = ec.register_resource("linux::Node")
ec.set(local, "hostname", 'localhost')
ec.set(local, "cleanExperiment", True)
ec.set(local, "cleanProcesses", True)
ec.deploy(local)

# creating the gateway node
gateway = ec.register_resource("linux::Node")
ec.set(gateway, "username", user_gateway)
ec.set(gateway, "hostname", host_gateway)
ec.set(gateway, "identity", user_identity)
ec.set(gateway, "cleanExperiment", True)
ec.set(gateway, "cleanProcesses", True)
ec.deploy(gateway)

# creating the fit01 node
fit01 = ec.register_resource("linux::Node")
ec.set(fit01, "username", user01)
ec.set(fit01, "hostname", host01)
ec.set(fit01, "gateway", host_gateway)
ec.set(fit01, "gatewayUser", user_gateway)
ec.set(fit01, "identity", user_identity)
ec.set(fit01, "cleanExperiment", True)
ec.set(fit01, "cleanProcesses", True)
ec.deploy(fit01)

# creating the fit02 node 
fit02 = ec.register_resource("linux::Node")
ec.set(fit02, "username", user02)
ec.set(fit02, "hostname", host02)
ec.set(fit02, "gateway", host_gateway)
ec.set(fit02, "gatewayUser", user_gateway)
ec.set(fit02, "identity", user_identity)
ec.set(fit02, "cleanExperiment", True)
ec.set(fit02, "cleanProcesses", True)
ec.deploy(fit02)

# application to copy file from local to gateway
app_local = ec.register_resource("linux::Application")
cmd  = 'scp {}{} {}@{}:{}{}; '.format(local_dir, file, user_gateway, host_gateway, gateway_dir, file)
ec.set(app_local, "command", cmd)
ec.register_connection(app_local, local)

# application to copy file to fit01 from gateway
app_gateway = ec.register_resource("linux::Application")
cmd  = 'scp {}{} {}@{}:{}{}; '.format(gateway_dir, file, user01, host01, host01_dir, file)
ec.set(app_gateway, "command", cmd)
ec.register_connection(app_gateway, gateway)

# fit01 node will send the file to fit 02 node
app_fit01 = ec.register_resource("linux::Application")
cmd = 'nc {} {} < {}{}'.format(host01, port, host01_dir, file)
ec.set(app_fit01, "depends", "netcat")
ec.set(app_fit01, "command", cmd)
ec.register_connection(app_fit01, fit01)

# fit02 node will rexeive the file from fit 01 node
app_fit02 = ec.register_resource("linux::Application")
cmd = 'nc -dl {} > {}{}'.format(port, host02_dir, file)
ec.set(app_fit02, "depends", "netcat")
ec.set(app_fit02, "command", cmd)
ec.register_connection(app_fit02, fit02)

# defining that the node gateway can copy the file to fit01 only after the file is copied to it from local
ec.register_condition(app_gateway, ResourceAction.START, app_local, ResourceState.STARTED) 

# defining that the node gateway can copy the file to fit01 only after the file is copied to it from local
ec.register_condition(app_fit01, ResourceAction.START, app_gateway, ResourceState.STARTED) 

# defining that the node fit01 can send only after node fit02 is listening
ec.register_condition(app_fit01, ResourceAction.START, app_fit02, ResourceState.STARTED) 

ec.deploy([app_local, app_gateway, app_fit01, app_fit02])
ec.wait_finished([app_local, app_gateway, app_fit01, app_fit02])

# recovering the results
print "\n--- INFO: output fit01:"
print ec.trace(app_fit01, "stdout")
print " "
print "\n--- INFO: output fit02:"
print ec.trace(app_fit02, "stdout")

# shutting down the experiment
ec.shutdown()

