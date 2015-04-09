#!/usr/bin/env python
#
#     ***** r2lab_testbed_wlping.py
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
# Example of how to run this experiment (replace with your information):
#
# $ cd <path-to-nepi>/examples/linux [where the script has been copied]
# python r2lab_testbed_wlping.py -x <fitXX> -y <fitYY> -c <channel> -e <essid> -u <r2lab-slicename> -i <ssh-key> -g <r2lab-gateway> -U <r2lab-node-username>
# python r2lab_testbed_wlping.py -x fit12 -y fit18 -c 03 -e fitessai -u root -i ~/.ssh -g faraday.inria.fr -U root
#
#  Testbed : R2LAB
#
#     Node fitXX 
#          0
#          |
#          0
#     Node fitYY 
#
#     PING
#      - Experiment:
#        - t0 : Deployment and configuration
#        - t1 : Ping Start (3 packets sent over the air)
#        - t2 : Kill the application and retrieve traces
#

from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState

from optparse import OptionParser
import os

usage = ("usage: %prog -x <fitXX> -y <fitYY> -c <channel> -e <essid> -u <r2lab-username> -i <ssh-key> -g <r2lab-gateway> -U <r2lab-gateway-username>")

parser = OptionParser(usage = usage)
parser.add_option("-x", "--nodex", dest="nodex", 
        help="R2lab first reserved node "
            "(e.g. hostname must be of form: fitXX)", 
        type="str")
parser.add_option("-y", "--nodey", dest="nodey", 
        help="R2lab second reserved node "
            "(e.g. hostname must be of form: fitYY)", 
        type="str")
parser.add_option("-c", "--channel", dest="channel", 
        help="R2lab reserved channel",
        type="str")
parser.add_option("-e", "--essid", dest="wlessid", 
        help="WLAN essid, string",
        type="str", default="fitr2lab")
parser.add_option("-U", "--username", dest="username", 
        help="Username for the nodes (usually root)", 
        type="str", default="root" )
parser.add_option("-g", "--gateway", dest="gateway", 
        help="Nitos gateway hostname", 
        type="str", default="faraday.inria.fr")
parser.add_option("-u", "--gateway-user", dest="gateway_username", 
        help="R2lab gateway username (slicename)", 
        type="str", default="root")
parser.add_option("-i", "--ssh-key", dest="ssh_key", 
        help="Path to private SSH key to be used for connection", 
        type="str")
(options, args) = parser.parse_args()

if not options.channel or not options.nodex or not options.nodey :
    parser.error("Missing argument channel, nodex, or nodey!")

#hosts = options.hosts
nodex = options.nodex.split(".")[-1]
nodey = options.nodey.split(".")[-1]
channel = options.channel
wlessid = options.wlessid
username = options.username
gateway = options.gateway
gateway_username = options.gateway_username
identity = options.ssh_key


print "nodex " , nodex
print "nodey " , nodey
print "channel " , channel
print "wlessid " , wlessid
print "username " , username
print "gateway " , gateway
print "gateway_username " , gateway_username
print "identity " , identity

hosts = "%s,%s" % (nodex, nodey)
print "hosts " , hosts
apps = []

ec = ExperimentController(exp_id="r2lab_bootstrap")

gw_node = ec.register_resource("linux::Node")
ec.set(gw_node, "username", gateway_username)
ec.set(gw_node, "hostname", gateway)
ec.set(gw_node, "identity", identity)
ec.set(gw_node, "cleanExperiment", True)
ec.set(gw_node, "cleanProcesses", False)
ec.set(gw_node, "cleanProcessesAfter", False)

status_cmd = "omf6 stat -t %s" % hosts 
print "status_cmd =" , status_cmd
status_app = ec.register_resource("linux::Application")
ec.set(status_app, "command", status_cmd)
ec.register_connection(status_app, gw_node)

hosts = hosts.split(",")

for hostname in hosts:
    host = hostname.split(".")[-1]
    print "running host", host
    node = ec.register_resource("linux::Node")
    ec.set(node, "username", username)
    ec.set(node, "hostname", host)
    ec.set(node, "identity", identity)
    ec.set(node, "gateway", gateway)
    ec.set(node, "gatewayUser", gateway_username)
    ec.set(node, "cleanExperiment", True)
    ec.register_condition(node, ResourceAction.DEPLOY, 
            status_app, ResourceState.STOPPED, time="20s") 
    wlan_start_app = ec.register_resource("linux::Application")
    wlan_start_cmd = "ip address flush dev wlan0; iwconfig wlan0 mode ad-hoc channel %s essid %s; ip link set wlan0 up; ip addr add 172.16.1.%s/24 dev wlan0" % (channel, wlessid, host[-2:])
    ec.set(wlan_start_app, "command", wlan_start_cmd)
    ec.register_connection(wlan_start_app, node)
    apps.append(wlan_start_app)
    ec.register_condition(wlan_start_app, ResourceAction.START, 
            status_app, ResourceState.STOPPED, time="30s") 
    wlan_check_app = ec.register_resource("linux::Application")
    wlan_check_cmd = "ifconfig wlan0; iwconfig"
    ec.set(wlan_check_app, "command", wlan_check_cmd)
    ec.register_connection(wlan_check_app, node)
    apps.append(wlan_check_app)
    ec.register_condition(wlan_check_app, ResourceAction.START, 
            wlan_start_app, ResourceState.STOPPED, time="10s") 
    if host == nodex:
        # Create and Configure the PING Application
        app1 = ec.register_resource("linux::Application")
        #ec.set(app1, "appid", "Ping#1")
        ec.set(app1, "command", "/bin/ping -c3 172.16.1.%s" % nodey[-2:])
        ec.register_connection(app1, node)
        apps.append(app1)
        ec.register_condition(app1, ResourceAction.START, 
                      wlan_check_app, ResourceState.STOPPED, time="20s") 


print "This might take time..."

ec.deploy(wait_all_ready=False)
print "Started"
ec.wait_finished(apps)
print ec.trace(status_app, "stdout")

for app in apps:
    print ec.trace(app, "stdout")

ec.shutdown()

