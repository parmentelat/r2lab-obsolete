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
ec = ExperimentController(exp_id="B1-send-file")

# we want to run a command right in the r2lab gateway
# so we need to define ssh-related details for doing so
gateway_hostname  = 'faraday.inria.fr'
gateway_username  = 'onelab.inria.mario.tutorial'
gateway_key       = '~/.ssh/onelab.private'

# setting up the credentials for the nodes
host01 = 'fit01'
user01 = 'root'
host01_dir = '/home/'

host02 = 'fit02'
user02 = 'root'
host02_dir = '/home/'
port = 1234

local_dir   = '/local_path/'
local_file  = 'file.txt'
gateway_dir = '/gateway_path/'

# creating local
local   = ec.register_resource("linux::Node",
                                hostname = 'localhost',
                                cleanExperiment = True,
                                cleanProcesses = True,
                                autoDeploy = True)

# creating the gateway node
gateway = ec.register_resource("linux::Node",
                                username = gateway_username,
                                hostname = gateway_hostname,
                                identity = gateway_key,
                                cleanExperiment = True,
                                cleanProcesses = True,
                                autoDeploy = True)

# creating the fit01 node
fit01 	= ec.register_resource("linux::Node",
                            	username = user01,
                            	hostname = host01,
                            	gateway = gateway_hostname,
                            	gatewayUser = gateway_username,
                            	identity = gateway_key,
                            	cleanExperiment = True,
                            	cleanProcesses = True,
                                autoDeploy = True)

# creating the fit02 node
fit02   = ec.register_resource("linux::Node",
                            	username = user02,
                            	hostname = host02,
                            	gateway = gateway_hostname,
                            	gatewayUser = gateway_username,
                            	identity = gateway_key,
                            	cleanExperiment = True,
                            	cleanProcesses = True,
                                autoDeploy = True)

# application to copy file from local to gateway
cmd  = 'scp {}{} {}@{}:{}{}; '.\
       format(local_dir, local_file,
              gateway_username, gateway_hostname, gateway_dir, local_file)
app_local = ec.register_resource("linux::Application",
                                  command = cmd,
                                  autoDeploy = True,
                                  connectedTo = local)

# application to copy file to fit02 from gateway
cmd  = 'scp {}{} {}@{}:{}{}; '.\
       format(gateway_dir, local_file,
              user02, host02, host02_dir, local_file)
app_gateway = ec.register_resource("linux::Application",
                                    command = cmd,
                                    autoDeploy = True,
                                    connectedTo = gateway)

# fit01 will receive the file from fit02, then we start listening in the port
cmd = 'nc -dl {} > {}{}'.\
      format(port, host01_dir, local_file)
app_fit01 = ec.register_resource("linux::Application",
                                  depends = "netcat",
                                  command = cmd,
                                  autoDeploy = True,
                                  connectedTo = fit01)

# fit02 will send the file to fit01
cmd = 'nc {} {} < {}{}'.\
      format(host01, port, host02_dir, local_file)
app_fit02 = ec.register_resource("linux::Application",
                                  depends = "netcat",
                                  command = cmd,
                                  autoDeploy = True,
                                  connectedTo = fit02)

# fit02 will list the dir after all process
cmd = 'ls -la {}'.format(host02_dir)
app_fit02_ls = ec.register_resource("linux::Application",
                                     command = cmd,
                                     autoDeploy = True,
                                     connectedTo = fit02)

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
print ("\n--- INFO: listing directory on fit02:")
print (ec.trace(app_fit02_ls, "stdout"))

# shutting down the experiment
ec.shutdown()
