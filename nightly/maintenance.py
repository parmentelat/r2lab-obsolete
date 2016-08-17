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
parser.add_argument("-dr", "--drop", dest="drop", action='store_true',
                    help="Drop and initialize the file. All data is erased")

args = parser.parse_args()

FILEDIR    = "/Users/nano/Documents/Inria/r2lab/nightly/"
#FILEDIR = "/root/r2lab/nightly/"
FILENAME = "maintenance_nodes.json"



def main(args):
    """ """
    nodes_i = args.include_node
    nodes_r = args.remove_node
    a_date  = args.a_date
    message = args.message
    reset   = args.reset
    nodes   = args.nodes
    drop    = args.drop

    if nodes_i is None and nodes_r is None:
        if nodes is None:
            check_node(nodes)
        else:
            check_node(nodes)
    if nodes_i is not None:
        include_node(nodes_i, a_date, message, reset)
    if nodes_r is not None:
        remove_node(nodes_r, a_date)
    if drop:
        drop_file()




def drop_file():
    """ reset file
    """
    dir         = FILEDIR
    file_name   = FILENAME
    content = {}
    with open(os.path.join(dir, file_name), "w") as js:
        js.write(json.dumps(content)+"\n")
    print('INFO: the file was erased')




def check_node(nodes):
    """ list nodes in the list
    """
    dir         = FILEDIR
    file_name   = FILENAME
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




def now():
    """ current datetime
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')




def beautify(text):
    """ json print more readable
    """
    new_text = text.replace('\n', '').replace('\"', '')
    new_text = new_text.replace('date:', '\r   date:   ')
    new_text = new_text.replace('message:', '\r   message:')
    new_text = new_text.replace('reset:', '\r   reset:  ')
    new_text = new_text.replace("{", '').replace("}", '\n').replace("[", '').replace("]", '').replace(",", '\n')
    new_text = new_text.replace("]", '')
    return new_text




def format_date(val=None):
    """ current date (2016-04-06)
    """
    if val is None:
        return datetime.now().strftime('%Y-%m-%d')
    else:
        return str(datetime.strptime(val, '%Y-%m-%d').date())




if __name__ == "__main__":
    main(args)
