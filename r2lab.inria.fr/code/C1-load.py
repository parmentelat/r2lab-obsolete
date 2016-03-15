#!/usr/bin/env python3

# including nepi library and other required packages
from __future__ import print_function
from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState
from nepi.util.sshfuncs import logger
import os

# setting up the default host, onelab user and shh key credential
gateway_hostname  = 'faraday.inria.fr'
gateway_username  = 'onelab.inria.mario.tutorial'
gateway_key       = '~/.ssh/onelab.private'

# setting up the credentials for the nodes
host01 = 'fit01'
user01 = 'root'

# distro version. Could be: 'ubuntu-14.10.ndz' or 'ubuntu-15.04.ndz' or 'fedora-21.ndz' or 'fedora-22.ndz'
version = 'fedora-21.ndz'

# creating a new ExperimentController (EC) to manage the experiment
ec = ExperimentController(exp_id="C1-load")

# creating the gateway node
gateway = ec.register_resource("linux::Node",
                                username = gateway_username,
                                hostname = gateway_hostname,
                                identity = gateway_key,
                                cleanExperiment = True,
                                cleanProcesses = True)
ec.deploy(gateway)

# application to copy load at fit01 a fresh distro
cmd  = 'rhubarbe-load {} -i {};'.format(host01, version)
app_gateway = ec.register_resource("linux::Application",
                                    command = cmd)
ec.register_connection(app_gateway, gateway)
ec.deploy(app_gateway)

#wait application finish
ec.wait_finished(app_gateway)

# creating the fit01 node
fit01   = ec.register_resource("linux::Node",
                                username = user01,
                                hostname = host01,
                                gateway = gateway_hostname,
                                gatewayUser = gateway_username,
                                identity = gateway_key,
                                cleanExperiment = True,
                                cleanProcesses = True)
ec.deploy(fit01)

# fit01 will check for the current version
cmd = "cat /etc/*-release | uniq -u | awk /PRETTY_NAME=/ | awk -F= '{print $2}'"
app_fit01 = ec.register_resource("linux::Application",
                                  command = cmd)
ec.register_connection(app_fit01, fit01)
ec.deploy(app_fit01)

#wait application to recovery the results
ec.wait_finished(app_fit01)

# recovering the results
print ("\n--- INFO: listing fit01 distro:")
print (ec.trace(app_fit01, "stdout"))

# shutting down the experiment
ec.shutdown()
