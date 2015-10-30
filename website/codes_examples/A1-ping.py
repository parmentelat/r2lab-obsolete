#!/usr/bin/env python

# including nepi library and other required packages
from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState
from nepi.util.sshfuncs import logger
import os

# setting up the default host, onelab user and shh key credential
host  = 'faraday.inria.fr'
user  = '[your_onelab_user]'
key   = '~/.ssh/[your_public_ssh_key]'

# creating a new ExperimentController (EC) to manage the experiment
ec = ExperimentController(exp_id="A1-ping")

# creating a node using the already filled credentials
# in this case we are creating the gateway node
# we are setting up the host, user and ssh key. 
node = ec.register_resource("linux::Node")
ec.set(node, "username", user)
ec.set(node, "hostname", host)
ec.set(node, "identity", key)
ec.set(node, "cleanExperiment", True)
ec.set(node, "cleanProcesses", True)
# deploying the node
ec.deploy(node)

# creating an application
app = ec.register_resource("linux::Application")
cmd = 'ping -c1 google.fr'
# given to the application a command to execute
ec.set(app, "command", cmd)
# registering the application to be executed in the node
ec.register_connection(app, node)
# deploying the application
ec.deploy(app)
# waiting the app finish its job
ec.wait_finished(app)

# recovering the results
print "\n--- INFO: output:"
print ec.trace(app, "stdout")

# shutting down the experiment
ec.shutdown()