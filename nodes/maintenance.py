#!/usr/bin/env python
#
# Author file: Mario Zancanaro <mario.zancanaro@inria.fr>
#
"""
The maintenance script used to store nodes that have undergone maintenance.
The file generated will include the node and the date of the maintenance and will be used to put in zero
the statistics presented in the graphs at hardware.md page (nodes link) at r2lab.inria.fr
"""

from argparse import ArgumentParser
import os
import os.path
import subprocess
from subprocess import Popen
from datetime import datetime
import time
import sys
import re
import json
import copy
from collections import OrderedDict

parser = ArgumentParser()
parser.add_argument("-n", "--nodes", dest="nodes", default="all",
                    help="Comma separated list of nodes to check at the maintenance list")
parser.add_argument("-i", "--include", dest="include_node",
                    help="Comma separated list of nodes to include at the maintenance list")
parser.add_argument("-r", "--remove", dest="remove_node",
                    help="Comma separated list of nodes to remove from the maintenance list")
parser.add_argument("-d", "--date", dest="a_date",
                    help="include/remove an specific date (format yyyy-mm-dd)")
parser.add_argument("-m", "--message", dest="message",
                    help="Single message to remember the maintenance action")
parser.add_argument("-e", "--reset", dest="reset", choices=['yes','no'],
                    help="A flag that indicates if the statistics must be reset")
parser.add_argument("-p", "--publish", dest="publish", action='store_true',
                    help="Publish the results")
parser.add_argument("-dr", "--drop", dest="drop", action='store_true',
                    help="Drop and initialize the file. All data is erased")

args = parser.parse_args()

FILEDIR = "/root/r2lab/nodes/"
try:
    os.listdir(FILEDIR)
except Exception as e:
    FILEDIR = "/Users/nano/Documents/Inria/r2lab/nodes/"
FILENAME = "maintenance_nodes.json"

try:
    with open(os.path.join(FILEDIR, FILENAME)) as data_file:
        pass
except Exception as e:
    with open(os.path.join(FILEDIR, FILENAME), "w") as js:
        js.write(json.dumps({})+"\n")



def main(args):
    """
    """
    nodes_i = args.include_node
    nodes_r = args.remove_node
    a_date  = args.a_date
    message = args.message
    reset   = args.reset
    nodes   = args.nodes
    drop    = args.drop
    publish = args.publish

    if nodes_i is None and nodes_r is None and not drop and not publish:
        check_node(nodes)
    if nodes_i is not None:
        include_node(nodes_i, a_date, message, reset)
    if nodes_r is not None:
        remove_node(nodes_r, a_date)
    if publish:
        print("INFO: publish started...")
    if drop:
        reset_file()



def reset_file():
    """ reset file
    """
    dir         = FILEDIR
    file_name   = FILENAME
    the_db  = FILEDIR + FILENAME
    bkp_db  = FILEDIR + 'bkp_{}_'.format(now(True)) + FILENAME
    content = {}

    command = "cp {} {};".format(the_db, bkp_db)
    ans_cmd = run(command)
    if not ans_cmd['status']:
        print('ERROR: something went wrong in copy/clear dir.')
        print(ans_cmd['output'])

    with open(os.path.join(dir, file_name), "w") as js:
        js.write(json.dumps(content)+"\n")
    print('INFO: the file was erased. A backup was also made.')



def check_node(nodes):
    """ list nodes in the list
    """
    dir         = FILEDIR
    file_name   = FILENAME
    param       = nodes
    nodes       = format_nodes(nodes)
    with open(os.path.join(dir, file_name)) as data_file:
        try:
            content = json.load(data_file)
        except Exception as e:
            content = {}
    print("INFO: nodes dates of maintenance")
    if len(content) == 0:
        print("INFO: empty file")
    for node in nodes:
        try:
            ans = json.dumps(content[node], sort_keys=True, indent=2)
            print('---NODE {}'.format(node))
            print(beautify(ans))
        except Exception as e:
            if param is not 'all':
                print('---NODE {}'.format(node))
                print('WARNING: node #{} not found.'.format(node))
                print('')



def include_node(nodes, date, message, reset):
    """ include nodes in the list
    """
    dir       = FILEDIR
    file_name = FILENAME
    date      = format_date(date)
    nodes     = format_nodes(nodes)
    if message is None:
        message = ""
    if reset is None:
        reset = "no"
    with open(os.path.join(dir, file_name)) as data_file:
        try:
            content = json.load(data_file)
        except Exception as e:
            content = {}
    for node in nodes:
        try:
            content[node].append({"date":date, "message":message, "reset":reset})
        except Exception as e:
            content.update({node : [{"date":date, "message":message, "reset":reset}]})
    with open(os.path.join(dir, file_name), "w") as js:
        js.write(json.dumps(content)+"\n")
    print('INFO: node(s) * {} * included.'.format(", ".join(nodes)))



def remove_node(nodes, date):
    """ remove nodes in the list
    """
    dir       = FILEDIR
    file_name = FILENAME
    givendate = args.a_date
    date      = format_date(date)
    nodes     = format_nodes(nodes)
    with open(os.path.join(dir, file_name)) as data_file:
        try:
            content = json.load(data_file)
        except Exception as e:
            content = {}
    old_content = copy.copy(content)
    for node in nodes:
        try:
            if givendate is None:
                content.pop(node)
                print('---NODE {}'.format(node))
                ans = json.dumps(old_content[node], sort_keys=True, indent=2)
                print(beautify(ans))
            else:
                #search each occourence of the date in the node list
                content[node] = [x for x in content[node] if x['date'] != date]
                #remove the node to avoid empty list
                if len(content[node]) == 0:
                    content.pop(node)
            print('INFO: node #{} was removed.'.format(node))
            print('')
        except Exception as e:
            print('WARNING: node #{} not found.'.format(node))
    with open(os.path.join(dir, file_name), "w") as js:
        js.write(json.dumps(content)+"\n")



def all_nodes():
    """ range of all nodes
    """
    nodes = range(1,38)
    nodes = list(map(str, nodes))
    for k, v in enumerate(nodes):
        if int(v) < 10:
            nodes[k] = v.rjust(2, '0')
    return nodes



def new_list_nodes(nodes):
    """ put nodes in string list format with zero left
    """
    if not type(nodes) is list:
        if ',' in nodes:
            nodes = nodes.split(',')
        elif '-' in nodes:
            nodes = nodes.strip("[]").split('-')
            nodes = range(int(nodes[0]), int(nodes[1])+1)
        else:
            nodes = [nodes]

    new_list_nodes = list(map(str, nodes))
    for k, v in enumerate(new_list_nodes):
        if int(v) < 10:
            new_list_nodes[k] = v.rjust(2, '0')
    return new_list_nodes



def format_nodes(nodes, avoid=None):
    """ correct format when inserted 'all' in -i / -r nodes parameter
    """
    to_remove = avoid
    if 'all' in nodes:
        nodes = all_nodes()
    else:
        nodes = new_list_nodes(nodes)

    if to_remove:
        to_remove = new_list_nodes(to_remove)
        nodes = [item for item in nodes if item not in to_remove]
    return nodes



def now(bkp=None):
    """ current datetime
    """
    if bkp is None:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        return datetime.now().strftime('%Y%m%d%H%M%S')



def beautify(text):
    """ json print more readable
    """
    new_text = text.replace('\n', '').replace('\"', '')
    new_text = new_text.replace('date:', '\r   date:')
    new_text = new_text.replace('message:', '\r reason:')
    new_text = new_text.replace('reset:', '\r  reset:')
    new_text = new_text.replace("{", '').replace("}", '\n').replace("[", '').replace("]", '').replace(",", '\n')
    new_text = new_text.replace("]", '')
    return new_text



def run(command, std=True):
    """ run the commands
    """
    if std:
        p   = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    else:
        p   = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    (out, err) = p.communicate()
    ret        = p.wait()
    out        = out.strip().decode('ascii')
    err        = err
    ret        = True if ret == 0 else False
    return dict({'output': out, 'error': err, 'status': ret})



def format_date(val=None):
    """ current date (2016-04-06)
    """
    if val is None:
        return datetime.now().strftime('%Y-%m-%d')
    else:
        return str(datetime.strptime(val, '%Y-%m-%d').date())



if __name__ == "__main__":
    main(args)
