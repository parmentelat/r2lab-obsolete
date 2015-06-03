#!/usr/bin/env python
#
#     ***** r2lab_testbed_reset_eth.py
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
## This is a maintenance script used to reset the nodes from
## INRIA testbed (R2Lab) before running a OMF experiment using Nitos nodes.
## This script restarts the nodes, then starts the wlan interface without configuring it
#
# Example of how to run this experiment (replace with your information):
#
# $ cd <path-to-nepi>/examples/linux [where the script has been copied]
# python r2lab_testbed_reset_eth.py -H <fitXX,fitZZ,..> -U <r2lab-node-username> -i <ssh-key> -g <r2lab-gateway> -u <r2lab-slicename>
# python r2lab_testbed_reset_eth.py -H fit12,fit18 -U root -i ~/.ssh -g faraday.inria.fr  -u root
#

from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState

from argparse import ArgumentParser
import os
import time

usage = ("usage: %prog -H <list-of-nodes> -U <node-username> -i <ssh-key> -g <r2lab-gateway> -u <slicename>")

parser = ArgumentParser(usage = usage)
parser.add_argument("-H", "--hosts", dest="hosts", 
        help="Space separated list of hosts")
parser.add_argument("-U", "--username", dest="username", 
        help="Username for the nodes (usually root)", default="root" )
parser.add_argument("-g", "--gateway", dest="gateway", 
        help="Nitos gateway hostname", default="faraday.inria.fr")
parser.add_argument("-u", "--gateway-user", dest="gateway_username", 
        help="R2lab gateway username (slicename)", default="root")
parser.add_argument("-i", "--ssh-key", dest="ssh_key", 
        help="Path to private SSH key to be used for connection")
args = parser.parse_args()

hosts = args.hosts
username = args.username
gateway = args.gateway
gateway_username = args.gateway_username
identity = args.ssh_key

print "hosts" , hosts
print "username" , username
print "gateway" , gateway
print "gateway_username" , gateway_username
print "identity" , identity

apps = []

random = (time.strftime("%m%d%Y%H%M%S"))
ec = ExperimentController('r2lab_reset_eth'+random)

gw_node = ec.register_resource("linux::Node")
ec.set(gw_node, "username", gateway_username)
ec.set(gw_node, "hostname", gateway)
ec.set(gw_node, "identity", identity)
ec.set(gw_node, "cleanExperiment", True)
ec.set(gw_node, "cleanProcesses", False)
ec.set(gw_node, "cleanProcessesAfter", False)

reboot_cmd = "omf6 tell -a reset -t %s" % hosts 
print "reboot_cmd =" , reboot_cmd
reboot_app = ec.register_resource("linux::Application")
ec.set(reboot_app, "command", reboot_cmd)
ec.register_connection(reboot_app, gw_node)

hosts = hosts.split(",")

for hostname in hosts:
    host = hostname.split(".")[-1]
    print "host", host
    node = ec.register_resource("linux::Node")
    ec.set(node, "username", username)
    ec.set(node, "hostname", host)
    ec.set(node, "identity", identity)
    ec.set(node, "gateway", gateway)
    ec.set(node, "gatewayUser", gateway_username)
    ec.set(node, "cleanExperiment", True)
    ec.register_condition(node, ResourceAction.DEPLOY, reboot_app, 
            ResourceState.STOPPED, time="30s") 
    ping_cmd = "ping -c4 192.168.3.100"
    ping_app = ec.register_resource("linux::Application")
    ec.set(ping_app, "command", ping_cmd)
    ec.register_connection(ping_app, node)
    apps.append(ping_app)
    ec.register_condition(ping_app, ResourceAction.START, 
				reboot_app, ResourceState.STOPPED, time="15s")
    modprobe_app = ec.register_resource("linux::Application")
    ec.set(modprobe_app, "command", "modprobe ath9k;lsmod | grep ath; ifconfig")
    ec.register_connection(modprobe_app, node)
    apps.append(modprobe_app)
    ec.register_condition(modprobe_app, ResourceAction.START, 
			ping_app, ResourceState.STOPPED) 
				

print "This might take time..."

ec.deploy(wait_all_ready=False)
print "Started"
ec.wait_finished(apps)
print ec.trace(reboot_app, "stdout")

for app in apps:
    print ec.trace(app, "stdout")

ec.shutdown()

