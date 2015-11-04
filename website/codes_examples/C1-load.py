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

# setting up the credentials for the nodes 
host01 = 'fit01'
user01 = 'root'

# distro version. Could be: 'ubuntu-14.10.ndz' or 'ubuntu-15.04.ndz' or 'fedora-21.ndz' or 'fedora-22.ndz'
version = 'fedora-21.ndz'

# creating a new ExperimentController (EC) to manage the experiment
ec = ExperimentController()

# creating the gateway node
gateway = ec.register_resource("linux::Node")
ec.set(gateway, "username", user_gateway)
ec.set(gateway, "hostname", host_gateway)
ec.set(gateway, "identity", user_identity)
ec.set(gateway, "cleanExperiment", True)
ec.set(gateway, "cleanProcesses", True)
ec.deploy(gateway)

# application to copy load at fit01 a fresh distro
app_gateway = ec.register_resource("linux::Application")
cmd  = 'omf6 load -t {} -i {};'.format(host01, version)
ec.set(app_gateway, "command", cmd)
ec.register_connection(app_gateway, gateway)
ec.deploy(app_gateway)

#wait application finish
ec.wait_finished(app_gateway)

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

# fit01 will check for the current version
app_fit01 = ec.register_resource("linux::Application")
cmd = "cat /etc/*-release | uniq -u | awk /PRETTY_NAME=/ | awk -F= '{print $2}'"
ec.set(app_fit01, "command", cmd)
ec.register_connection(app_fit01, fit01)
ec.deploy(app_fit01)

#wait application to recovery the results 
ec.wait_finished(app_fit01)

# recovering the results
print "\n--- INFO: listing fit01 distro:"
print ec.trace(app_fit01, "stdout")

# shutting down the experiment
ec.shutdown()