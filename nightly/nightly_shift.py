#!/usr/bin/env python
#
# Author file: Mario Zancanaro <mario.zancanaro@inria.fr>
#
"""
The nightly script used to monitor all the R2lab on a nightly basis
and outline the ones that are not reliable
"""

from argparse import ArgumentParser
import os
import os.path
from datetime import datetime
import time
import sys
import re
import json
from parallel import Parallel

from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState
from nepi.util.sshfuncs import logger

parser = ArgumentParser()
parser.add_argument("-N", "--nodes", dest="nodes",
                    help="Comma separated list of nodes")
parser.add_argument("-a", "--avoid", dest="avoid_nodes",
                    help="Comma separated list of nodes to avoid")
parser.add_argument("-V", "--version", default=None, dest="version",
                    help="O.S version to load")
parser.add_argument("-t", "--text-dir", default="/root/r2lab/nightly",
                    help="Directory to save text file")

args = parser.parse_args()

VERSIONS_ALIAS  = ['u-1410',           'u-1504',           'f-21',          'f-22',           'f-23']
VERSIONS_NAMES  = ['ubuntu 14.10',     'ubuntu 15.04',     'fedora 21',     'fedora 22',      'fedora 23']
VERSIONS        = ['ubuntu-14.10.ndz', 'ubuntu-15.04.ndz', 'fedora-21.ndz', 'fedora-22.ndz',  'fedora-23.ndz']

SEND_RESULTS_TO = ['mario.zancanaro@inria.fr']

phases          = {}



def main(args):
    """ Execute the load for all nodes in Faraday. """

    nodes    = args.nodes
    version  = args.version
    avoid_nodes = args.avoid_nodes

    if version is not None:
        valid_version(version)

    nodes     = format_nodes(nodes, avoid_nodes)
    all_nodes = name_node(nodes)

    #===========================
    #creating db for phases test
    for node in nodes:
        create_phases_db(node)

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
    # Uncomment the line below to use CURL format "on" command
    cmd = command_in_curl(all_nodes, 'on')
    results = execute(cmd)

    if error_presence(results):
        print "** ERROR: turn on not executed"
    else:
        print "-- INFO: nodes turned on"


    #==================================================================
    #searching in the answer of the command for the sentence of success
    for node in nodes:
        cmd = command_in_curl([name_node(node)])
        results = execute(cmd)
        if results == "on":
            update_phases_db(node, 1)


    #=========================================
    # CHECK THE CURRENT OS ===================
    print "-- INFO: check OS version for each node"
    wait_and_update_progress_bar(20)
    all_nodes = to_str(nodes)
    bug_node  = []
    old_os    = {}
    results   = {}


    for node in all_nodes:
        build_grouped_os_list

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
            update_phases_db(node, 2)


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
                    #==================================================================
                    #searching in the answer of the command for the sentence of success
                    nodes_found = parse_results_from_load(results)
                    update_phases_db(nodes_found, 3)
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
            bug_node.append(node)
            go = False

        if go:
            oldos = old_os[node]['os']
            newos = new_os[node]['os']

            if None is version:
                if oldos != newos:
                    if node in bug_node: bug_node.remove(node)
                    isok = 'yes'
                    update_phases_db(node, 4)
                else:
                    isok = 'no'
                    bug_node.append(node)
            else: # A VERSION WAS GIVEN
                if named_version(newos) == named_version(version):
                    if node in bug_node: bug_node.remove(node)
                    isok = 'yes'
                    update_phases_db(node, 4)
                else:
                    isok = 'no'
                    bug_node.append(node)

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
    # CHECK ZOMBIE (not turn off) NODES =====================
    print "-- INFO: check for zombie nodes"
    wait_and_update_progress_bar(20)
    all_nodes   = to_str(nodes)
    zombie_nodes= []
    results     = {}

    for node in all_nodes:
        wait_and_update_progress_bar(2)
        cmd = "curl reboot{}/status;".format(node)
        result = execute(cmd, key=node)
        results.update(result)

        if error_presence(result):
            # UPDATE NODES WHERE SOME BUG IS PRESENT
            bug_node.append(node)
        else:
            status = remove_special_char(result[node]['stdout']).strip()
            if status.lower() not in ['already off', 'off']:
                zombie_nodes.append(node)
            else:
                update_phases_db(node, 5)

    #=========================================
    # RESULTS  ===============================
    print "** WARNING: possible zombie nodes"
    print list(set(zombie_nodes))
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

    save_in_json(loaded_nodes, 'nightly')

    set_node_status(range(1,38), 'ok')
    #set_node_status(zombie_nodes, 'ko')
    set_node_status(bug_node, 'ko')

    print "-- INFO: send email"
    summary_in_mail(list(set(bug_node)))
    print "-- INFO: write in file"
    write_in_file(list(set(bug_node)))

    print "-- INFO: end of main"

    # =========================================
    # RESTARTING  SERVICES (temporary) ========
    # print "-- INFO: Restarting services"
    print "-- INFO: {}".format(now())
    # execute(RESTART_ALL)




def parse_results_from_load(text):
    """ return a list of the nodes found in the log/answer from load commmand """
    text    = text.lower()
    search  = "uploading successful"
    idxs    = [n for n in xrange(len(text)) if text.find(search, n) == n]
    back_in = 7 #fit02 is 5 + two spaces use it on split
    split_by= ' '
    found   = []

    for idx in idxs:
        found.append(text[idx-back_in : idx].split(split_by)[1])

    found = map(lambda each:each.strip("fit"), found)

    return found




def update_phases_db(node, the_phase):
    """ set fail for the node n in the phase """

    if not type(node) is list:
        phases[int(node)]["ph{}".format(the_phase)] = '32px Arial, Tahoma, Sans-serif; color: green;">&#8226;'
    else:
        for n in node:
            phases[int(n)]["ph{}".format(the_phase)] = '32px Arial, Tahoma, Sans-serif; color: green;">&#8226;'




def create_phases_db(node):
    """ create the phases to register each step of nightly routine """
    number_of_phases = 5
    all_phases = {}
    for n in range(number_of_phases):
        all_phases["ph{}".format(n+1)] = '18px Arial, Tahoma, Sans-serif; color: red;">&#215;'

    phases.update({int(node) : all_phases})




def write_in_file(text):
    """save the results in a file for posterior use of it """
    dir_name  = args.text_dir
    file_name = "nightly.txt"

    text = ', '.join(str(x) for x in text)

    with open(os.path.join(dir_name, file_name), "a") as fl:
        fl.write("{}: {}\n".format(date(),text))




def summary_in_mail(nodes):
    """send a summary output of the routine"""
    list_of_bug_nodes = nodes
    title = ''
    body  = ''
    to    = SEND_RESULTS_TO

    line_ok = ''
    line_fail = ''
    lines_fail = ''

    header = '\
            <tr>\n \
            <td style="width: 40px; text-align: center;"></td>\n \
            <td style="font:11px Arial, Tahoma, Sans-serif; width: 40px; text-align: center;"><img src="http://r2lab.inria.fr/assets/img/power.png"/ style="width:25px;height:25px;">&nbsp;on&nbsp;</td>\n \
            <td style="font:11px Arial, Tahoma, Sans-serif; width: 40px; text-align: center;"><img src="http://r2lab.inria.fr/assets/img/term.png"/ style="width:25px;height:25px;">ssh</td>\n \
            <td style="font:11px Arial, Tahoma, Sans-serif; width: 40px; text-align: center;"><img src="http://r2lab.inria.fr/assets/img/share.png"/ style="width:25px;height:25px;">load</td>\n \
            <td style="font:11px Arial, Tahoma, Sans-serif; width: 40px; text-align: center;"><img src="http://r2lab.inria.fr/assets/img/shuffle.png"/ style="width:25px;height:25px;">o.s.</td>\n \
            <td style="font:11px Arial, Tahoma, Sans-serif; width: 40px; text-align: center;"><img src="http://r2lab.inria.fr/assets/img/zombie.png"/ style="width:25px;height:25px;">zombie</td>\n \
            <td>&nbsp;&nbsp;</td>\n \
            <td colspan="3"></td>\n \
            </tr>'

    for node in list_of_bug_nodes:
        line_fail = '\
                    <tr>\n \
                        <td style="font:15px helveticaneue, Arial, Tahoma, Sans-serif;"><span style="border-radius: 50%; border: 2px solid #525252; width: 30px; height: 30px; line-height: 30px; display: block; text-align: center;"><span style="color: #525252;">{}</span></span></td>\n \
                        <td style="text-align: center; font:{}</td>\n \
                        <td style="text-align: center; font:{}</td>\n \
                        <td style="text-align: center; font:{}</td>\n \
                        <td style="text-align: center; font:{}</td>\n \
                        <td style="text-align: center; font:{}</td>\n \
                        <td></td>\n \
                        <td style="text-align: center;"><span style="background:#828282; color:#fff; padding:4px; border-radius: 5px; display: inline-block; width: 120px;"">{}</span></td>\n \
                        <td style="text-align: center; font:20px Arial, Tahoma, Sans-serif;">&nbsp; &#155; &nbsp;</td>\n \
                        <td style="text-align: center;"><span style="background:#42c944; color:#fff; padding:4px; border-radius: 5px; display: inline-block; width: 120px;"">{}</span><td>\n \
                    </tr>\
                    '.format(node, phases[node]['ph1'], phases[node]['ph2'], phases[node]['ph3'], phases[node]['ph4'], phases[node]['ph5'], loaded_nodes[node]['old_os'], loaded_nodes[node]['new_os'] )
        lines_fail += line_fail
    lines_fail = header + lines_fail

    line_ok = '\
            <tr>\n \
                <td style="font:11px Arial, Tahoma, Sans-serif; width: 10px; text-align: left;"><img src="http://r2lab.inria.fr/assets/img/people.png"/ style="width:35px;height:35px;"></td>\n \
                <td colspan="9" style="font:14px Arial, Tahoma, Sans-serif; vertical-align: middle; text-align: left;"><b>Yeah!</b><span style="font:12px Arial"> All nodes are working fine!</span></td>\n \
            </tr>\n \
            '

    with open('_nightly_email.html', 'r') as email_partial:
        body = email_partial.read()

    body = body.replace("[THE DATE]", date('%d/%m/%Y'))

    if len(list_of_bug_nodes) < 1:
        body = body.replace("[THE CONTENT]", line_ok)

        title = 'Nightly Routine of {}: Perfect!'.format(date('%d/%m/%Y'))

    elif len(list_of_bug_nodes) >= 1:
        body = body.replace("[THE CONTENT]", lines_fail)

        title = 'Nightly Routine of {}: Issues!'.format(date('%d/%m/%Y'))

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
    socketio.emit('chan-status', json.dumps(infos), None)




def command_in_curl(nodes, action='status'):
    """ Transform the command to execute in CURL format """
    nodes = number_node(nodes)

    in_curl = map(lambda x:'curl reboot'+str('0'+str(x) if x<10 else x)+'/'+action, nodes)
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




def new_list_nodes(nodes):
    """Put nodes in string list format with zero left """
    if not type(nodes) is list:
        if ',' in nodes:
            nodes = nodes.split(',')
        elif '-' in nodes:
            nodes = nodes.strip("[]").split('-')
            nodes = range(int(nodes[0]), int(nodes[1])+1)

    new_list_nodes = map(str, nodes)
    for k, v in enumerate(new_list_nodes):
        if int(v) < 10:
            new_list_nodes[k] = v.rjust(2, '0')

    return new_list_nodes




def format_nodes(nodes, avoid=None):
    """Correct format when inserted 'all' in -N nodes parameter """
    to_remove = avoid

    if 'all' in nodes:
        nodes = all_nodes()
    else:
        nodes = new_list_nodes(nodes)

    if to_remove:
        to_remove = new_list_nodes(to_remove)
        nodes = [item for item in nodes if item not in to_remove]

    return nodes




def save_in_json(results, file_name):
    """ Save the result in a json file """

    dir = args.text_dir
    file_name = "{}.ext".format(file_name)

    with open(os.path.join(dir, file_name), "w") as js:
        js.write(json.dumps(results))




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
    """ Current datetime """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')




def date(format='%Y-%m-%d'):
    """ Current date """
    return datetime.now().strftime(format)




if __name__ == "__main__":
    main(args)
