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
from subprocess import Popen
import time
import sys
import copy
from collections import OrderedDict
from argparse import ArgumentParser
from datetime import datetime
from sys import version_info
from collections import OrderedDict
import progressbar
from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
    FileTransferSpeed, FormatLabel, Percentage, \
    ProgressBar, ReverseBar, RotatingMarker, Timer, AdaptiveETA



IMAGEDIR        = '/var/lib/rhubarbe-images/'
NODE_TAG_IMAGE  = '/etc/rhubarbe-image' #this is a TAG, not a folder
ADD_IN_NAME     = '_snap_'
ADD_IN_FOLDER   = '_snapshots'
DEFAULT_IMAGE   = 'fedora-23.ndz'

FILEDIR = "/root/r2lab/nightly/"
try:
    os.listdir(FILEDIR)
except Exception as e:
    #for my local dir
    FILEDIR = "/Users/nano/Documents/Inria/r2lab/nightly/"

USER_IMAGEDIR = '/var/lib/rhubarbe-images/'
try:
    os.listdir(USER_IMAGEDIR)
except Exception as e:
    #for my local dir
    USER_IMAGEDIR = '/Users/nano/'



def main():
    """
    """
    parser = ArgumentParser()
    parser.add_argument("-n", "--nodes", dest="nodes", default='all',
                        help="Comma separated list of nodes")
    parser.add_argument("-s", "--save", dest="save_snapshot",
                        help="Save r2lab snapshot based in the current image name")
    parser.add_argument("-p", dest="persist", action='store_true',
                        help="Persist the current image as a new one")
    parser.add_argument("-l", "--load", dest="load_snapshot",
                        help="Load a given snapshot")
    parser.add_argument("-v", "--view", dest="view_snapshot", default=None,
                        help="View a given snapshot")
    args = parser.parse_args()

    save_snapshot  = args.save_snapshot
    persist        = args.persist
    load_snapshot  = args.load_snapshot
    view_snapshot  = args.view_snapshot
    nodes          = args.nodes

    #save
    if save_snapshot is not None:
        save(format_nodes(nodes), save_snapshot, persist)
    #load
    elif load_snapshot is not None:
        load(load_snapshot)
    #view
    elif view_snapshot is not None:
        view(view_snapshot)
    else:
        view(view_snapshot)
    return 0



def save(nodes, snapshot, persist=False):
    """ save a snapshot for the user according nodes state using threading
    """
    file    = snapshot+'.snap'
    path    = os.getcwd()+'/'+file
    db      = {}
    errors  = []

    print('INFO: saving snapshot...')
    on_nodes, off_nodes = split_nodes_by_status(nodes)
    print('INFO: checking node images...')
    for node in off_nodes:
        db.update( {str(node) : {"state":'off', "imagepath":IMAGEDIR, "imagename": DEFAULT_IMAGE}})

    widgets = ['INFO: ', Percentage(), ' | ', Bar(), ' | ', Timer()]
    i = 0
    for node in on_nodes:
        if i == 0: bar = progressbar.ProgressBar(widgets=widgets,maxval=len(on_nodes)).start()
        saved_file = fetch_last_image(node, errors)
        image_path, image_name = os.path.split(str(saved_file))
        db.update( {str(node) : {"state":'on' , "imagepath":image_path+'/', "imagename":image_name }})
        i = i + 1
        time.sleep(0.1)
        bar.update(i)
    if i > 0: print('\r')
    if persist and on_nodes: persist_image(on_nodes, snapshot, db, errors)

    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    except Exception as e:
        print('ERROR: something went wrong in create directory in home.')
        exit(1)
    with open(path, "w+") as f:
        f.write(json.dumps(db)+"\n")
    if errors:
        print('INFO: something went wrong in the process of save your snapshot. Check it out:')
        for error in errors:
            print(error)
    else:
        print('INFO: snapshot saved. Enjoy!')



def load(snapshot):
    """ load an already saved snapshot
    """
    file_name, file_extension = os.path.splitext(snapshot)
    if not file_extension:
        file_extension = '.snap'
    with open(os.path.join(file_name + file_extension )) as data_file:
        try:
            content = json.load(data_file)
        except Exception as e:
            content = {}
    print('INFO: loading {} snapshot. This may take a little while.'.format(snapshot))
    (the_images, the_nodes) = group_nodes_and_images(content)

    if run_load(the_images, the_nodes):
        print('INFO: snapshot {} loaded. Enjoy!'.format(snapshot))



def view(snapshot):
    """ run the load command grouped by images and nodes
    """
    if snapshot is None:
        print("ERROR: snapshot name was not informed.")
        exit(1)



def run_load(images, nodes):
    """ run the load command grouped by images and nodes
    """
    failed = []
    for i,image in enumerate(images):
        n = ',fit'.join(nodes[i])
        n = 'fit'+n
        command = "rhubarbe-load {} -i {}; ".format(n, image)
        ans_cmd = run(command)
        loaded_nodes = parse_results_from_load(ans_cmd['output'])
        if len(loaded_nodes) > 0:
            print('INFO: working in nodes {}. Please, wait...'.format(",".join(sorted(loaded_nodes))))
        diff = list(set(nodes[i])-set(loaded_nodes))
        if diff != []:
            failed = failed + diff
    if failed == []:
        print('INFO: images loaded.')
        return True
    else:
        print('ERROR: something went wrong in load. Failed nodes: {}!'.format(",".join(sorted(failed))))
        return False



def group_nodes_and_images(db):
    """ return the nodes that have the same image to load
    """
    grouped_nodes = []
    related_image = []
    for node in db:
        state = db[node]['state']
        if state in "on":
            image = db[node]['imagepath']+db[node]['imagename']

            try:
                pos = related_image.index(image)
                grouped_nodes[pos].append(node)
            except Exception as e:
                related_image.append(image)
                grouped_nodes.append([node])
    return (related_image, grouped_nodes)



def split_nodes_by_status(nodes):
    """ split nodes in a list of on/off state nodes
    """
    print('INFO: checking node status...')
    widgets = ['INFO: ', Percentage(), ' | ', Bar(), ' | ', Timer()]
    bar = progressbar.ProgressBar(widgets=widgets,maxval=len(nodes)).start()
    on_nodes  = []
    off_nodes = []
    i = 0
    for node in nodes:
        node_status = check_status(node, 1)
        if 'on' in node_status:
            on_nodes.append(node)
        else:
            off_nodes.append(node)
        i = i + 1
        time.sleep(0.1)
        bar.update(i)
    print('\r')
    return (on_nodes, off_nodes)



def persist_image(on_nodes, snapshot, db, errors):
    """ save the images using rhubarbe
    """
    widgets = ['INFO: ', Percentage(), ' | ', Bar(), ' | ', Timer()]
    create_user_folder()
    clean_old_files()

    answers = persist_image_with_rhubarbe(on_nodes, snapshot)
    if True in answers:
        errors.append('ERROR: one or more image node could not be saved.')
    print('INFO: arranging files...')
    i = 0
    bar = progressbar.ProgressBar(widgets=widgets,maxval=len(on_nodes)).start()

    #move each saved file to the user snapshots folder
    for node in on_nodes:
        #searching for saved file give by rsave
        saved_file = fetch_saved_file_by_rhubarbe(node)
        image_path, image_name = os.path.split(str(saved_file))
        db.update( {str(node) : {"state":'on' , "imagepath":image_path+'/', "imagename":image_name }})
        if saved_file:
            user_folder = my_user_folder()
            os.rename(saved_file, user_folder+image_name)
        else:
            errors.append('ERROR: could not find file for node fit{}.'.format(node))
        i = i + 1
        time.sleep(0.1)
        bar.update(i)
    print('\r')



def persist_image_with_rhubarbe(nodes, snapshot):
    """ forks the rhubarbe save command
    """
    print('INFO: saving images. This may take a little while.')
    file_part   = code()+ADD_IN_NAME
    jobs_ans    = []
    i           = 0
    jobs        = [Popen("rhubarbe save {} -o {}".format(node, file_part),
                        shell=True, stdout=subprocess.PIPE)
                        for node in nodes]
    for job in jobs:
        jobs_ans.append(job.wait())
    return jobs_ans



def check_status(node, silent=0):
    """ return the state of each node. On and Off are searched.
    """
    options = ['on', 'already on', 'off', 'already off']
    command = 'curl -s reboot{}/status;'.format(node)
    ans_cmd = run(command)

    if not ans_cmd['status'] or ans_cmd['output'] not in options:
        if silent is 0:
            print('WARNING: could not detect the status of node #{}. It will be set as "off".'.format(node))
        return "off"
    else:
        return ans_cmd['output']



def create_user_folder():
    """ create a user folder in images folder
    """
    user = fetch_user()
    folder = user + ADD_IN_FOLDER
    path = USER_IMAGEDIR + folder + '/'

    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    except Exception as e:
        print('ERROR: something went wrong in create directory in images folder.')
        exit(1)



def my_user_folder():
    """ create a user folder in images folder
    """
    user = fetch_user()
    folder = user + ADD_IN_FOLDER
    path = USER_IMAGEDIR + folder +'/'
    if os.path.exists(path):
        return path
    else:
        print('ERROR: something went wrong in read user directory images folder.')
        exit(1)



def fetch_last_image(node, errors):
    """ recover the last image save in the node
    """
    image_name = DEFAULT_IMAGE

    try:
        command = "ssh root@fit{} cat {} | tail -n1 | awk '{{print $7}}'".format(node, NODE_TAG_IMAGE)
        ans_cmd = run(command)
        if ans_cmd['status']:
            ans = ans_cmd['output'].lower()
            if not 'no such file' in ans and not 'could not resolve' in ans and not 'no route to host' in ans:
                image_name = ans
            else:
                image_name = try_guess_the_image(node)
                errors.append('WARNING: image name of node {} was not found. A default {} is used.'.format(node, image_name))
    except Exception as e:
        pass

    user = fetch_user()
    folder = user + ADD_IN_FOLDER
    path = USER_IMAGEDIR + folder +'/'

    #try first in user images folder, if not try the common image repository
    if os.path.exists(path):
        command = "ls {}*saving__fit{}__*{}*.ndz".format(path, node, image_name)
        ans_cmd = run(command)
        if ans_cmd['status']:
            ans = ans_cmd['output'].lower()
            if not 'no such file' in ans:
                image_name = ans
            else:
                image_name = IMAGEDIR+image_name
        else:
            image_name = IMAGEDIR+image_name
    else:
        image_name = IMAGEDIR+image_name

    return image_name



def try_guess_the_image(node):
    """ try to guess the image instlled in the node
    """
    image_name = DEFAULT_IMAGE

    command = "ssh -q root@fit{}".format(node) + " cat /etc/*-release | uniq -u | awk /PRETTY_NAME=/ | awk -F= '{print $2}'"
    ans_cmd = run(command)
    if not ans_cmd['status'] or ans_cmd['output'] == "":
        pass
    else:
        image_name = ans_cmd['output']
        image_name = which_version(image_name)
    return image_name



def which_version(version):
    """ try to identify the version in the machine and return the version to install
    """
    OSS        = [ "fedora"           , "ubuntu"                                               ]
    VERSIONS   = [ ["23", "22", "21"] , ["16.04", "15.10", "15.04", "14.10", "14.04", "12.04"] ]
    oss         = OSS
    versions    = VERSIONS
    try_version = ''
    found_at    = -1
    version = version.lower()
    for i,v in enumerate(oss):
        if v in version:
            found_at    = i
            try_version = v + '-'
    if found_at == -1:
        try_version = oss[0] + '-' + version[0][0]
    else:
        found_at = -1
        for i,v in enumerate(versions[found_at]):
            if v in version:
                found_at    = i
                try_version = try_version + v + ".ndz"
        if found_at == -1:
            try_version = try_version + versions[0][0] + ".ndz"

    return try_version



def code():
    """ give me a small hash code from user name
    """
    user = fetch_user()
    return str(abs(hash(user)) % (10 ** 8))



def clean_old_files():
    """ move the old files with signature of user code + _snap_ to its folder
    """
    user_folder = my_user_folder()
    file_part_name = code()+ADD_IN_NAME
    command = "mv {}*saving__*{}.ndz {}".format(USER_IMAGEDIR, file_part_name, user_folder)
    ans_cmd = run(command)



def fetch_saved_file_by_rhubarbe(node):
    """ list the images dir in last modified file order
    """
    file_part_name = code()+ADD_IN_NAME
    command = "ls -la {}*saving__fit{}_*{}.ndz | awk '{{print $9}}'".format(USER_IMAGEDIR, node, file_part_name)
    ans_cmd = run(command)
    if ans_cmd['status']:
        ans = ans_cmd['output']
        if 'No such file or directory' in ans:
            return False
        else:
            return ans
    else:
        return False



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
