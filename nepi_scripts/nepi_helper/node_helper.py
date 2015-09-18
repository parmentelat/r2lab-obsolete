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
# Author: Alina Quereilhac <alina.quereilhac@inria.fr>
#         Maksym Gabielkov <maksym.gabielkovc@inria.fr>
#
# Author file: Mario Zancanaro <mario.zancanaro@inria.fr>
#
# This is a maintenance script used to make group operations at the nodes from
# INRIA testbed (R2Lab) before running a OMF experiment using Nitos nodes.
#
# Example of how to run this experiment (replace with your information):
#
# $ cd <path-to-nepi>/examples/linux [where the script has been copied]
# python node_helper.py -A <action> -N <fitXX,fitZZ,..> -U <r2lab-node-username> -i <ssh-key> -g <r2lab-gateway> -u <r2lab-slicename>
# python node_helper.py -A status -N fit10,fit26,fit223 -U root -i ~/.ssh/id_rsa -g faraday.inria.fr  -u mario
#

from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState
from nepi.util.sshfuncs import logger
from node_functions import *
from argparse import ArgumentParser


usage = ("usage: %prog -A <action-to-execute> -N <list-of-nodes> -U <node-username> -i <ssh-key> -g <gateway> -u <slicename>")

parser = ArgumentParser(usage = usage)
parser.add_argument("-A", "--action", dest="action", 
        help="Action to execute in the nodes")
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

action      = args.action
nodes       = args.nodes
username    = args.username
gateway     = args.gateway
gateway_username = args.gateway_username
identity    = args.ssh_key
connection_info = { 'nodes':nodes, 'username':username, 'gateway':gateway, 'gateway_username':gateway_username, 'identity':identity }


if "status" == action or "st" == action:
    # check status of each node from the list
    result = status(nodes, connection_info)
elif "on" == action:
    # turn on each node from the list
    result = on(nodes, connection_info)
elif "off" == action:
    # turn off each node from the list
    result = off(nodes, connection_info)
elif "reset" == action:
    # reset each node from the list
    result = reset(nodes, connection_info)
elif "load-u1410" == action:
    # load image in each node from the list
    result = load(nodes, 'ubuntu-14.10.ndz', connection_info)
elif "load-u1504" == action:
    # load image in each node from the list
    result = load(nodes, 'ubuntu-15.04.ndz', connection_info)
elif "load-f21" == action:
    # load image in each node from the list
    result = load(nodes, 'fedora-21.ndz', connection_info)
elif "alive" == action or "cmc-on-off" == action:
    # check if each node from the list anwer a ping in the CM card
    result = alive(nodes, connection_info)
elif "answer" == action or "control-ping" == action:
    # check if each node from the list anwer a ping
    result = answer(nodes, connection_info)
elif "info" == action or "os-release" == action or "control-ssh" == action:
    # check the S.O. info
    result = info(nodes, connection_info)
else:
    print "invalid option: {}".format(action)
    exit()

