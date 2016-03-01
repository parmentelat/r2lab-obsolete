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
ec = ExperimentController(exp_id="A2-ping")

# we want to run a command right in the r2lab gateway
# so we need to define ssh-related details for doing so
gateway_hostname  = 'faraday.inria.fr'
gateway_username  = 'onelab.inria.mario.tutorial'
gateway_key       = '~/.ssh/onelab.private'

# creating a node object using our credentials
# this time we want to reach a node in R2lab through the gateway
node = ec.register_resource("linux::Node",
                            # from the gateway, anyone can reach any node
                            # using the root account
                            username = 'root',
                            hostname = 'fit01',
                            # credentials to use for logging into the gateway
                            # in the first place
                            gateway = gateway_hostname,
                            gatewayUser = gateway_username,
                            identity = gateway_key,
                            # recommended settings
                            cleanExperiment = True,
                            cleanProcesses = True)
ec.deploy(node)

# creating an application
app = ec.register_resource("linux::Application",
                           # the command to execute
                           command='ping -c1 faraday.inria.fr')
ec.deploy(app)

# connect app to node
ec.register_connection(app, node)

# and finally waiting for the app to finish its job
ec.wait_finished(app)

# recovering the results
print ("--- INFO : experiment output:",
       ec.trace(app, "stdout"))

# shutting down the experiment
ec.shutdown()
