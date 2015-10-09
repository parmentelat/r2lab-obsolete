#!/usr/bin/env python
#
#
#    NEPI, a framework to manage network experiments
#    Copyright (C) 2015 INRIA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as
#    published by the Free Software Foundation;
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#      Author: Alina Quereilhac <alina.quereilhac@inria.fr>
#              Maksym Gabielkov <maksym.gabielkovc@inria.fr>
#
#
# This is a script used to simulate a sender-receiver file between two nodes A and B from
# INRIA testbed (R2Lab) before running a OMF experiment using Nitos nodes.
# For simplicity, the file should be already present in the node A (sender) and it call file1.txt
#
# Example of how to run this experiment (replace with your information):
#
# $ cd <path-to-nepi>/examples/linux [where the script has been copied]
# python sender_receiver.py -N <nodeA,nodeB> -U <host_username> -i <ssh-key> -g <gateway> -u <gateway_username>
#
#
from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState
import os
from nepi.util.sshfuncs import logger
import logging
from argparse import ArgumentParser

usage = ("usage: %prog -N <node-A-and-Node-B> -U <node-username> -i <ssh-key> -g <gateway> -u <slicename>")

parser = ArgumentParser(usage = usage)
parser.add_argument("-N", "--nodes", dest="nodes", 
        help="Comma separated list of nodes")
parser.add_argument("-U", "--username", dest="username", 
        help="Username for the nodes (usually root)", default="root" )
parser.add_argument("-g", "--gateway", dest="gateway", 
        help="Gateway hostname", default="faraday.inria.fr")
parser.add_argument("-u", "--gateway-user", dest="gateway_username", 
        help="Gateway username", default="root")
parser.add_argument("-i", "--ssh-key", dest="ssh_key", 
        help="Path to private SSH key to be used for connection")

args = parser.parse_args()

# receive the arguments from command line
nodes       = args.nodes.split(',')
username    = args.username
gateway     = args.gateway
gateway_username = args.gateway_username
identity    = args.ssh_key

name_nodeA = nodes[0]
name_nodeB = nodes[1]
apps  = []

# create the experiment controller
ec = ExperimentController(exp_id="NC")

# create the node A listener
nodeA = ec.register_resource("linux::Node")
ec.set(nodeA, "username", username)
ec.set(nodeA, "hostname", name_nodeA)
ec.set(nodeA, "identity", identity)
ec.set(nodeA, "gateway", gateway)
ec.set(nodeA, "gatewayUser", gateway_username)
ec.set(nodeA, "cleanExperiment", True)

# create the node B sender
nodeB = ec.register_resource("linux::Node")
ec.set(nodeB, "username", username)
ec.set(nodeB, "hostname", name_nodeA)
ec.set(nodeB, "identity", identity)
ec.set(nodeB, "gateway", gateway)
ec.set(nodeB, "gatewayUser", gateway_username)
ec.set(nodeB, "cleanExperiment", True)

# files path and port number
file_from   = '/home/file1.txt'
file_to     = '/home/file1.txt'
receiver    = name_nodeA
port        = 1234

# create the application to listen in node A at port 1234
receiver_cmd = "nc -dl {} > {}".format(port, file_to)
receiver_app = ec.register_resource("linux::Application")
ec.set(receiver_app, "depends", "netcat")
ec.set(receiver_app, "command", receiver_cmd)
ec.register_connection(receiver_app, nodeA)
apps.append(receiver_app)

# create the application in node B to send the file to node A at port 1234
sender_cmd = "cat {} | nc {} {} ".format(file_from, receiver, port)
sender_app = ec.register_resource("linux::Application")
ec.set(sender_app, "depends", "netcat")
ec.set(sender_app, "command", sender_cmd)
ec.register_connection(sender_app, nodeB)
apps.append(sender_app)

# defining that the node B can send only after node A is listening
ec.register_condition(sender_app, ResourceAction.START, receiver_app, ResourceState.STARTED) 

# deploy the experiment
ec.deploy([nodeA, nodeB, receiver_app, sender_app])

# wait for the experiment exit
ec.wait_finished(apps)

# recover and print the results
for app in apps:
    print ec.trace(app, "stdout")

# destroy the controller
ec.shutdown()