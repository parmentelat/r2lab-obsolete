#!/usr/bin/env python3
#
# Author file: Mario Zancanaro <mario.zancanaro@inria.fr>
#
"""
As convenience tool to save a snapshot of R2lab nodes and recover in a future moment
"""

import re
import os, os.path
import json
import subprocess
import time
import sys
import copy
from collections import OrderedDict
from argparse import ArgumentParser
from datetime import datetime
from sys import version_info
from collections import OrderedDict



FILEDIR = "/root/r2lab/nightly/"
try:
    os.listdir(FILEDIR)
except Exception as e:
    FILEDIR = "/Users/nano/Documents/Inria/r2lab/nightly/"
IMAGEDIR   = '/var/lib/rhubarbe-images/'



def main():
    """
    """
    parser = ArgumentParser()
    parser.add_argument("-n", "--nodes", dest="nodes", default='all',
                        help="Comma separated list of nodes")
    parser.add_argument("-s", "--save", dest="save_snapshot",
                        help="Save the snapshot")
    parser.add_argument("-l", "--load", dest="load_snapshot",
                        help="Load a given snapshot")
    parser.add_argument("-v", "--view", dest="view_snapshot",
                        help="View a given snapshot")
    args = parser.parse_args()

    save_snapshot = args.save_snapshot
    load_snapshot = args.load_snapshot
    view_snapshot = args.view_snapshot
    nodes         = args.nodes

    #view
    if view_snapshot is not None:
        view_snapshot(user, view_snapshot_ar)
    #save
    elif save_snapshot is not None:
        create_snapshot(nodes=format_nodes(nodes), user=user, snapshot=create_snapshot_ar, vimage=image_node, vstatus=status_node)
    #load
    elif load_snapshot is not None:
        load_snapshot(user, load_snapshot_ar)

    return 0



def save(nodes, user, snapshot, vimage=None, vstatus=None):
    """ save a snapshot for the user according nodes state
    """



def load(user, snapshot):
    """ load an already saved snapshot for the user
    """



def view(nodes):
    """ run the load command grouped by images and nodes
    """



def wait_and_update_progress_bar(wait_for):
    """ print the progress bar when waiting for a while
    """
    for n in range(wait_for):
        time.sleep(1)
        print('.', end=''),
        sys.stdout.flush()
    print("")



def command_in_curl(nodes, action='status'):
    """ transform the command to execute in CURL format
    """
    in_curl = map(lambda x:'curl reboot'+str('0'+str(x) if x<10 else x)+'/'+action, nodes)
    in_curl = '; '.join(in_curl)
    return in_curl



def fetch_user():
    """ identify the logged user
    """
    command = 'whoami'
    ans_cmd = run(command)
    if ans_cmd['status']:
        return ans_cmd['output']
    else:
        print('ERROR: user not detected.')
        exit(1)



def run(command):
    """ run the commands
    """
    p   = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (out, err) = p.communicate()
    ret        = p.wait()
    out        = out.strip().decode('ascii')
    err        = err
    ret        = True if ret == 0 else False
    return dict({'output': out, 'error': err, 'status': ret})



def parse_results_from_load(text):
    """ return a list of successfully load nodes found in the log/answer
    """
    text    = text.lower()
    search  = "uploading successful"
    idxs    = [n for n in range(len(text)) if text.find(search, n) == n]
    back_in = 7 #fit02 is 5 + two spaces use it on split
    split_by= ' '
    found   = []
    for idx in idxs:
        found.append(text[idx-back_in : idx].split(split_by)[1])
    found = map(lambda each:each.strip("fit"), found)
    found = list(set(found))
    return found



def all_nodes():
    """ return the list of all nodes
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



def ask(message):
    """ interruption for an user input
    """
    py3 = version_info[0] > 2
    if py3:
        response = input(message)
    else:
        response = raw_input(message)
    return response



if __name__ == '__main__':
    exit(main())
