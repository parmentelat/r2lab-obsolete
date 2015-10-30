#!/usr/bin/env python

# including nepi library and other required packages
from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState
from nepi.util.sshfuncs import logger
import os

# setting up the default host, onelab user and shh key credential
host_gateway  = 'faraday.inria.fr'
user_gateway  = '[your_onelab_user]'
user_identity = '~/.ssh/[your_public_ssh_key]'
gateway_dir 	= '/home/[your_onelab_user]/'

# setting up the credentials for the nodes 
host01 = 'fit01'
user01 = 'root'
host01_dir = '/home/'

host02 = 'fit02'
user02 = 'root'
host02_dir = '/home/'
port   = 1234

local_file = '[some_file.txt]'
local_dir  = '[some_file_path]'

# creating a new ExperimentController (EC) to manage the experiment
ec = ExperimentController(exp_id="B1-send-file")

# creating local
local = ec.register_resource("linux::Node")
ec.set(local, "hostname", "localhost")
ec.set(local, "cleanExperiment", True)
ec.set(local, "cleanProcesses", True)

# creating the gateway node
gateway = ec.register_resource("linux::Node")
ec.set(gateway, "username", user_gateway)
ec.set(gateway, "hostname", host_gateway)
ec.set(gateway, "identity", user_identity)
ec.set(gateway, "cleanExperiment", True)
ec.set(gateway, "cleanProcesses", True)

# creating the fit01 node
fit01 = ec.register_resource("linux::Node")
ec.set(fit01, "username", user01)
ec.set(fit01, "hostname", host01)
ec.set(fit01, "gateway", host_gateway)
ec.set(fit01, "gatewayUser", user_gateway)
ec.set(fit01, "identity", user_identity)
ec.set(fit01, "cleanExperiment", True)
ec.set(fit01, "cleanProcesses", True)

# creating the fit02 node 
fit02 = ec.register_resource("linux::Node")
ec.set(fit02, "username", user02)
ec.set(fit02, "hostname", host02)
ec.set(fit02, "gateway", host_gateway)
ec.set(fit02, "gatewayUser", user_gateway)
ec.set(fit02, "identity", user_identity)
ec.set(fit02, "cleanExperiment", True)
ec.set(fit02, "cleanProcesses", True)

# application to copy file from local to gateway
app_local = ec.register_resource("linux::Application")
cmd  = 'scp {}{} {}@{}:{}{}; '.format(local_dir, local_file, user_gateway, host_gateway, gateway_dir, local_file)
ec.set(app_local, "command", cmd)
ec.register_connection(app_local, local)

# application to copy file to fit02 from gateway
app_gateway = ec.register_resource("linux::Application")
cmd  = 'scp {}{} {}@{}:{}{}; '.format(gateway_dir, local_file, user02, host02, host02_dir, local_file)
ec.set(app_gateway, "command", cmd)
ec.register_connection(app_gateway, gateway)

# fit01 will receive the file from fit02, then we start listening in the port
app_fit01 = ec.register_resource("linux::Application")
cmd = 'nc -dl {} > {}{}'.format(port, host01_dir, local_file)
ec.set(app_fit01, "depends", "netcat")
ec.set(app_fit01, "command", cmd)
ec.register_connection(app_fit01, fit01)

# fit02 will send the file to fit01 
app_fit02 = ec.register_resource("linux::Application")
cmd = 'nc {} {} < {}{}'.format(host01, port, host02_dir, local_file)
ec.set(app_fit02, "depends", "netcat")
ec.set(app_fit02, "command", cmd)
ec.register_connection(app_fit02, fit02)

# fit02 will list the dir after all process 
app_fit02_ls = ec.register_resource("linux::Application")
cmd = 'ls -la {}'.format(host02_dir)
ec.set(app_fit02_ls, "command", cmd)
ec.register_connection(app_fit02_ls, fit02)

# defining that the node gateway can copy the file to fit02 only after the file is copied to it from local
ec.register_condition(app_gateway, ResourceAction.START, app_local, ResourceState.STOPPED) 

# defining that the node ftt02 can send the file to fit01 only after the file is copied to it from gateway
ec.register_condition(app_fit02, ResourceAction.START, app_gateway, ResourceState.STOPPED) 

# defining that the node fit02 can send only after node fit01 is listening
ec.register_condition(app_fit02, ResourceAction.START, app_fit01, ResourceState.STARTED)

# defining that the node fit02 can send only after node fit01 is listening
ec.register_condition(app_fit02_ls, ResourceAction.START, app_fit02, ResourceState.STOPPED) 

# deploy all applications
ec.deploy([local, gateway, fit01, fit02, app_local, app_gateway, app_fit01, app_fit02, app_fit02_ls])

#wait ls application to recovery the results and present after
ec.wait_finished(app_fit02_ls)

# recovering the results
print "\n--- INFO: listing directory on fit02:"
print ec.trace(app_fit02_ls, "stdout")

# shutting down the experiment
ec.shutdown()
