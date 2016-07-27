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
parser.add_argument("-i", "--include", dest="include_node",
                    help="Comma separated list of nodes to include at the maintenance list")
parser.add_argument("-r", "--remove", dest="remove_node",
                    help="Comma separated list of nodes to remove from the maintenance list")
parser.add_argument("-d", "--date", dest="a_date",
                    help="include/remove an specific date (format yyyy-mm-dd)")
parser.add_argument("-D", "--file-dir", dest="file_dir", default="/root/r2lab/nightly/",
                    help="Directory to save json file")
parser.add_argument("-f", "--file", dest="file", default="maintenance_nodes.json",
                    help="File name")

args = parser.parse_args()



def main(args):
    """ """
    nodes_i = args.include_node
    nodes_r = args.remove_node
    a_date  = args.a_date

    if nodes_i is None and nodes_r is None:
        check_node()
    if nodes_i is not None:
        include_node(format_nodes(nodes_i), date(a_date))
    if nodes_r is not None:
        remove_node(format_nodes(nodes_r), date(a_date))




def check_node():
    """ include nodes in the list """
    dir         = args.file_dir
    file_name   = args.file
    with open(os.path.join(dir, file_name)) as data_file:
        try:
            content = json.load(data_file, object_pairs_hook=OrderedDict)
        except Exception as e:
            content = {}
    ans = json.dumps(content, sort_keys=True, indent=4)
    print ans




def include_node(nodes, date):
    """ include nodes in the list """
    dir         = args.file_dir
    file_name   = args.file
    with open(os.path.join(dir, file_name)) as data_file:
        try:
            content = json.load(data_file)
        except Exception as e:
            content = {}
    for node in nodes:
        try:
            content[node].append(date)
        except Exception as e:
            content.update({node : [date]})
    with open(os.path.join(dir, file_name), "w") as js:
        js.write(json.dumps(content)+"\n")
    print('node(s) {} included.'.format(", ".join(nodes)))




def remove_node(nodes, date=None):
    """ remove nodes in the list """
    dir         = args.file_dir
    file_name   = args.file
    with open(os.path.join(dir, file_name)) as data_file:
        try:
            content = json.load(data_file)
        except Exception as e:
            content = {}
    old_content = copy.copy(content)
    for node in nodes:
        try:
            if args.a_date is None:
                content.pop(node)
            else:
                while date in content[node]:
                    content[node].remove(date)
                #remove the node when the date list is empty
                if len(content[node]) == 0:
                    content.pop(node)
        except Exception as e:
            print('Warning: node {} not found.').format(node)
    print("---------------------")
    print("INFO: old data below:\n{}".format(json.dumps(old_content)))
    print("---------------------")

    with open(os.path.join(dir, file_name), "w") as js:
        js.write(json.dumps(content)+"\n")
    print('node(s) {} removed.'.format(", ".join(nodes)))




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
        else:
            nodes = [nodes]

    new_list_nodes = map(str, nodes)
    for k, v in enumerate(new_list_nodes):
        if int(v) < 10:
            new_list_nodes[k] = v.rjust(2, '0')

    return new_list_nodes




def format_nodes(nodes, avoid=None):
    """Correct format when inserted 'all' in -i / -r nodes parameter """
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
    """ Current datetime """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')




def date(val=None):
    """ Current date (2016-04-06)"""
    if val is None:
        return datetime.now().strftime('%Y-%m-%d')
    else:
        return str(datetime.strptime(val, '%Y-%m-%d').date())


if __name__ == "__main__":
    main(args)
