#!/usr/bin/env python
#
# Author file: Mario Zancanaro <mario.zancanaro@inria.fr>
#
"""
The info script stores information/photos about each node on r2lab.
These info managed by this script is pubilshed at run/status at r2lab.inria.fr
"""

import argparse
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
parser.add_argument(dest="nodes", nargs='?', default='all',
                    help="View nodes information stored.")
parser.add_argument("-i", "--include", nargs='*', dest="include",
                    help="Set information for a given node. <Node id>, <tab title> and <file name1, file name2,...> are the parameters order.")
parser.add_argument("-r", "--remove", nargs='*', dest="remove",
                    help="Remove node informations.")
parser.add_argument("-dr", "--drop", dest="drop", action='store_true',
                    help="Drop and initialize the nodes information. All data is erased.")

args = parser.parse_args()

FILEDIR = "/root/r2lab/r2lab.inria.fr/nodes/"
try:
    os.listdir(FILEDIR)
except Exception as e:
    FILEDIR = "/Users/nano/Documents/Inria/r2lab/r2lab.inria.fr/nodes/"
FILENAME = "nodes_info.json"



def main(args):
    """
    """
    nodes_i = args.include
    nodes_r = args.remove
    drop    = args.drop
    nodes   = args.nodes

    if nodes_i is not None:
        try:
            nodes, tab = nodes_i[0], nodes_i[1]
            files      = nodes_i[2:]
            include_node(nodes, tab, files)
        except Exception as e:
            print('ERROR: check the number of args.')
    elif nodes_r is not None:
        try:
            if len(nodes_r) > 1:
                nodes, tab = nodes_r[0], nodes_r[1]
            else:
                nodes = nodes_r[0]
                tab   = None
        except Exception as e:
            print('ERROR: check the number of args.')
        remove_node(nodes, tab)
    elif drop:
        reset_file()
    else:
        check_node(format_nodes(nodes))


def reset_file():
    """ reset file
    """
    dir         = FILEDIR
    file_name   = FILENAME
    content = {}
    with open(os.path.join(dir, file_name), "w") as js:
        js.write(json.dumps(content)+"\n")
    print('INFO: the file was erased')



def sync_files(files):
    """ copy files to folders
    """
    copiar os arquivos para as pastas info e images dentro de nodes
    tornar a pasta images dentro de nodes estática nas confs do django
    remover a sincronização do git para estas duas pastas



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
    if len(content) == 0:
        print("INFO: empty file")

    for node in nodes:
        try:
            print('---NODE {}'.format(node))
            tabs = content[node]
            for tb, tab in enumerate(tabs):
                file = content[node][tb]['file']

                if type(file) is list:
                    try:
                        tab  = content[node][tb]['tab']
                        file = content[node][tb]['file']
                        print("     tab: {}".format(tab))
                        print(" file(s): {}".format((', ').join(file)))
                        print('')
                    except Exception as e:
                        pass
                else:
                    try:
                        tab  = content[node][tb]['tab']
                        file = content[node][tb]['file']
                        print("     tab: {}".format(tab))
                        print("    file: {}".format(file))
                        print('')
                    except Exception as e:
                        pass
        except Exception as e:
            print('WARNING: node #{} info not found.'.format(node))
            print('')



def include_node(nodes, tab, files):
    """ include nodes in the list
    """
    dir       = FILEDIR
    file_name = FILENAME

    with open(os.path.join(dir, file_name)) as data_file:
        try:
            content = json.load(data_file)
        except Exception as e:
            content = {}

    files = touch_file(files)

    for node in format_nodes(nodes):
        try:
            content.update({ node : [{"tab":tab, "file":files}] })
        except Exception as e:
            content[node].update({"tab":tab, "file":files})

    with open(os.path.join(dir, file_name), "w") as js:
        js.write(json.dumps(content)+"\n")
    print('INFO: information for node(s) * {} * included.'.format(nodes))



def remove_node(nodes, tab=None):
    """ remove nodes in the list
    """
    dir       = FILEDIR
    file_name = FILENAME

    with open(os.path.join(dir, file_name)) as data_file:
        try:
            content = json.load(data_file)
        except Exception as e:
            content = {}

    for node in format_nodes(nodes):
        if tab is None:
            try:
                content.pop(node)
            except Exception as e:
                print('WARNING: node * {} * not found.'.format(node))
        else:
            try:
                tabs = content[node]
                for tb, tabf in enumerate(tabs):
                    if int(tb) == int(tab):
                        del content[node][tb]
                if len(content[node]) == 0:
                    content.pop(node)
            except Exception as e:
                print('WARNING: node * {} * not found.'.format(node))
    with open(os.path.join(dir, file_name), "w") as js:
        js.write(json.dumps(content)+"\n")
    print('INFO: information for node * {} * removed.'.format(nodes))



def touch_file(files):
    """ ensure the correct files
    """
    images  = ['.jpg', '.jpeg', '.gif', '.png']
    content = ['.md']
    allow   = images + content
    for file in files:
        ftype  = os.path.splitext(file)[1]
        if not ftype in allow:
            print('ERROR: file {} not allowed.'.format(file))
            exit()

    if len(files) == 1:
        ftype  = os.path.splitext(files[0])[1]
        if ftype in content:
            files = files[0]
        if ftype not in images and ftype not in content:
            print('ERROR: file {} not allowed.'.format(files[0]))
            exit()
    if len(files) == 0:
        files = ''
    return files



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



def format_date(val=None):
    """ current date (2016-04-06)
    """
    if val is None:
        return datetime.now().strftime('%Y-%m-%d')
    else:
        return str(datetime.strptime(val, '%Y-%m-%d').date())



if __name__ == "__main__":
    main(args)
