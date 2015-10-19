#!/usr/bin/env python
#
# Author file: Mario Zancanaro <mario.zancanaro@inria.fr>
#
# This is a maintenance functions used to make group operations at the nodes from
# INRIA testbed (R2Lab).
#

from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState
from argparse import ArgumentParser
import os
from nepi.util.sshfuncs import logger
from datetime import datetime
import time
import sys
import re
import json

parser = ArgumentParser()
parser.add_argument("-N", "--nodes", dest="nodes", 
       help="Comma separated list of nodes")

args = parser.parse_args()


def main(args):
    """ Treat nodes format and follows """

    nodes    = args.nodes
    nodes    = format_nodes(nodes)


    #=========================================
    # TURN ON ALL NODES ======================
    print "-- INFO: turn on nodes"
    all_nodes = name_node(nodes)
    all_nodes = stringfy_list(all_nodes)
    cmd = "omf6 tell -t {} -a on".format(all_nodes)
    results = execute(cmd)

    if error_presence(results):
        print "** ERROR: turn on not executed"
    else:
        print "-- INFO: nodes turned on"


    #=========================================
    # CHECK THE CURRENT OS ===================
    print "-- INFO: check OS version for each node"
    wait_and_update_progress_bar(30)
    all_nodes = to_str(nodes)
    bug_node   = []
    old_os = {}
    results    = {}
    
    for node in all_nodes:
        host = name_node(node)
        user = 'root'
        cmd = "cat /etc/*-release | uniq -u | awk /PRETTY_NAME=/ | awk -F= '{print $2}'"
        result = execute(cmd, host_name=host, key=node)
        results.update(result)

        if error_presence(result):
            # UPDATE NODES WHERE SOME BUG IS PRESENT
            bug_node.append(node)
        else:
            os = name_os(result[node]['stdout'])
            old_os.update( {node : {'os' : os}} )
    
  
    #=========================================
    # LOAD THE NEW OS ON NODES ===============
    print "-- INFO: execute load on nodes"
    versions_names = ['ubuntu 14.10',       'ubuntu 15.04',     'fedora 21']
    grouped_os_list = build_grouped_os_list(old_os)
    
    for k, v in grouped_os_list.iteritems():
        os         = k
        list_nodes = v

        if os in versions_names:
            all_nodes = name_node(list_nodes)
            all_nodes = stringfy_list(all_nodes)

            new_version = which_version(os)
            real_version = named_version(new_version)

            cmd = "omf6 load -t {} -i {} ".format(all_nodes, real_version) 
            results = execute(cmd)

            if error_presence(results):
                print "** ERROR: load not executed"
            else:
                print "-- INFO: nodes loaded"

        # IN CASE OF RETURN A unknown OS NAME
        else:
            for node in list_nodes:
                # UPDATE NODES WHERE SOME BUG IS PRESENT
                bug_node.append(node)


    #=========================================
    # CHECK AGAIN THE OS =====================
    print "-- INFO: check OS version for each node"
    wait_and_update_progress_bar(30)
    all_nodes = to_str(nodes)
    new_os     = {}
    results    = {}
    
    for node in all_nodes:
        host = name_node(node)
        user = 'root'
        cmd = "cat /etc/*-release | uniq -u | awk /PRETTY_NAME=/ | awk -F= '{print $2}'"
        result = execute(cmd, host_name=host, key=node)
        results.update(result)

        if error_presence(result):
            # UPDATE NODES WHERE SOME BUG IS PRESENT
            bug_node.append(node)
        else:
            os = name_os(result[node]['stdout'])
            new_os.update( {node : {'os' : os}} )



    #=========================================
    # VERIFY IF CHANGED THE OS ===============
    loaded_nodes = {}
    for os in old_os:
        go = True

        try: 
            new_os[os]['os']
        except: 
            loaded_nodes.update( { os : {'old_os' : 'not found', 'new_os' : 'not found', 'changed' : 'no'}} )
            go = False

        if go: 
            if old_os[os]['os'] != new_os[os]['os']:
                loaded_nodes.update( { os : {'old_os' : old_os[os]['os'], 'new_os' : new_os[os]['os'], 'changed' : 'ok'}} )
            else:
                loaded_nodes.update( { os : {'old_os' : old_os[os]['os'], 'new_os' : new_os[os]['os'], 'changed' : 'no'}} )


    #=========================================
    # TURN OFF ALL NODES ======================
    print "-- INFO: turn off nodes"
    all_nodes = name_node(nodes)
    all_nodes = stringfy_list(all_nodes)
    cmd = "omf6 tell -t {} -a off".format(all_nodes)
    results = execute(cmd)

    if error_presence(results):
        print "** ERROR: turn off not executed"
    else:
        print "-- INFO: nodes turned off"


    #=========================================
    # CHECK ZUMBIE NODES =====================
    print "-- INFO: check for zumbie nodes"
    # wait_and_update_progress_bar(30)
    all_nodes   = to_str(nodes)
    zumbie_nodes= []
    results     = {}
    
    for node in all_nodes:
        cmd = "curl 192.168.1.{}/status;".format(node)
        result = execute(cmd, key=node)
        results.update(result)

        if error_presence(result):
            # UPDATE NODES WHERE SOME BUG IS PRESENT
            bug_node.append(node)
        else:
            status = remove_special_char(result[node]['stdout']).strip()
            if status.lower() not in ['already off', 'off']:
                zumbie_nodes.append(node)

    
    #=========================================
    # RESULTS  ===============================
    print "** WARNING: possible zumbie nodes"
    print zumbie_nodes
    print " "

    print "** ERROR: nodes with some problem"
    print bug_node
    print " "

    print "-- INFO: summary of reset routine"
    for node in loaded_nodes:
        print "node: {} ".format(node)
        print "old:  {} ".format(loaded_nodes[node]['old_os'])
        print "new:  {} ".format(loaded_nodes[node]['new_os'])
        print "ok?:  {} ".format(loaded_nodes[node]['changed'])
        print "--"
    print " "

    print "-- INFO: end of main"




def build_grouped_os_list(list):
    """ Process the old_os dict and returns the O.S. gruped by node """
    """ INPUT  -> {'12': {'os': 'fedora 21'}, '11': {'os': 'fedora 21'}, '10': {'os': 'ubuntu 14.04'}} """
    """ OUTPUT -> {'ubuntu 14.04': ['10'], 'fedora 21': ['11, 12']} """
    grouped_os_list = {}
    
    for k, v in list.iteritems():
        grouped_os_list.setdefault(v['os'], []).append(k)

    return grouped_os_list




def which_version(version):
    """ Return the version to install """
    versions_alias = ['u-1410',             'u-1504',           'f-21']
    versions_names = ['ubuntu 14.10',       'ubuntu 15.04',     'fedora 21']
    
    new_version_idx = 0

    if version in versions_names:
        old_version_idx = versions_names.index(version)
    else:
        old_version_idx = -1

    if old_version_idx >= len(versions_names)-1:
        new_version_idx = 0
    else:
        new_version_idx = old_version_idx + 1
    
    return versions_names[new_version_idx]




def valid_version(version):
    """ Check if the version to load """
    versions_alias = ['u-1410', 'u-1504', 'f-21']
    if version not in versions_alias:
        raise Exception("invalid version, must be {}".format(versions_alias))
        return False
    else:
        return version




def named_version(version):
    """ Return a explicit name version """
    version = version.lower()

    versions_alias = ['u-1410',             'u-1504',           'f-21']
    versions_names = ['ubuntu 14.10',       'ubuntu 15.04',     'fedora 21']
    versions       = ['ubuntu-14.10.ndz',   'ubuntu-15.04.ndz', 'fedora-21.ndz']

    if version in versions_alias:
        explicit_version = versions[versions_alias.index(version)]
    elif version in versions_names:
        explicit_version = versions[versions_names.index(version)]
    else:
        explicit_version = versions[0]

    return explicit_version




def to_str(list_items):
    """ Change the integer array to string array """
    
    if not type(list_items) is list:
        raise Exception("invalid parameter: {}, must be a list".format(list_items))
        return False

    new_list = (map(str, list_items))

    return new_list




def wait_and_update_progress_bar(wait_for):
    """ Print the progress bar when waiting for a while """
    for n in range(wait_for):
        time.sleep(1)
        print '\b.',
        sys.stdout.flush()
    print ""




def execute(command, host_name='localhost', host_user='root', key='node'):
    """ Execute the command in host """

    ec = ExperimentController()

    node = ec.register_resource("linux::Node")
    ec.set(node, "hostname", host_name)
    ec.set(node, "username", host_user)
    ec.set(node, "cleanExperiment", True)
    ec.set(node, "cleanProcesses", False)
    ec.set(node, "cleanProcessesAfter", False)
    ec.deploy(node)

    app = ec.register_resource("linux::Application")
    ec.set(app, "command", command)
    ec.register_connection(app, node)
    ec.deploy(app)
    ec.wait_finished(app)

    stdout    = remove_special_char(ec.trace(app, "stdout"))
    exitcode  = remove_special_char(ec.trace(app, 'exitcode'))

    results = {}
    results.update({ str(key) : {'exitcode' : exitcode, 'stdout' : stdout}})

    return results




def error_presence(results):
    """ Check error mentions in output or 1 in exit code """
    err_words = ['error', 'errors', 'fail']

    error = False

    for result in results:
        stdout    = remove_special_char(results[result]['stdout'])
        exitcode  = remove_special_char(results[result]['exitcode'])

        if exitcode is '':
            exitcode = 1

        if set(err_words).intersection(stdout.split()) or int(exitcode) > 0:
            error = True
            break
        
    return error




def stringfy_list(list):
    """ Return the list in a string comma separated ['a,'b','c'] will be a,b,c """
    
    stringfy_list = ','.join(list)

    return stringfy_list




def name_os(os):
    """ Format the O.S. names """
    versions_names = ['ubuntu 14.10',       'ubuntu 15.04',     'fedora 21']
    
    os = os.strip()

    if os == "":
        os = 'undefined'
    # Search in the list the 9th first characters
    all_os_found = filter(lambda x: os[:9] in x, versions_names)

    return all_os_found[0] if all_os_found else 'undefined'




def remove_special_char(str):
    """ Remove special caracters from a string """
    if str is not None:
        new_str = str.replace('\n', ' ').replace('\r', ' ').replace('\"', ' ').lower()
        #new_str = re.sub('[^A-Za-z0-9]+', ' ', str)
    else:
        new_str = ''

    return new_str




def number_node(nodes):
    """ Returns the number from the node alias [fitXX] """
    
    if type(nodes) is list:
        ans = []
        for node in nodes:
            node_temp = int(node.lower().replace('fit', ''))
            ans.append(node_temp)
    else:
        ans = int(nodes.lower().replace('fit', ''))
    
    return ans




def name_node(nodes):
    """ Returns the name from the node alias [fitXX] """
    
    if type(nodes) is list:
        ans = []
        for node in nodes:
            ans.append('fit'+str(node))
    else:
        ans = 'fit'+str(nodes)
    
    return ans




def all_nodes():
    """Range of all nodes in faraday """
    
    nodes = range(1,38)
    nodes = map(str, nodes)
    for k, v in enumerate(nodes):
        if int(v) < 10:
            nodes[k] = v.rjust(2, '0')
    
    return nodes




def format_nodes(nodes):
    """Correct format when inserted 'all' in -N nodes parameter """

    if 'all' in nodes:
        nodes = all_nodes()
    else:
        if not type(nodes) is list:
            if ',' in nodes:
                nodes = nodes.split(',')
            elif '-' in nodes:
                nodes = nodes.strip("[]").split('-')
                nodes = range(int(nodes[0]), int(nodes[1])+1)
            else:
                nodes = nodes.split()

    return nodes




if __name__ == "__main__":
    main(args)
