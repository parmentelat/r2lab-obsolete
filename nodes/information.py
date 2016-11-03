#!/usr/bin/env python3
#
# Author file: Mario Zancanaro <mario.zancanaro@inria.fr>
#
"""
The info script stores information/photos about each node on r2lab.
These info managed by this script is pubilshed at run/status at r2lab.inria.fr
"""

import argparse
from argparse import ArgumentParser
import subprocess
from subprocess import Popen
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
parser.add_argument("-n", "--nodes", dest="nodes", default='all',
                    help="View nodes information stored.")
parser.add_argument("-i", "--include", nargs='*', dest="include",
                    help="Set information for a given node. <Node id>, <tab title> and <file_name1 file_name2 ...> are the parameters order.")
parser.add_argument("-r", "--remove", dest="remove",
                    help="Remove node informations.")
parser.add_argument("-t+", dest="tabp", action='store_true',
                    help="Add node tab.")
parser.add_argument("-t", dest="tabl",
                    help="Remove node tab.")
parser.add_argument("--drop", dest="drop", action='store_true',
                    help="Drop and initialize the nodes information. All data is erased.")

args = parser.parse_args()

FILEDIR = "/root/r2lab/nodes/"
try:
    os.listdir(FILEDIR)
except Exception as e:
    FILEDIR = "/Users/nano/Documents/Inria/r2lab/nodes/"
FILENAME = "info_nodes.json"

try:
    with open(os.path.join(FILEDIR, FILENAME)) as data_file:
        pass
except Exception as e:
    with open(os.path.join(FILEDIR, FILENAME), "w") as js:
        js.write(json.dumps({})+"\n")

LOC_DIR_IMGS = 'images/'
LOC_DIR_INFO = 'info/'


def main(args):
    """
    """
    nodes_i = args.include
    nodes_r = args.remove
    drop    = args.drop
    nodes   = args.nodes
    tabp    = args.tabp
    tabl    = args.tabl

    if nodes_i is not None:
        try:
            nodes, tabname, files = nodes_i[0], nodes_i[1], nodes_i[2:]
        except Exception as e:
            print('ERROR: check the number of args. [nodes] [tab text] [option files]')
            exit()
        include_node(nodes, tabname, files, tabp)
    elif nodes_r is not None:
        nodes = nodes_r
        if tabl:
            tabl = int(tabl) - 1
        remove_node(nodes, tabl)
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
    pub_img = FILEDIR + LOC_DIR_IMGS
    pub_mds = FILEDIR + LOC_DIR_INFO
    the_db  = FILEDIR + FILENAME
    bkp_db  = FILEDIR + 'bkp_{}_'.format(now(True)) + FILENAME
    choi = None
    while not choi:
        choi = input('INPUT: confirm action? [Y/n]')
        if choi in ['Y']:
            choi = True

            command = "cp {} {}; rm {}*; rm {}*".format(the_db, bkp_db, pub_mds, pub_img)
            ans_cmd = run(command)
            if not ans_cmd['status']:
                print('ERROR: something went wrong in copy/clear dir.')
                print(ans_cmd['output'])

            with open(os.path.join(dir, file_name), "w") as js:
                js.write(json.dumps(content)+"\n")
            print('INFO: the file was erased. A backup was also made.')
        else:
            print('INFO: no action made.')



def sync_files(files):
    """ copy files to folders
    """
    pub_img = FILEDIR + LOC_DIR_IMGS
    pub_mds = FILEDIR + LOC_DIR_INFO

    if type(files) is list:
        command = "cp {} {}".format(' '.join(files), pub_img)
    else:
        command = "cp {} {}".format(files, pub_mds)
    ans_cmd = run(command)
    if not ans_cmd['status']:
        print('ERROR: something went wrong in coping file(s).')
        print(ans_cmd['output'])
        exit()



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



def include_node(nodes, tab, files, append):
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
    selif = change_path(files)
    for node in format_nodes(nodes):
        try:
            tabs = content[node]
        except Exception as e:
            tabs = []
        try:
            if append:
                try:
                    content[node].append({"tab":tab, "file":selif})
                except Exception as e:
                    for tb, tabf in enumerate(tabs):
                        fl = content[node][tb]['file'] #sometime is array of files
                        remove_single_file(fl)
                    content.update({ node : [{"tab":tab, "file":selif}] })
            else:
                for tb, tabf in enumerate(tabs):
                    fl = content[node][tb]['file'] #sometime is array of files
                    remove_single_file(fl)
                content.update({ node : [{"tab":tab, "file":selif}] })
        except Exception as e:
            for tb, tabf in enumerate(tabs):
                fl = content[node][tb]['file'] #sometime is array of files
                remove_single_file(fl)
            content[node].update({"tab":tab, "file":selif})
    if files:
        sync_files(files)
    with open(os.path.join(dir, file_name), "w") as js:
        js.write(json.dumps(content)+"\n")
    print('INFO: information for node(s) * {} * included.'.format(nodes))



def change_path(files):
    """ changing the cmd line given path for assets path
    """
    selif = copy.deepcopy(files)
    if files:
        if type(files) is list:
            for idx, file in enumerate(files):
                head, tail = os.path.split(file)
                selif[idx] = LOC_DIR_IMGS + tail
        else:
            head, tail = os.path.split(files)
            selif = LOC_DIR_INFO + tail
    return selif



def remove_single_file(files):
    """ remove single file from folder info or nodes
    """
    if files:
        if type(files) is list:
            command = "rm {}{}".format(FILEDIR,' {}'.format(FILEDIR).join(files))
        else:
            command = "rm {}{}".format(FILEDIR, files)
        ans_cmd = run(command)
        if not ans_cmd['status']: #here we do not stop in error case
            print('WARNING: something went wrong in removing file(s) or files were already removed.')
            print(ans_cmd['output'])



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
                tabs = content[node]
                for tb, tabf in enumerate(tabs):
                    fl = content[node][tb]['file'] #sometime is array of files
                    remove_single_file(fl)
                content.pop(node)
            except Exception as e:
                print('WARNING: node * {} * not found.'.format(node))
        else:
            try:
                tabs = content[node]
                for tb, tabf in enumerate(tabs):
                    if int(tb) == int(tab):
                        fl = content[node][tb]['file'] #sometime is array of files
                        remove_single_file(fl)
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
        if not ftype.lower() in allow:
            print('ERROR: file {} not allowed.'.format(file))
            exit()

    if len(files)  > 1:
        for file in files:
            ftype  = os.path.splitext(file)[1]
            if not ftype.lower() in images:
                print('ERROR: multiple files supported only for images. Check the file {}.'.format(file))
                exit()
    if len(files) == 1:
        ftype  = os.path.splitext(files[0])[1]
        if ftype.lower() in content:
            files = files[0]
        if ftype.lower() not in images and ftype.lower() not in content:
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



def now(bkp=None):
    """ current datetime
    """
    if bkp is None:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        return datetime.now().strftime('%Y%m%d%H%M%S')



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
