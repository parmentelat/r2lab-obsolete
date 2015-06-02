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
import time




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
    """ Class that holds all simulations through using ExperimentController of NEPI Framework """
    
    def __init__(self, id):
        super(Simulation, self).__init__()
        self.id = id
        self.ec = ExperimentController(id)

    @staticmethod
    def new(id):        
        """ Instantiate the simulation """
        simulation = Simulation(id)
        return simulation

    def connect_gateway(self):
        """ Set the connection through the gateway """
        gateway = self.ec.register_resource('linux::Node')    
        
        self.ec.set(gateway, "username", 'mario')
        self.ec.set(gateway, "hostname", 'faraday.inria.fr')      
        self.ec.set(gateway, "identity", '~/.ssh/id_rsa')
        self.ec.set(gateway, "cleanExperiment", True)

        return gateway

    def connect_node(self, nd):
        """ Set the connection through the node  """
        node = self.ec.register_resource('linux::Node')    

        self.ec.set(node, "identity", '~/.ssh/id_rsa')
        self.ec.set(node, "gateway",  'faraday.inria.fr')
        self.ec.set(node, "gatewayUser", 'mario')
        self.ec.set(node, "username", 'root')
        self.ec.set(node, "hostname", nd.node)
        self.ec.set(node, "cleanExperiment", True)

        return node

    def create_app(self, cmd, node):
        """ Set the application resource of NEPI  """
        app = self.ec.register_resource('linux::Application')
        self.ec.set(app, "command", cmd)    
        self.ec.register_connection(app, node)

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

            self.ec.deploy()
            self.ec.wait_finished(app)
            
            print self.ec.trace(app, "stdout")




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
    """ Class to store the commandas in a stack structure """

    def __init__(self):
        super(StackCommand, self).__init__()
        self.counter    = list()
        self.command    = list()
        self.execute_at = list()

    def add(self, command, execute_at):
        """ Adds commands to the stack """
        self.execute_at.append(execute_at)
        self.command.append(command)
        self.counter.append(len(self.counter) + 1)
    
    def drop(self, indice):
        """ Remove commands from the stack """
        real_index = self.counter.index(indice)
        
        self.counter.pop(real_index)
        self.command.pop(real_index)
        self.execute_at.pop(real_index)

    def queue(self):
        """ Returns the queue of commands """
        commands = []
        for i in range(len(self.command)):
            commands.append("[ {} - {} : {} ]".format(self.counter[i], self.command[i], RunAt.place(self.execute_at[i])))
        return commands




class Node(object): 
    """ Creates a abstract node object to operates in NEPI """

    def __init__(self, node):
        super(Node, self).__init__()
        self.ip            = self.ask_ip(node)
        self.node          = node
        self.interface     = None
        self.channel       = None
        self.commands      = StackCommand()

    @staticmethod
    def new(node):
        """ Instantiate the node """
        node = Node(node)
        return node

    def on(self):
        """ Turns node on """
        execute = RunAt.GATEWAY
        cmd = "curl {}/on ".format(self.ip)
        self.commands.add(cmd, execute)

    def off(self):
        """ Turns node off """
        execute = RunAt.GATEWAY
        cmd = "curl {}/off ".format(self.ip)
        self.commands.add(cmd, execute)

    def ping(self, target, times=1):
        """ Create a single ping command """
        execute = RunAt.NODE
        cmd = "ping -c {} {} ".format(times, target)
        self.commands.add(cmd, execute)

    def free_command(self, command):
        """ Receives a command to execute """
        execute = RunAt.NODE
        cmd = command
        self.commands.add(cmd, execute)

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


           
