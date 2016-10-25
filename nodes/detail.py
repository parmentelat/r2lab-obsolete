#!/usr/bin/env python
#
# Author file: Mario Zancanaro <mario.zancanaro@inria.fr>
#
"""
The detail script used to store nodes info details.
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
                    help="Comma separated list OR range of nodes")
parser.add_argument("-i", "--include", dest="include_node", nargs=3,
                    help="Comma separated list OR range of nodes to include")
parser.add_argument("-r", "--remove", dest="remove_node",
                    help="Comma separated list OR range of nodes to remove")
parser.add_argument("-e", "--edit", dest="edit_node", nargs=3,
                    help="Comma separated list OR range of nodes to edit")
parser.add_argument("-d", "--date", dest="a_date",
                    help="include/remove an specific date (format yyyy-mm-dd)")
parser.add_argument("-a", "--attribute", dest="attribute",
                    help="Single attribute to remember the maintenance action")
parser.add_argument("-v", "--value", dest="value",
                    help="The value of the attribute")
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
FILENAME = "detail_nodes.json"

try:
    with open(os.path.join(FILEDIR, FILENAME)) as data_file:
        pass
except Exception as e:
    with open(os.path.join(FILEDIR, FILENAME), "w") as js:
        js.write(json.dumps({})+"\n")

LOC_DIR_IMGS = 'images_dt/'
LOC_DIR_INFO = 'info_dt/'


def main(args):
    """
    """
    nodes_i   = args.include_node
    nodes_r   = args.remove_node
    nodes_e   = args.edit_node
    a_date    = args.a_date
    attribute = args.attribute
    value     = args.value
    nodes     = args.nodes
    publish   = args.publish
    drop      = args.drop

    if nodes_e is None and nodes_i is None and nodes_r is None and not drop and not publish:
        check_node(nodes)
    if nodes_i is not None:
        nd, attribute, value = nodes_i
        include_node(nd, attribute, value, a_date)
    if nodes_r is not None:
        remove_node(nodes_r, attribute)
    if nodes_e is not None:
        nd, old_attr, new_attr = nodes_e
        edit_node(nd, old_attr, new_attr, a_date)
    if publish:
        print("INFO: publish started...")
    if drop:
        reset_file()



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
    print("INFO: nodes details and attributes")
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



def include_node(nodes, attribute, value, date):
    """ include nodes in the list
    """
    dir       = FILEDIR
    file_name = FILENAME
    date      = format_date(date)
    nodes     = format_nodes(nodes)
    if attribute is None:
        attribute = ""
    if value is None:
        value = ""
    else:
        value = touch_file(value)

    with open(os.path.join(dir, file_name)) as data_file:
        try:
            content = json.load(data_file)
        except Exception as e:
            content = {}
    for node in nodes:
        try:
            content[node].append({"date":date, "attribute":attribute, "value":value})
        except Exception as e:
            content.update({node : [{"date":date, "attribute":attribute, "value":value}]})
    with open(os.path.join(dir, file_name), "w") as js:
        js.write(json.dumps(content)+"\n")
    print('INFO: node(s) * {} * included.'.format(", ".join(nodes)))



def remove_node(nodes, attribute):
    """ remove nodes in the list
    """
    dir       = FILEDIR
    file_name = FILENAME
    nodes     = format_nodes(nodes)
    with open(os.path.join(dir, file_name)) as data_file:
        try:
            content = json.load(data_file)
        except Exception as e:
            content = {}
    old_content = copy.copy(content)
    for node in nodes:
        try_remove(old_content[node], attribute)
        if attribute is None:
            try:
                content.pop(node)
                print('---NODE {}'.format(node))
                ans = json.dumps(old_content[node], sort_keys=True, indent=2)
                print('INFO: node #{} was removed.'.format(node))
                print('')
            except Exception as e:
                print('WARNING: node or attribute not found.'.format(node))
        else:
            try:
                #search each occourence of the attribute in the node list
                content[node] = [x for x in content[node] if x['attribute'] != attribute]
                #remove the node to avoid empty list
                if len(content[node]) == 0:
                    content.pop(node)
                print('INFO: attribute * {} * from node #{} was removed.'.format(attribute, node))
                print('')
            except Exception as e:
                print('WARNING: node or attribute not found.'.format(node))
    with open(os.path.join(dir, file_name), "w") as js:
        js.write(json.dumps(content)+"\n")



def edit_node(nodes, old_attr, new_attr, date):
    """ edit nodes in the list
    """
    dir       = FILEDIR
    file_name = FILENAME
    date      = format_date(date)
    nodes     = format_nodes(nodes)
    if old_attr is None:
        old_attr = "None"
    if new_attr is None:
        new_attr = "None"

    with open(os.path.join(dir, file_name)) as data_file:
        try:
            content = json.load(data_file)
        except Exception as e:
            content = {}
    for node in nodes:
        try:
            for att in content[node]:
                if att['attribute'] == old_attr:
                    att['attribute'] = new_attr
        except Exception as e:
            print('WARNING: attribute {} not found for node {}.'.format(old_attr, node))
    with open(os.path.join(dir, file_name), "w") as js:
        js.write(json.dumps(content)+"\n")
    print('INFO: attribute {} updated to {}.'.format(old_attr, new_attr))



def all_nodes():
    """ range of all nodes
    """
    nodes = range(1,38)
    nodes = list(map(str, nodes))
    for k, v in enumerate(nodes):
        if int(v) < 10:
            nodes[k] = v.rjust(2, '0')
    return nodes



def try_remove(data, attribute=None):
    """ parse files to try remove
    """

    if attribute is None:
        for dt in data:
            file = dt['value']
            ftype = os.path.splitext(file)[1]
            if ftype:
                remove_single_file(file)
    else:
        for dt in data:
            if dt['attribute'] == attribute:
                file = dt['value']
                ftype = os.path.splitext(file)[1]
                if ftype:
                    remove_single_file(file)



def remove_single_file(files):
    """ remove single file from folder info or nodes
    """
    if files:
        command = "rm {}{}".format(FILEDIR, files)
        ans_cmd = run(command)
        if not ans_cmd['status']: #here we do not stop in error case
            print('WARNING: something went wrong in removing file(s) or files were already removed.')
            print(ans_cmd['output'])



def touch_file(file):
    """ ensure the correct files
    """
    images  = ['.jpg', '.jpeg', '.png']
    content = ['.md']
    allow   = images + content
    ftype   = os.path.splitext(file)[1]

    if ftype in content:
        sync_files(file, LOC_DIR_INFO)
        file = change_path(file, LOC_DIR_INFO)
    elif ftype in images:
        sync_files(file, LOC_DIR_IMGS)
        file = change_path(file, LOC_DIR_IMGS)
    return file



def sync_files(files, locdir):
    """ copy files to folders
    """
    command = "cp {} {}".format(files, FILEDIR + locdir)
    ans_cmd = run(command)
    if not ans_cmd['status']:
        print('ERROR: something went wrong in coping file(s).')
        print(ans_cmd['output'])
        exit()



def change_path(files, dir):
    """ changing the cmd line given path for assets path
    """
    selif = copy.deepcopy(files)
    if files:
        head, tail = os.path.split(files)
        selif = dir + tail
    return selif



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
    new_text = new_text.replace('date:', '\r      date:')
    new_text = new_text.replace('attribute:', '\r attribute:')
    new_text = new_text.replace('value:', '\r     value:')
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
