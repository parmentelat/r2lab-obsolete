#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
#     This file contains a class that inherits ExperimentController from NEPI framework
#     used at INRIA testbed (R2Lab) with Nitos nodes.  
#               
# Author: Mario ZANCANARO <mario.zancanaro@inria.fr>
# 

from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceState, ResourceAction

class DataConnection(object):
    """Informations to connect the nodes and the gateway"""
    def __init__(self, username, hostname, identity, gateway_user=None, gateway=None):
        super(DataConnection, self).__init__()
        self.username     = username
        self.hostname     = hostname
        self.identity     = identity
        self.gateway_user = gateway_user
        self.gateway      = gateway

class Simulation(object): 

    def __init__(self, id=None):
        """ Class that holds all simulations through using ExperimentController of NEPI Framework """
        super(Simulation, self).__init__()
        self._id = id
        self._ec = ExperimentController(id)
         
    @staticmethod
    def new(id=None):        
        """ Instantiate the simulation """
        simulation = Simulation(id=None)
        return simulation

    @property
    def ec(self):
        """ Returns the ExperimentController associated to the simulation """
        return self._ec()

    def connect_gateway(self):
        """ Set the connection through the gateway """
        gateway = self._ec.register_resource('linux::Node')    
        
        self._ec.set(gateway, "username", 'mario')
        self._ec.set(gateway, "hostname", 'faraday.inria.fr')      
        self._ec.set(gateway, "identity", '~/.ssh/id_rsa')
        self._ec.set(gateway, "cleanExperiment", True)

        return gateway

    def connect_node(self, nd):
        """ Set the connection through the node  """
        node = self._ec.register_resource('linux::Node')    

        self._ec.set(node, "identity", '~/.ssh/id_rsa')
        self._ec.set(node, "gateway",  'faraday.inria.fr')
        self._ec.set(node, "gatewayUser", 'mario')
        self._ec.set(node, "username", 'root')
        self._ec.set(node, "hostname", nd.node)
        self._ec.set(node, "cleanExperiment", True)

        return node

    def create_app(self, cmd, node):
        """ Set the application resource of NEPI  """
        app = self._ec.register_resource('linux::Application')
        self._ec.set(app, "command", cmd)    
        self._ec.register_connection(app, node)

        return app

    def execute(self, nd):
        """ Execute the commands of each node instantiate and push to NEPI framework """
        list_of_commands_by_node = range(len(nd.commands.command)) 

        for i in list_of_commands_by_node:
            """ For each command associated at each node """
            place = nd.commands.execute_at[i]
            cmd   = nd.commands.command[i]    

            if "NODE" in RunAt.place(place):
               node = self.connect_node(nd)
            else:
               node = self.connect_gateway()
    
            app  = self.create_app(cmd, node)
                
            self._ec.deploy()
            self._ec.wait_finished(app)
            print self._ec.trace(app, "stdout")
                

class RunAt(object):
    """ Defines where the command will execute """
    NODE    = 1
    GATEWAY = 2

    @staticmethod
    def place(source):
        """ Help """
        if source is 1:
            return "NODE"
        if  source is 2:
            return "GATEWAY"
    


class StackCommand(object): 
    
    def __init__(self):
        """ Class to store the commandas in a stack structure """
        super(StackCommand, self).__init__()
        self._counter    = list()
        self._command    = list()
        self._execute_at = list()

    def add(self, command, execute_at):
        """ Adds commands to the stack """
        self._execute_at.append(execute_at)
        self._command.append(command)
        self._counter.append(len(self._counter) + 1)
    
    def drop(self, indice):
        """ Remove commands from the stack """
        real_index = self._counter.index(indice)
        
        self._counter.pop(real_index)
        self._command.pop(real_index)
        self._execute_at.pop(real_index)

    @property
    def counter(self):
        """ Returns counter """
        return self._counter

    @property
    def command(self):
        """ Returns command """
        return self._command

    @property
    def execute_at(self):
        """ Returns execute_at """
        return self._execute_at

    def queue(self):
        """ Returns the queue of commands """
        commands = []
        for i in range(len(self._command)):
            commands.append("[ {} - {} : {} ]".format(self._counter[i], self._command[i], RunAt.place(self._execute_at[i])))
        return commands


class Node(object): 

    def __init__(self, node):
        """ Creates a abstract node object to operates in NEPI """
        super(Node, self).__init__()
        self._ip            = self.ask_ip(node)
        self._node          = node
        self._interface     = None
        self._channel       = None
        self._commands      = StackCommand()

    @staticmethod
    def new(node):
        """ Instantiate the node """
        node = Node(node)
        return node

    @property
    def node(self):
        """ Returns node """
        return self._node

    @property
    def commands(self):
        """ Returns commands """
        return self._commands

    @property
    def type(self):
        """ Returns type """
        return self._type

    @node.setter
    def node(self, node):
        """ Sets node name """
        if valid_node(node):
            self._node = node

    @property
    def ip(self):
        """ Returns ip of node """
        return self._ip

    @property
    def interface(self):
        """ Returns interface """
        return self._interface

    @interface.setter
    def interface(self, interface):
        """ Sets interface """
        if valid_interface(interface):
            self._interface = interface

    @property
    def channel(self):
        """ Returns channel """
        return self._channel

    @channel.setter
    def channel(self, channel):
        """ Sets channel """
        if valid_channel(channel):
            self._channel = channel

    def on(self):
        """ Turns node on """
        execute = RunAt.GATEWAY
        cmd = "curl {}/on ".format(self.ip)
        self._commands.add(cmd, execute)

    def off(self):
        """ Turns node off """
        execute = RunAt.GATEWAY
        cmd = "curl {}/off ".format(self.ip)
        self._commands.add(cmd, execute)

    def ping(self, target, times=1):
        """ Create a single ping command """
        execute = RunAt.NODE
        cmd = "ping -c {} {} ".format(times, target)
        self._commands.add(cmd, execute)

    def free_command(self, command):
        """ Receives a command to execute """
        execute = RunAt.NODE
        cmd = command
        self._commands.add(cmd, execute)

    @staticmethod
    def ask_ip(alias):
        """ Returns the ip from the node alias [fitXX] """
        prefix = '192.168.1.xx'
        alias = alias.lower().replace('fit', '')

        try:
            int(alias)
        except Exception, e:
            raise Exception("error in ip convertion")
        
        ip = prefix.replace('xx', alias)
        return ip

    @staticmethod
    def ask_alias(ip):
        """ Returns the alias from the ip adress """
        prefix = 'Fitxx'
        
        if not valid_ip(ip):
            raise Exception("error in ip convertion")

        ip = ip[ip.rfind('.') + 1 : len(ip)]
        ip = str(ip).zfill(2)
        alias = prefix.replace('xx', ip)
        return alias

    @staticmethod
    def valid_interface(interface):
        """ Check if interface is in the list of availables """
        interfaces = ['eth0', 'wlan1', 'wlan2', 'p2p1']
        if interface.lower() not in interfaces:
            raise Exception("invalid interface, must be {}".format(interfaces))
            return False
        else:
            return interface

    @staticmethod
    def valid_channel(channel):
        """ Check if channel is in the list of availables """
        channels = ['1', '2', '3', '4']
        if channel not in channels:
            raise Exception("invalid channel, must be {}".format(channels))
            return False
        else:
            return channel

    @staticmethod
    def valid_ip(channel):
        """ Check if ip valid """
        #TODO
        return True


           
