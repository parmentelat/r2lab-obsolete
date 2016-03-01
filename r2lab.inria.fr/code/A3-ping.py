#!/usr/bin/env python

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
ec = ExperimentController(exp_id="A3-ping")

# we want to run a command right in the r2lab gateway
# so we need to define ssh-related details for doing so
gateway_hostname  = 'faraday.inria.fr'
gateway_username  = 'onelab.inria.mario.tutorial'
gateway_key       = '~/.ssh/onelab.private'

fit01 = ec.register_resource("linux::Node",
                            username = 'root',
                            hostname = 'fit01',
                            gateway = host_gateway,
                            gatewayUser = user_gateway,
                            identity = user_identity,
                            cleanExperiment = True,
                            cleanProcesses = True)
ec.deploy(fit01)

fit02 = ec.register_resource("linux::Node",
                             username = 'root',
                             hostname = 'fit02',
                             gateway = host_gateway,
                             gatewayUser = user_gateway,
                             identity = user_identity,
                             cleanExperiment = True,
                             cleanProcesses = True)
ec.deploy(fit02)

# creating an application
# application to setup (wired) data interface on fit01 node
cmd = 'ip link set dev data down; dhclient data;'
app_fit01 = ec.register_resource("linux::Application",
                                 command=cmd)
ec.deploy(app_fit01)

# connect app to node
ec.register_connection(app_fit01, fit01)
# execute this bit and wait for completion
ec.wait_finished(app_fit01)

# application to setup data interface on fit02 node
cmd = 'ip link set dev data down; dhclient data;'
app_fit02 = ec.register_resource("linux::Application",
                                 command=cmd)
ec.deploy(app_fit02)

ec.register_connection(app_fit02, fit02)
# execute this bit and wait for completion
ec.wait_finished(app_fit02)

# creating an application to ping the wired
# data interface of fit02 from the fit01
# FYI the actual IP here would be 192.168.2.2
cmd = 'ping -c1 data02 ; '
app = ec.register_resource("linux::Application",
                           command=cmd)
ec.register_connection(app, fit01)
ec.deploy(app)
ec.wait_finished(app)

# recovering the results
print ("--- INFO : experiment output:",
       ec.trace(app, "stdout"))

# shutting down the experiment
ec.shutdown()
