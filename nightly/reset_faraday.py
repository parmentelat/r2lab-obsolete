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
from parallel import Parallel
from datetime import datetime

parser = ArgumentParser()
parser.add_argument("-N", "--nodes", dest="nodes", 
       help="Comma separated list of nodes")
parser.add_argument("-V", "--version", default=None, dest="version", 
       help="O.S version to load")

args = parser.parse_args()

VERSIONS_ALIAS = ['u-1410',             'u-1504',           'f-21',          'f-22']
VERSIONS_NAMES = ['ubuntu 14.10',       'ubuntu 15.04',     'fedora 21',     'fedora 22']
VERSIONS       = ['ubuntu-14.10.ndz',   'ubuntu-15.04.ndz', 'fedora-21.ndz', 'fedora-22.ndz']
#RESTART_ALL    = "service omf-sfa stop; stop ntrc; service dnsmasq stop; service dnsmasq start; start ntrc; service omf-sfa start; "




def main(args):
    """ Execute the load for all nodes in Faraday. """

    nodes    = args.nodes
    version  = args.version

    if not None is version:
        valid_version(version)

    nodes    = format_nodes(nodes)
    all_nodes = name_node(nodes)

    # =========================================
    # RESTARTING  SERVICES (temporary) ========
    print "-- INFO: {}".format(now())
    # print "-- INFO: Restarting services"
    # execute(RESTART_ALL)
    

    #=========================================
    # TURN ON ALL NODES ======================
    print "-- INFO: turn on nodes"
    all_nodes = name_node(nodes)

    #------------------------------------------
    # Uncomment the two lines below to use OMF format "on" command
    #all_nodes = stringfy_list(all_nodes)
    #cmd = "omf6 tell -t {} -a on".format(all_nodes)    
    
    # OR

    #------------------------------------------ 
    # Uncomment the line below to use CURL format "on" command
    cmd = command_in_curl(all_nodes, 'on')
    
    results = execute(cmd)

    if error_presence(results):
        print "** ERROR: turn on not executed"
    else:
        print "-- INFO: nodes turned on"


    #=========================================
    # CHECK THE CURRENT OS ===================
    print "-- INFO: check OS version for each node"
    wait_and_update_progress_bar(20)
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
            old_os.update( {node : {'os' : 'unknown'}} )
        else:
            os = name_os(result[node]['stdout'])
            old_os.update( {node : {'os' : os}} )
    
  
    #=========================================
    # LOAD THE NEW OS ON NODES ===============
    print "-- INFO: execute load on nodes"
    results    = {}
    versions_names = VERSIONS_NAMES
    grouped_os_list = build_grouped_os_list(old_os)
    cmds= []    
    do_execute = False
    executions = 38 #(divide from the total nodes - 1 means total_nodes/1)

    # in case of have the version specified in the command line - do it for all
    if not None is version:
        do_execute = True
        
        splited_group = split(nodes, executions)
        for sub_list_nodes in splited_group:
            all_nodes = name_node(sub_list_nodes)
            all_nodes = stringfy_list(all_nodes)
            real_version = named_version(version)
            
            cmds.append("rhubarbe-load {} -i {}; ".format(all_nodes, real_version))
    else:
        for k, v in grouped_os_list.iteritems():
            do_execute = True
            os         = k
            list_nodes = v

            if os in versions_names or os == 'unknown':
                splited_group = split(list_nodes, executions)
                for sub_list_nodes in splited_group:
                    all_nodes = name_node(sub_list_nodes)
                    all_nodes = stringfy_list(all_nodes)            
                    new_version = which_version(os)
                    real_version = named_version(new_version)

                    cmds.append("rhubarbe-load {} -i {}; ".format(all_nodes, real_version))

            # IN CASE OF RETURN A unknown OS NAME
            else:
                for node in list_nodes:
                    # UPDATE NODES WHERE SOME BUG IS PRESENT
                    old_os.update( {node : {'os' : 'not found'}} )
                    bug_node.append(node)

    if do_execute:

        for cmd in cmds:
            #-------------------------------------
            # CONTROL BY THE MONITORING Thread
            
            omf_load = Parallel(cmd)
            omf_load.start()

            check_number_times = 3   # Let's check n times before kiil the thread (normally using groups of 5 in executions)
            delay_before_kill  = 60  # Timeout for each check

            for i in range(check_number_times+1):
                print "-- INFO: monitoring check #{}".format(i)
                
                wait_and_update_progress_bar(delay_before_kill)

                if omf_load.alive():
                    if i == check_number_times:
                        omf_load.stop()
                        print "** ERROR: oops! timeout reached!"
                        results = { 'node' : {'exitcode' : '1', 'stdout' : 'error'}}
                        break
                    else:
                        print "-- WARNING: let's wait more ... {}/{}".format(i+1,check_number_times)
                else:
                    print "-- INFO: leaving before timeout "
                    results = omf_load.output
                    break
            #-------------------------------------
            
            if error_presence(results):
                print "** ERROR: one or more node were not loaded correctly"
            else:
                print "-- INFO: nodes were loaded"


    #=========================================
    # CHECK AGAIN THE OS =====================
    print "-- INFO: check OS version for each node"
    wait_and_update_progress_bar(20)
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
            old_os.update( {node : {'os' : 'unknown'}} )
            bug_node.append(node)
        else:
            os = name_os(result[node]['stdout'])
            new_os.update( {node : {'os' : os}} )


    #=========================================
    # VERIFY IF CHANGED THE OS ===============
    loaded_nodes = {}
    for node in old_os:
        go = True

        try: 
            new_os[node]['os']
        except: 
            loaded_nodes.update( { node : {'old_os' : 'not found', 'new_os' : 'not found', 'changed' : 'no'}} )
            go = False

        if go:
            oldos = old_os[node]['os']
            newos = new_os[node]['os']

            if None is version:
                if oldos != newos:
                    if node in bug_node: bug_node.remove(node)
                    isok = 'yes'
                else:
                    isok = 'no'
            else: # A VERSION WAS GIVEN  
                if named_version(newos) == named_version(version):
                    if node in bug_node: bug_node.remove(node)
                    isok = 'yes'
                else:
                    isok = 'no'

            loaded_nodes.update( { node : {'old_os' : oldos, 'new_os' : newos, 'changed' : isok}} )

   
    #=========================================
    # TURN OFF ALL NODES ======================
    print "-- INFO: turn off nodes"
    all_nodes = name_node(nodes)

    #------------------------------------------
    # Uncomment the two lines below to use OMF format "on" command
    #all_nodes = stringfy_list(all_nodes)
    # cmd = "omf6 tell -t {} -a off".format(all_nodes)
    
    # OR
    
    #------------------------------------------ 
    # Uncomment the line below to use CURL format "on" command
    cmd = command_in_curl(all_nodes, 'off')
    
    results = execute(cmd)

    if error_presence(results):
        print "** ERROR: turn off not executed"
    else:
        print "-- INFO: nodes turned off"


    #=========================================
    # CHECK ZUMBIE (not turn off) NODES =====================
    print "-- INFO: check for zumbie nodes"
    wait_and_update_progress_bar(20)
    all_nodes   = to_str(nodes)
    zumbie_nodes= []
    results     = {}
    
    for node in all_nodes:
        wait_and_update_progress_bar(2)
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
    print list(set(zumbie_nodes))
    print " "

    print "** ERROR: possible problem nodes"
    print list(set(bug_node))
    print " "

    print "-- INFO: summary of reset routine"
    for key, value in sorted(loaded_nodes.iteritems()):
        print "node: #{} ".format(key)
        print "old:   {} ".format(value['old_os'])
        print "new:   {} ".format(value['new_os'])
        print "ok?:   {} ".format(value['changed'])
        print "--"
    print " "

    save_in_json(loaded_nodes, 'reset_faraday')

    set_node_status(range(1,38), 'ok')
    #set_node_status(zumbie_nodes, 'ko')
    set_node_status(bug_node, 'ko')
    
    summary_in_mail(list(set(bug_node)))

    print "-- INFO: end of main"

    # =========================================
    # RESTARTING  SERVICES (temporary) ========
    # print "-- INFO: Restarting services"
    print "-- INFO: {}".format(now())
    # execute(RESTART_ALL)




def summary_in_mail(content):
    """send a summary output of the routine"""

    list_of_bug_nodes = content

    title = ''
    body  = ''
    #to    = 'mario.zancanaro@inria.fr, thierry.parmentelat@inria.fr'
    to    = 'mario.zancanaro@inria.fr'

    if len(list_of_bug_nodes) < 1:
        title = 'Nightly Routine: Perfect!'
        body  = 'All nodes are OK!'
    elif len(list_of_bug_nodes) >= 1:
        title = 'Nightly Routine: Issues!'
        body  = 'Something went wrong with the node(s): <br> {}'.format(', '.join(str(x) for x in list_of_bug_nodes))

    cmd = 'mail -a "Content-type: text/html" -s "{}" {} <<< "{}"'.format(title, to, body)
    result = execute(cmd)




def set_node_status(nodes, status='ok'):
    """ Inform status page in r2lab.inria.fr the nodes with problem """
    from socketIO_client import SocketIO, LoggingNamespace

    hostname = 'r2lab.inria.fr'
    port     = 443
    
    infos = [{'id': arg, 'available' : status} for arg in nodes]

    socketio = SocketIO(hostname, port, LoggingNamespace)
    # print("Sending {infos} onto {hostname}:{port}".format(**locals()))
    socketio.emit('r2lab-news', json.dumps(infos), None)




def command_in_curl(nodes, action='status'):
    """ Transform the command to execute in CURL format """
    
    nodes = number_node(nodes)

    in_curl = map(lambda x:'curl 192.168.1.'+str(x)+'/'+action, nodes)
    in_curl = '; '.join(in_curl)

    return in_curl




def build_grouped_os_list(list):
    """ Process the old_os dict and returns the O.S. gruped by node """
    """ INPUT  -> {'12': {'os': 'fedora 21'}, '11': {'os': 'fedora 21'}, '10': {'os': 'ubuntu 14.04'}} """
    """ OUTPUT -> {'ubuntu 14.04': ['10'], 'fedora 21': ['11', '12']} """
    grouped_os_list = {}
    
    for k, v in list.iteritems():
        grouped_os_list.setdefault(v['os'], []).append(k)

    return grouped_os_list




def which_version(version):
    """ Return the version to install """
    versions_alias = VERSIONS_ALIAS
    versions_names = VERSIONS_NAMES
    
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
    versions_alias = VERSIONS_ALIAS
    if version not in versions_alias:
        raise Exception("invalid version, must be {}".format(versions_alias))
        return False
    else:
        return version




def named_version(version):
    """ Return a explicit name version """
    version = version.lower()

    versions_alias = VERSIONS_ALIAS
    versions_names = VERSIONS_NAMES
    versions       = VERSIONS

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
    versions_names = VERSIONS_NAMES
    
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
            if int(node) < 10:
                node = str(node).rjust(2, '0')
            
            ans.append('fit'+str(node))
    else:
        if int(nodes) < 10:
            nodes = str(nodes).rjust(2, '0')
       
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




def save_in_json(results, file_name=None):
    """ Save the result in a json file """
    
    dir = os.getcwd() + "/"
    ext = ".json"

    if file_name is None:
        file_name = 'result_reset_faraday'+ext

    try:
        os.stat(dir)
    except:
        os.mkdir(dir)

    file = open(dir+file_name+ext, "w")
    file.write(json.dumps(results))
    file.close()




def split(array, size):
    """ split one array in n (size) other parts """

    splited_arrays = []

    while len(array) > size:
        pice = array[:size]
        splited_arrays.append(pice)
        array = array[size:]
    splited_arrays.append(array)

    return splited_arrays




def now():
    """ Time now """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')




if __name__ == "__main__":
    main(args)
