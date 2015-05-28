# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
#     ***** talk_node_c.py
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
#     This file contains a class that inherits ExperimentController from Nepi framework
#     used at INRIA testbed (R2Lab) with Nitos nodes. The class add an identification attribute
#     and a couple of main commands to execute Nepi reusing codes which create and deploy nodes     
#     To have access of the class just include the file in your script file like:
#     from talk_node_c import TalkNodeHelper
# 
# Author: Mario ZANCANARO <mario.zancanaro@inria.fr>
# 

from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceState, ResourceAction

class TalkNodeHelper(ExperimentController): 
  
    def __init__(self, id):
        self._interface = None

        super(TalkNodeHelper, self).__init__()

    #creates a new NEPI node in gateway to coordinate the nodes
    def new_node_gateway(self, type='linux::Node', **kwargs):
        gateway         = kwargs.get('gateway')
        gateway_user    = kwargs.get('gateway_user')
        gateway_user_key= kwargs.get('gateway_user_key')

        node = self.register_resource(type)
        self.set(node, "identity", gateway_user_key)
        self.set(node, "username", gateway_user)
        self.set(node, "hostname", gateway)
        self.set(node, "cleanExperiment", True)

        self.the_gtw = node
        return node

    #creates a new NEPI node
    def new_node(self, type='linux::Node', **kwargs):
        gateway         = kwargs.get('gateway')
        gateway_user    = kwargs.get('gateway_user')
        gateway_user_key= kwargs.get('gateway_user_key')
        self.node_host  = kwargs.get('node_name')
        self.node_user  = kwargs.get('node_user')

        node = self.register_resource(type)
        self.set(node, "identity", gateway_user_key)
        self.set(node, "gateway", gateway)
        self.set(node, "gatewayUser", gateway_user)
        self.set(node, "username", self.node_user)
        self.set(node, "hostname", self.node_host)
        self.set(node, "cleanExperiment", True)
        return node

    # Gets the interface to execute
    @property
    def interface(self):
        return self._interface

    # Sets the interface to execute
    @interface.setter
    def interface(self, interface):
        interfaces = ['eth0', 'wlan1', 'wlan2', 'p2p1']
        if interface not in interfaces:
            raise Exception("invalid interface, must be {}".format(interfaces))

        self._interface = interface

    # Chance the interface to execute
    def change_interface(self, interface):
        self.interface = interface
    
    # Execution in both (gateway and nodes) once connected
    def free_command(self, cmd, node, type=None):
        if type is None:
            type = 'linux::Application'
        app = self.register_resource(type)

        if not self.interface == None:
            cmd = cmd + " -I {}".format(self.interface)

        self.set(app, "command", cmd)    
        self.register_connection(app, node)
        return app

    # Execution in both (gateway and nodes) once connected
    def simple_ping(self, times, node, type=None):
        print "--- + pinging "
        cmd = 'ping -c{} nepi.inria.fr'.format(times)
        return self.free_command(cmd, node, type)

    # Execution in gateway to reset the nodes
    def reset_node(self, ip, type=None):
        print "--- + reseting {}".format(ip)
        cmd = "curl {}/reset ".format(ip)
        return self.free_command(cmd, node, type)

    # Execution in gateway to obtain the info from node(s)
    def info_node(self, ip, type=None):
        print "--- + info {}".format(ip)
        cmd = "curl {}/info ".format(ip)
        return self.free_command(cmd, self.the_gtw, type)

    # Execution in gateway to turn on/off node(s)
    # actions  -> [on|off]
    def turn_node(self, ip, action, type=None):
        options = ['on','off']
        if action not in options:
            raise Exception("invalid option, must be {}".format(options))
            exit()
        
        print "--- + set {} action for node {}".format(action, ip)
        cmd = "curl {}/{} ".format(ip, action)
        return self.free_command(cmd, self.the_gtw, type)

    # Execution in node(s) to turn on/off wireless card(s)
    # actions  -> [up|down]
    # wlan     -> [1,2,...]
    def turn_wlan(self, wlan, action, node, type=None):
        options = ['up','down']
        if action not in options:
            raise Exception("invalid option, must be {}".format(options))
        wlans = [1,2]
        if wlan not in wlans:
            raise Exception("invalid wlan, must be {}".format(wlans))
           
        print "--- + set node {}, wlan{} as {}".format(self.node_host, wlan, action)
        cmd = "ifconfig wlan{} {}".format(wlan,action)
        cmd = cmd + "; ip link show wlan{} ".format(wlan)
        return self.free_command(cmd, node, type)

    # Execution in node(s) to show wireless card(s) status
    # wlan    -> [1,2,...]
    def status_wlan(self, wlan, node, type=None):
        wlans = [1,2]
        if wlan not in wlans:
            raise Exception("invalid wlan, must be {}".format(wlans))
        print "--- + status of wlan{} from node {}".format(wlan, self.node_host)
        cmd = "ip link show wlan{}".format(wlan)
        return self.free_command(cmd, node, type)


    # Execution the actions using NEPI framework
    def execute(self, apps): 
        self.deploy()
        self.wait_finished(apps)

        for ap in apps:
            print self.trace(ap, "stdout")
