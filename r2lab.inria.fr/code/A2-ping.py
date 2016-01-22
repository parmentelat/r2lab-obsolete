#!/usr/bin/env python

# including nepi library and other required packages
from __future__ import print_function
from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState
from nepi.util.sshfuncs import logger
import os

# setting up the default host, onelab user and shh key credential
host_gateway  = 'faraday.inria.fr'
user_gateway  = '[your_onelab_user]'
user_identity = '~/.ssh/[your_public_ssh_key]'

# setting up the credentials for one fit01 node 
host01 = 'fit01'
user01 = 'root'

# creating a new ExperimentController (EC) to manage the experiment
ec = ExperimentController(exp_id="A2-ping")

# creating the gateway node
gateway = ec.register_resource("linux::Node",
                                username = user_gateway,
                                hostname = host_gateway,
                                identity = user_identity,
                                cleanExperiment = True,
                                cleanProcesses = True)
# deploying the gateway node
ec.deploy(gateway)

# creating the fit01 node
fit01   = ec.register_resource("linux::Node",
                                username = user01,
                                hostname = host01,
                                # to reach the fit01 node it must go through the gateway, so let's assign the gateway infos
                                gateway = host_gateway,
                                gatewayUser = user_gateway,
                                identity = user_identity,
                                cleanExperiment = True,
                                cleanProcesses = True)
# deploying the fit01 node
ec.deploy(fit01)

# creating an application to ping the control inteface of fit01 node from the gateway
app = ec.register_resource("linux::Application")
cmd = 'ping -c1 192.168.03.01'
# given to the application a command to execute
ec.set(app, "command", cmd)
# registering the application to be executed in the fit01 node
ec.register_connection(app, gateway)
# deploying the application
ec.deploy(app)
# waiting the app finish its job
ec.wait_finished(app)

# recovering the results
print ("\n--- INFO: output:")
print (ec.trace(app, "stdout"))

# shutting down the experiment
ec.shutdown()
