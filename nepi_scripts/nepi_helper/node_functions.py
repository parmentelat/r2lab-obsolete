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
# This is a maintenance functions used to make group operations at the nodes from
# INRIA testbed (R2Lab) before running a OMF experiment using Nitos nodes.
#

from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState
import os
from nepi.util.sshfuncs import logger
import time
import sys
import re
import json


def load(nodes, version, connection_info, show_results=True):
    """ Load a new image to the nodes from the list """
    valid_version(version)
    ec    = ExperimentController(exp_id="ld-{}".format(version))
    
    nodes = format_nodes(nodes)
    nodes = check_node_name(nodes)

    gw_node = ec.register_resource("linux::Node")
    ec.set(gw_node, "hostname", connection_info['gateway'])
    ec.set(gw_node, "username", connection_info['gateway_username'])
    ec.set(gw_node, "identity", connection_info['identity'])
    ec.set(gw_node, "cleanExperiment", True)
    ec.set(gw_node, "cleanProcesses", False)
    ec.set(gw_node, "cleanProcessesAfter", False)

    node_appname = {}
    node_appid   = {}
    apps         = []

    for node in nodes:
        on_cmd_a = "omf6 load -t fit{} -i {} ".format(node, version) 
        node_appname.update({node : 'app_{}'.format(node)}) 
        node_appname[node] = ec.register_resource("linux::Application")
        ec.set(node_appname[node], "command", on_cmd_a)
        ec.register_connection(node_appname[node], gw_node)
        # contains the app id given when register the app by EC
        node_appid.update({node_appname[node] : node})
        apps.append(node_appname[node])

    ec.deploy(gw_node)

    results = {}
    for app in apps:
        print "-- loading image at node {}".format(node_appid[app])
        ec.deploy(app)
        ec.wait_finished(app)
        
    results = {}
    for app in apps:
        stdout    = remove_special_char(ec.trace(app, "stdout"))
        exitcode  = remove_special_char(ec.trace(app, 'exitcode'))
        results.update({ node_appid[app] : {'exit' : exitcode, 'stdout' : stdout}})
    
    ec.shutdown()

    for key_node in sorted(results):
        if error_presence(results[key_node]['stdout']):            
            exitcode  = 1
            results.update({ node_appid[app] : {'exit' : exitcode, 'stdout' : stdout}})
        elif '0' in results[key_node]['exit']:
            # implement thread for improvements and check in parallel
            ans = check_if_node_answer(key_node, connection_info, 3, 15)
            results.update(ans)

    if show_results:
        results = format_results(results, 'load')
        print_results(results)

    save_in_file(results, 'load_results')

    return results


def reset(nodes, connection_info, show_results=True):
    """ Reset all nodes from the list """
    ec    = ExperimentController(exp_id="reset")
    
    nodes = format_nodes(nodes)
    nodes = check_node_name(nodes)

    gw_node = ec.register_resource("linux::Node")
    ec.set(gw_node, "hostname", connection_info['gateway'])
    ec.set(gw_node, "username", connection_info['gateway_username'])
    ec.set(gw_node, "identity", connection_info['identity'])
    ec.set(gw_node, "cleanExperiment", True)
    ec.set(gw_node, "cleanProcesses", False)
    ec.set(gw_node, "cleanProcessesAfter", False)

    node_appname = {}
    node_appid   = {}
    apps         = []

    for node in nodes:
        on_cmd_a = "curl 192.168.1.{}/reset".format(node) 
        node_appname.update({node : 'app_{}'.format(node)}) 
        node_appname[node] = ec.register_resource("linux::Application")
        ec.set(node_appname[node], "command", on_cmd_a)
        ec.register_connection(node_appname[node], gw_node)
        # contains the app id given when register the app by EC
        node_appid.update({node_appname[node] : node})
        apps.append(node_appname[node])

    ec.deploy(gw_node)

    results = {}
    for app in apps:
        print "-- restarting node {}".format(node_appid[app])
        ec.deploy(app)
        ec.wait_finished(app)
        
        stdout    = remove_special_char(ec.trace(app, "stdout"))
        exitcode  = remove_special_char(ec.trace(app, 'exitcode'))
        results.update({ node_appid[app] : {'exit' : exitcode, 'stdout' : stdout}})

    ec.shutdown()
    
    for key_node in sorted(results):
        if error_presence(results[key_node]['stdout']):            
            exitcode  = 1
            results.update({ node_appid[app] : {'exit' : exitcode, 'stdout' : stdout}})
        if '0' in results[key_node]['exit']:
            ans = check_if_node_answer(key_node, connection_info, 3, 10)
            results.update(ans)

    if show_results:
        results = format_results(results, 'reset')
        print_results(results)

    save_in_file(results, 'reset_results')

    return results

def answer(nodes, connection_info, show_results=True):
    """ Check if a node answer a ping command in control interface """
    ec    = ExperimentController(exp_id="answer")
    
    nodes = format_nodes(nodes)
    nodes = check_node_name(nodes)

    gw_node = ec.register_resource("linux::Node")
    ec.set(gw_node, "hostname", connection_info['gateway'])
    ec.set(gw_node, "username", connection_info['gateway_username'])
    ec.set(gw_node, "identity", connection_info['identity'])
    ec.set(gw_node, "cleanExperiment", True)
    ec.set(gw_node, "cleanProcesses", False)
    ec.set(gw_node, "cleanProcessesAfter", False)

    node_appname = {}
    node_appid   = {}
    apps         = []

    for node in nodes:
        on_cmd_a = "ping -c1 192.168.3.{}".format(node) 
        node_appname.update({node : 'app_{}'.format(node)}) 
        node_appname[node] = ec.register_resource("linux::Application")
        ec.set(node_appname[node], "command", on_cmd_a)
        ec.register_connection(node_appname[node], gw_node)
        # contains the app id given when register the app by EC
        node_appid.update({node_appname[node] : node})
        apps.append(node_appname[node])

    ec.deploy(gw_node)

    ec.deploy(apps)
    ec.wait_finished(apps) 

    #ec.register_condition(sender_app, ResourceAction.START, receiver_app, ResourceState.STARTED) 

    results = {}
    for app in apps:
        stdout    = remove_special_char(ec.trace(app, "stdout"))
        exitcode  = remove_special_char(ec.trace(app, 'exitcode'))
        results.update({ node_appid[app] : {'exit' : exitcode, 'stdout' : stdout}})

    ec.shutdown()

    if show_results:
        results = format_results(results, 'answer')
        print_results(results)

    save_in_file(results, 'answer_results')

    return results


def info(nodes, connection_info, show_results=True):
    """ Get the info from the operational system """
    ec    = ExperimentController(exp_id="info")
    
    nodes = format_nodes(nodes)
    nodes = check_node_name(nodes)

    node_appname = {}
    node_appid   = {}
    apps         = []

    for node in nodes:        
        by_node = ec.register_resource("linux::Node")

        ec.set(by_node, "hostname", 'fit'+str(node))
        ec.set(by_node, "username", 'root')
        ec.set(by_node, "identity", connection_info['identity'])
        ec.set(by_node, "gateway", connection_info['gateway'])
        ec.set(by_node, "gatewayUser", connection_info['gateway_username'])
        ec.set(by_node, "cleanExperiment", True)
        ec.set(by_node, "cleanProcesses", False)
        ec.set(by_node, "cleanProcessesAfter", False)


        on_cmd_a = "cat /etc/*-release | uniq -u | awk /PRETTY_NAME=/ | awk -F= '{print $2}'" 
        node_appname.update({node : 'app_{}'.format(node)}) 
        node_appname[node] = ec.register_resource("linux::Application")
        ec.set(node_appname[node], "command", on_cmd_a)
        ec.register_connection(node_appname[node], by_node)
        # contains the app id given when register the app by EC
        node_appid.update({node_appname[node] : node})
        apps.append(node_appname[node])

        ec.deploy(by_node)

        ec.deploy(node_appname[node])
        ec.wait_finished(node_appname[node]) 

    results = {}
    for app in apps:
        stdout    = remove_special_char(ec.trace(app, "stdout"))
        exitcode  = remove_special_char(ec.trace(app, 'exitcode'))
        results.update({ node_appid[app] : {'exit' : exitcode, 'stdout' : stdout}})

    ec.shutdown()

    if show_results:
        results = format_results(results, 'info', True)
        print_results(results)

    save_in_file(results, 'info_results')

    return results


def alive(nodes, connection_info, show_results=True):
    """ Check if a node answer a ping command in the CM card """
    ec    = ExperimentController(exp_id="alive")
    
    nodes = format_nodes(nodes)
    nodes = check_node_name(nodes)

    gw_node = ec.register_resource("linux::Node")
    ec.set(gw_node, "hostname", connection_info['gateway'])
    ec.set(gw_node, "username", connection_info['gateway_username'])
    ec.set(gw_node, "identity", connection_info['identity'])
    ec.set(gw_node, "cleanExperiment", True)
    ec.set(gw_node, "cleanProcesses", False)
    ec.set(gw_node, "cleanProcessesAfter", False)

    node_appname = {}
    node_appid   = {}
    apps         = []

    for node in nodes:
        on_cmd_a = "ping -c1 192.168.1.{}".format(node) 
        node_appname.update({node : 'app_{}'.format(node)}) 
        node_appname[node] = ec.register_resource("linux::Application")
        ec.set(node_appname[node], "command", on_cmd_a)
        ec.register_connection(node_appname[node], gw_node)
        # contains the app id given when register the app by EC
        node_appid.update({node_appname[node] : node})
        apps.append(node_appname[node])

    ec.deploy(gw_node)

    ec.deploy(apps)
    ec.wait_finished(apps) 

    #ec.register_condition(sender_app, ResourceAction.START, receiver_app, ResourceState.STARTED) 

    results = {}
    for app in apps:
        stdout    = remove_special_char(ec.trace(app, "stdout"))
        exitcode  = remove_special_char(ec.trace(app, 'exitcode'))
        results.update({ node_appid[app] : {'exit' : exitcode, 'stdout' : stdout}})

    ec.shutdown()

    if show_results:
        results = format_results(results, 'alive')
        print_results(results)

    save_in_file(results, 'alive_results')

    return results


def status(nodes, connection_info, show_results=True):
    """ Check the status of all nodes from the list """
    return multiple_action(nodes, connection_info, 'status')


def on(nodes, connection_info, show_results=True):
    """ Turn on all nodes from the list """
    return multiple_action(nodes, connection_info, 'on')


def off(nodes, connection_info, show_results=True):
    """ Turn off all nodes from the list """
    return multiple_action(nodes, connection_info, 'off')


def multiple_action(nodes, connection_info, action, show_results=True):
    """ Execute the command in all nodes from the list """
    ec    = ExperimentController(exp_id=action)
    
    nodes = format_nodes(nodes)
    nodes = check_node_name(nodes)

    gw_node = ec.register_resource("linux::Node")
    ec.set(gw_node, "hostname", connection_info['gateway'])
    ec.set(gw_node, "username", connection_info['gateway_username'])
    ec.set(gw_node, "identity", connection_info['identity'])
    ec.set(gw_node, "cleanExperiment", True)
    ec.set(gw_node, "cleanProcesses", False)
    ec.set(gw_node, "cleanProcessesAfter", False)

    node_appname = {}
    node_appid   = {}
    apps         = []

    for node in nodes:
        on_cmd_a = "curl 192.168.1.{}/{}".format(node, action) 
        node_appname.update({node : 'app_{}'.format(node)}) 
        node_appname[node] = ec.register_resource("linux::Application")
        ec.set(node_appname[node], "command", on_cmd_a)
        ec.register_connection(node_appname[node], gw_node)
        # contains the app id given when register the app by EC
        node_appid.update({node_appname[node] : node})
        apps.append(node_appname[node])

    ec.deploy(gw_node)

    ec.deploy(apps)
    ec.wait_finished(apps) 

    results = {}
    for app in apps:
        stdout    = remove_special_char(ec.trace(app, "stdout"))
        exitcode  = remove_special_char(ec.trace(app, 'exitcode'))
        results.update({ node_appid[app] : {'exit' : exitcode, 'stdout' : stdout}})

    ec.shutdown()
    
    if show_results:
        results = format_results(results, action, True)
        print_results(results)

    save_in_file(results, 'multiple_results')

    return results


def remove_special_char(str):
    """ Remove special caracters from a string """
    if str is not None:
        new_str = str.replace('\n', '').replace('\r', '').replace('\"', '').lower()
        #new_str = re.sub('[^A-Za-z0-9]+', ' ', str)
    else:
        new_str = ''

    return new_str


def ip_node(alias):
    """ Returns the ip from the node alias [fitXX] """
    prefix = '192.168.1.xx'
    alias = alias.lower().replace('fit', '')

    try:
        int(alias)
    except Exception, e:
        raise Exception("error in ip convertion")
    
    ip = prefix.replace('xx', alias)
    return ip


def check_node_name(nodes):
    """ Returns the node without alias format """
    new_nodes = []
    nodes = (map(str,nodes))

    if not type(nodes) is list:
        raise Exception("invalid paramenter: {}, must be a list".format(nodes))
        return False
    for node in nodes:
        if "fit" in node:
            new_nodes.append(number_node(node))
        else:
            new_nodes.append(int(node))

    return new_nodes


def number_node(alias):
    """ Returns the number from the node alias [fitXX] """
    node = alias.lower().replace('fit', '')
    
    return int(node)


def valid_version(version):
    """ Check if the version to load """
    versions = ['ubuntu-14.10.ndz', 'ubuntu-15.04.ndz', 'fedora-21.ndz']
    if version not in versions:
        raise Exception("invalid version, must be {}".format(versions))
        return False
    else:
        return version

def format_results(results, action, stdout=False):
    """ Format the results in a summary way """
    formated_results = {}
    
    if results:
        for key in sorted(results):
            if not results[key]['exit']:
                new_result = 'fail'
            elif int(results[key]['exit']) > 0:
                new_result = 'fail'
            elif error_presence(results[key]['stdout']):
                new_result = 'fail'
            else:
                if stdout:
                    if results[key]['stdout'] == 'already on':
                        new_result = 'ok'
                    else:
                        new_result = results[key]['stdout']
                else:
                    new_result = action

            formated_results.update({ key : {action : new_result}})
            #print "node {:02}: {}".format(key, new_result)

    else:
        formated_results.update({ key : {action : 'no results to show'}})
        #print "-- no results to show"

    return formated_results

def print_results(results):
    """ Print the results """
    print "+ + + + + + + + +"
    for key, value in results.iteritems():
        print "node {:02}: {}".format(key, value)
    print "+ + + + + + + + +"


def check_if_node_answer(node, connection_info, times=2, wait_for=10):
    """ Wait for a while and to try a ping by 'answer' method """
    results = {}
    turn = 0
    for n in range(times):
        turn += 1
        print "-- attempt #{} for node {}".format(n+1, node)
                
        ans = answer([node], connection_info, False)
        if '0' in ans[node]['exit']:
            results.update(ans)
            break
        else:
            if times > turn:
                print "-- waiting for a while for new attempt"
                wait_and_update_progress_bar(wait_for)

    return results


def wait_and_update_progress_bar(wait_for):
    """ Print the progress bar when waiting for a while """
    for n in range(wait_for):
        time.sleep(1)
        print '\b.',
        sys.stdout.flush()
    print ""


def error_presence(stdout):
    """ Check so error mentions in the output results """
    err_words = ['error', 'errors', 'fail']

    if set(err_words).intersection(stdout.split()):
        return True
    else:
        return False


def save_in_file(results, file_name=None):
    """ Save the result in a json file """
    """ The format will be: """
    """ variable_name = '{
                            "key1" : {"name1" : "value1", "name2" : "value2"}, 
                            "key2" : {"name1" : "value1", "name2" : "value2"}
                         }' 
    """

    ext = ".json"

    if file_name is None:
        file_name = 'results'+ext

    file = open(file_name+ext, "w")
    file.write(file_name + " = '" + json.dumps(results) + "'")
    file.close()


def all_nodes():
    """Range of all nodes in faraday """
    
    nodes = range(1,38)
    
    return nodes


def format_nodes(nodes):
    """Correct format when inserted 'all' in -N nodes parameter """

    if 'all' in nodes:
        nodes = all_nodes()
    else:
        if not type(nodes) is list:
            if ',' in nodes:
                nodes = nodes.split(',')
            else:
                nodes = nodes.split()

    return nodes

