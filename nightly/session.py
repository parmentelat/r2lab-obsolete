#!/usr/bin/env python3

"""
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

NODES      = list(range(1,3))
#FILEDIR   = "/root/r2lab/nightly/"
FILEDIR    = "/Users/nano/Documents/Inria/r2lab/nightly/"
FILENAME   = "session_nodes.json"
PR_LIST    = False
PREFERABLE = ['fedora-22.ndz', 'fedora-23.ndz', 'ubuntu-15.10.ndz', 'ubuntu-16.04.ndz']

OSS        = [ "fedora"           , "ubuntu"                                               ]
VERSIONS   = [ ["23", "22", "21"] , ["16.04", "15.10", "15.04", "14.10", "14.04", "12.04"] ]


def check_user():
    """ asdf
    """
    command = 'whoami'
    ans_cmd = run(command)
    return ans_cmd



def fech_os():
    """ asdf
    """
    command = 'ls *.ndz | ls'
    ans_cmd = run(command)
    if ans_cmd['status']:
        return ans_cmd['output'].split('\n')
    else:
        return []



def beautify_list_os(options):
    """ asdf
    """
    options_prefer = PREFERABLE
    options_dir    = list(set(options) - set(options_prefer))
    options_all    = options_prefer + options_dir
    items_per_col  = 7
    left_blank     = 4 #supports until 1000 elements

    if len(options_all) > 0:
        data = chunkify(options_dir,items_per_col)
        col_width = max(len(word)+left_blank for row in data for word in row) + 3
        print('')
        for row in chunkify(options_prefer,4):
            print("".join("{}: ".format( str(options_prefer.index(word)+1).rjust(left_blank, ' ') if (options_prefer.index(word) < 1000)  else options_prefer.index(word)+1 ) + word.ljust(col_width) for word in row))

        print('')
        for row in data:
            print("".join("{}: ".format( str(options_all.index(word)+1).rjust(left_blank, ' ') if (options_all.index(word) < 1000)  else options_all.index(word)+1 ) + word.ljust(col_width) for word in row))
        print('')
    else:
        print('')
        print("INFO: no itens found")



def chunkify(lst,n):
    """ asdf
    """
    return [ lst[i::n] for i in range(n if n < len(lst) else len(lst)) ]



def get_printed_list():
    """ asdf
    """
    return PR_LIST



def set_printed_list(v):
    """ asdf
    """
    global PR_LIST
    PR_LIST = v



def which_version(version):
    """ Try to identify the version in the machine and return the version to install
    """
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



def check_os(node):
    """ asdf
    """
    options_prefer    = PREFERABLE
    options_dir       = list(set(fech_os()) - set(options_prefer))
    options_all       = options_prefer + options_dir
    number_of_options = len(options_all)
    command = "ssh -q root@fit{}".format(node) + " cat /etc/*-release | uniq -u | awk /PRETTY_NAME=/ | awk -F= '{print $2}'"
    ans_cmd = run(command)

    if not ans_cmd['status'] or ans_cmd['output'] == "":
        if not get_printed_list():
            beautify_list_os(options_dir)
            set_printed_list(True)

        choice = True
        while(choice):
            print('WARNING: could not detect automatically the image for node #{}. Please, input the corresponding number for it based on the list above.'.format(node))
            opt = ask_for_os([node])
            try:
                choice = False
                int(opt[0])
            except Exception as e:
                print('ERROR: value must be integer and between 1 and {}.'.format(number_of_options))
                choice = True

            if not choice:
                if not (int(opt[0]) > 0 and int(opt[0]) <= number_of_options):
                    print('WARNING: value must between 1 and {}.'.format(number_of_options))
                    choice = True
        return options_all[int(opt[0])-1]
    else:
        ans = ans_cmd['output']
        ans = which_version(ans)

        opt = '*'
        opt_accept = ['no', 'n', 'y', 'yes', '']
        while(opt not in opt_accept):
            opt = ask('INFO: * {} * was detect for node #{}.\nContinue? (y/n/^c): '.format(ans, node))

        if opt.lower() == 'n' or opt.lower() == 'no':
            if not get_printed_list():
                beautify_list_os(options_dir)
                set_printed_list(True)

            choice = True
            while(choice):
                print('INFO: Please, insert the corresponding image number for node #{}.'.format(node))
                opt = ask_for_os([node])
                try:
                    choice = False
                    int(opt[0])
                except Exception as e:
                    print('ERROR: value must be integer and between 1 and {}.'.format(number_of_options))
                    choice = True

                if not choice:
                    if not (int(opt[0]) > 0 and int(opt[0]) <= number_of_options):
                        print('WARNING: value must between 1 and {}.'.format(number_of_options))
                        choice = True
            return options_all[int(opt[0])-1]
        else:
            return ans



def check_status(node):
    """ asdf
    """
    options = ['on', 'already on', 'off', 'already off']
    command = 'curl -s reboot{}/status;'.format(node)
    ans_cmd = run(command)

    if not ans_cmd['status'] or ans_cmd['output'] not in options:
        print('WARNING: could not detect the status of node #{}. It will be set as "off". See -h option to change it.'.format(node))
        return "off"
    else:
        return ans_cmd['output']



def run(command):
    """ asdf
    """
    p   = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (out, err) = p.communicate()
    ret        = p.wait()
    out        = out.strip().decode('ascii')
    err        = err
    ret        = True if ret == 0 else False
    return dict({'output': out, 'error': err, 'status': ret})



def drop_file():
    """ reset file """
    dir         = FILEDIR
    file_name   = FILENAME
    content = {}
    with open(os.path.join(dir, file_name), "w") as js:
        js.write(json.dumps(content)+"\n")
    print('INFO: file erased')



def format_date(val=None):
    """ current date (2016-04-06)"""
    if val is None:
        return datetime.now().strftime('%Y-%m-%d')
    else:
        return str(datetime.strptime(val, '%Y-%m-%d').date())



def valid_image(image):
    """ asdf
    """
    images = fech_os()
    return (image in images)



def create_session(nodes, user, name, vimage=None, vstatus=None, load=None):
    """ include nodes in the list
    """
    dir       = FILEDIR
    file_name = FILENAME
    date      = format_date()
    nodes     = format_nodes(nodes)
    with open(os.path.join(dir, file_name)) as data_file:
        try:
            content = json.load(data_file)
        except Exception as e:
            content = {}

    for node in nodes:
        if vimage is None:
            os_ver = check_os(node)
        else:
            if not valid_image(vimage):
                print('ERROR: image * {} *  is not valid or is not saved in default folder.'.format(vimage))
                exit(1)
            else:
                os_ver = vimage

        if vstatus is None:
            status = check_status(node)
        else:
            if vstatus not in ["on", "off"]:
                print('ERROR: status * {} * is not valid. The options are `on` or `off`.'.format(vstatus))
                exit(1)
            else:
                status = vstatus

        try:
            content[user][name].update( {node : {"date":date, "status":status, "os":os_ver}} )
        except Exception as e:
            try:
                content[user].update( {name: {node : {"date":date, "status":status, "os":os_ver}}} )
            except Exception as e:
                content.update( {user: {name: {node : {"date":date, "status":status, "os":os_ver}}}} )

    with open(os.path.join(dir, file_name), "w") as js:
        js.write(json.dumps(content)+"\n")
    print('')
    print('INFO: node(s) * {} * updated.'.format(", ".join(nodes)))
    if load is None:
        print('INFO: creating * {} * session. This may take a while.'.format(name))
        # if load_session(user):
        #     print('INFO: session  * {} *  loaded. Enjoy!'.format(name))
        # else:
        #     print('ERROR: something went wrong in load  * {} * session!'.format(name))
    print('')



def all_nodes():
    """ range of all nodes """
    nodes = range(1,38)
    nodes = list(map(str, nodes))
    for k, v in enumerate(nodes):
        if int(v) < 10:
            nodes[k] = v.rjust(2, '0')

    return nodes



def new_list_nodes(nodes):
    """ put nodes in string list format with zero left """
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
    """ correct format when inserted 'all' in -i / -r nodes parameter """
    to_remove = avoid

    if 'all' in nodes:
        nodes = all_nodes()
    else:
        nodes = new_list_nodes(nodes)

    if to_remove:
        to_remove = new_list_nodes(to_remove)
        nodes = [item for item in nodes if item not in to_remove]

    return nodes



def eq(output, str):
    """ asdf
    """
    return output.strip().decode('ascii') == str



def ask(message):
    """ asdf
    """
    py3 = version_info[0] > 2
    if py3:
        response = input(message)
    else:
        response = raw_input(message)
    return response



def ask_for_os(nodes):
    """ asdf
    """
    opt = []
    for node in nodes:
        opt.append(ask("-- image for node #{}: ".format(node)))
    return opt



def exit_gracefully():
    """ asdf
    """
    print("\n\nINFO: you aborted the operation or something went wrong. Consider check your session database. Type -h to see the options.")
    print('')
    exit(1)



########################################
def main():
    create_session(NODES, 'nano', 'bla')

    #copy_session(old, new)
    #remove_session(session_id)
    #clear_sessions()
    #view_session(user_id)
    #load_session(session_id)
    #

    return 0



if __name__ == '__main__':
    try:
        exit(main())
    except KeyboardInterrupt:
        exit_gracefully()
