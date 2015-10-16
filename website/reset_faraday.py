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
parser.add_argument("-V", "--versions", dest="version", 
       help="Version of O.S.")

args = parser.parse_args()


def main(args):
    """ Treat nodes format and follows """

    nodes    = args.nodes
    version  = args.version    
    nodes    = format_nodes(nodes)

    valid_version(version)


    #=========================================
    # TURN ON ALL NODES ======================
    print "-- INFO: turn on nodes"
    all_nodes = name_node(nodes)
    all_nodes = stringfy_list(all_nodes)
    cmd = "ls"
    #cmd = "omf6 tell -t {} -a on".format(all_nodes)
    results = execute(cmd)

    if error_presence(results):
        print "** ERROR: turn on not executed"
        exit()
    else:
        print "-- INFO: nodes turned on"


    
    print "-- INFO: end of main"





def which_version(version):
    """ Return the version to install """
    versions_alias = ['u-1410', 'u-1504', 'f-21']
    versions_names = ['ubuntu 14.04', 'ubuntu 15.10', 'fedora 21']
    
    new_version_idx = 0

    if version in versions_names:
        old_version_idx = versions_names.index(version)
    else:
        old_version_idx = -1

    if old_version_idx >= len(versions_names)-1:
        new_version_idx = 0
    else:
        new_version_idx = old_version_idx + 1
    
    return named_version(versions_names[new_version_idx])




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
    versions_alias = ['u-1410', 'u-1504', 'f-21']
    versions_names = ['ubuntu 14.04', 'ubuntu 15.10', 'fedora 21']
    versions  = ['ubuntu-14.10.ndz', 'ubuntu-15.04.ndz', 'fedora-21.ndz']

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
    versions_names = ['ubuntu 14.04', 'ubuntu 15.10', 'fedora 21']
    
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
