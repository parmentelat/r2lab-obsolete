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
from operator import itemgetter
from parallel import *




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

    @staticmethod
    def ping(target, times=1, *nodes):        
        """ Schedule for all nodes the ping command """
        for node in nodes:
            node.ping(target, times)

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

    def create_app(self, command, node):
        """ Set the application resource of NEPI  """
        app = self.ec.register_resource('linux::Application')
        self.ec.set(app, "command", command)    
        self.ec.register_connection(app, node)

        return app

    def deploy(self, application):
        self.ec.deploy()
        self.ec.wait_finished(application)
                
        print self.ec.trace(application, "stdout")
    
    def execute(self, *nodes):
        """ Execute the commands of each node instantiate and push to NEPI framework """
        for node in nodes:    
            
            for item in node.commands.tuple.itervalues():
                """ For each command associated at each node """
                command = item['command']    
                execute = item['execute']

                if RunAt.node(execute):
                   connected_node = self.connect_node(node)
                else:
                   connected_node = self.connect_gateway()
        
                app  = self.create_app(command, connected_node)

                #The ideia is implement send commands of each node in parallel
                #[Node | Who lauch     | togheder me? | times]
                #[N1   | [N2, N3, ...] | yes          | 1    ]
                #[N2   | [N1, N3, ...] | no           | 1    ]

                #print '---'
                #p1 = Parallel(node)
                #p1.start()
                #print "---"

                self.deploy(app)




class RunAt(object):
    """ Defines where the command will execute """
    
    NODE    = 'NODE'
    GATEWAY = 'GATEWAY'

    @staticmethod
    def node(element):
        if element == RunAt.NODE:
            return True
        else:
            return False

    @staticmethod
    def gateway(element):
        if element == RunAt.GATEWAY:
            return True
        else:
            return False





class VirtualTable(object):
    """ Create abstract queue based in the elements passed. The firs is always the id"""
    id = 0

    def __init__(self):
        super(VirtualTable, self).__init__()
        VirtualTable.id += 1
        self.id     = VirtualTable.id
        self.keys   = list()
        self.tuple  = dict()
    
    @staticmethod
    def new(*keys):
        vt = VirtualTable()
        for key in keys:
            vt.keys.append(key)
        return vt

    def counter(self):
        counter = 0
        if self.tuple:
            counter = max(self.tuple)
        return counter + 1

    def push(self, *values):
        id     = self.counter()
        keys   = self.keys
        values = values

        if len(keys) != len(values):
            raise Exception("the number of parameters are not the same as you definied, must be {}, means {}".format(len(keys), keys))
            return False
        dictionary = dict(zip(keys, values))
        self.tuple.update( { id : dictionary } )
       
    def pop(self, id):
        self.tuple.pop(id)

    def state(self):
        header  = ['ID'] + self.list_in_upper(self.keys)
        keys    = ['id'] + self.keys
        sort_by_key = 'id'
        sort_order_reverse = False

        data = []
        for key, value in self.tuple.iteritems():
            index = {'id' : key} 
            value.update(index)
            data.append(value)

        print self.to_table(data, keys, header, sort_by_key, sort_order_reverse)

    @staticmethod
    def list_in_upper(list):
        return map(str.upper, list)
    
    @staticmethod
    def to_table(data, keys, header=None, sort_by_key=None, sort_order_reverse=False):
        """Takes a list of dictionaries, formats the data, and returns
        the formatted data as a text table.

        Required Parameters:
            data - Data to process (list of dictionaries). (Type: List)
            keys - List of keys in the dictionary. (Type: List)

        Optional Parameters:
            header - The table header. (Type: List)
            sort_by_key - The key to sort by. (Type: String)
            sort_order_reverse - Default sort order is ascending, if
                True sort order will change to descending. (Type: Boolean)
        """
        # Sort the data if a sort key is specified (default sort order
        # is ascending)
        if sort_by_key:
            data = sorted(data,
                          key=itemgetter(sort_by_key),
                          reverse=sort_order_reverse)

        # If header is not empty, add header to data
        if header:
            # Get the length of each header and create a divider based
            # on that length
            header_divider = []
            for name in header:
                header_divider.append('-' * len(name))

            # Create a list of dictionary from the keys and the header and
            # insert it at the beginning of the list. Do the same for the
            # divider and insert below the header.
            header_divider = dict(zip(keys, header_divider))
            data.insert(0, header_divider)
            header = dict(zip(keys, header))
            data.insert(0, header)

        column_widths = []
        for key in keys:
            column_widths.append(max(len(str(column[key])) for column in data))

        # Create a tuple pair of key and the associated column width for it
        key_width_pair = zip(keys, column_widths)

        format = ('%-*s ' * len(keys)).strip() + '\n'
        formatted_data = ''
        for element in data:
            data_to_format = []
            # Create a tuple that will be used for the formatting in
            # width, value format
            for pair in key_width_pair:
                data_to_format.append(pair[1])
                data_to_format.append(element[pair[0]])
            formatted_data += format % tuple(data_to_format)
        return formatted_data





class Node(object): 
    """ Creates a abstract node object to operates in NEPI """

    def __init__(self, node):
        super(Node, self).__init__()
        self.ip            = self.ask_ip(node)
        self.node          = self.valid_node(node)
        self.interface     = None
        self.channel       = None
        self.commands      = VirtualTable.new('command', 'execute')

    @staticmethod
    def new(node):
        """ Instantiate the node """
        node = Node(node)
        return node

    @staticmethod
    def clone(node, clone):
        """ Clones the node """
        cloned = Node.new(node)
        
        for tuple in clone.commands.tuple:
            cloned.commands.tuple.append(tuple)
        
        return cloned

    def on(self):
        """ Turns node on """
        execute = RunAt.GATEWAY
        cmd = "curl {}/on ".format(self.ip)
        self.commands.push(cmd, execute)

    def off(self):
        """ Turns node off """
        execute = RunAt.GATEWAY
        cmd = "curl {}/off ".format(self.ip)
        self.commands.push(cmd, execute)

    def ping(self, target, times=1):
        """ Create a single ping command """
        execute = RunAt.NODE
        cmd = "ping -c {} {} ".format(times, target)
        self.commands.push(cmd, execute)

    def free_command(self, command):
        """ Receives a command to execute """
        execute = RunAt.NODE
        cmd = command
        self.commands.push(cmd, execute)

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
    def valid_node(node):
        """ Check if the node name is in the list of availables """
        nodes = ['fit10', 'fit13']
        if node.lower() not in nodes:
            raise Exception("invalid node name, must be {}".format(nodes))
            return False
        else:
            return node

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


           
