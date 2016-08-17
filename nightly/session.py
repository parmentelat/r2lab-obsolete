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

NODES      = list(range(1,38))
IMAGEDIR   = '/var/lib/rhubarbe-images/'
#FILEDIR    = "/root/r2lab/nightly/"
FILEDIR    = "/Users/nano/Documents/Inria/r2lab/nightly/"
FILENAME   = "session_nodes.json"
PR_LIST    = False
PREFERABLE = ['fedora-22.ndz', 'fedora-23.ndz', 'ubuntu-15.10.ndz', 'ubuntu-16.04.ndz']

OSS        = [ "fedora"           , "ubuntu"                                               ]
VERSIONS   = [ ["23", "22", "21"] , ["16.04", "15.10", "15.04", "14.10", "14.04", "12.04"] ]


def fetch_user():
    """ asdf
    """
    command = 'whoami'
    ans_cmd = run(command)
    if ans_cmd['status']:
        return ans_cmd['output']
    else:
        print('ERROR: user not detected.')
        exit(1)



def fetch_os():
    """ asdf
    """
    command = 'ls {}*.ndz || ls'.format(IMAGEDIR)
    ans_cmd = run(command)
    if ans_cmd['status']:
        ans = ans_cmd['output'].replace(IMAGEDIR, '')
        return ans.split('\n')
    else:
        return []



def beautify_list_os(options):
    """ asdf
    """
    options_prefer = PREFERABLE
    options_dir    = list(set(options) - set(options_prefer))
    options_all    = options_prefer + options_dir
    items_per_col  = 30
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
    options_dir       = list(set(fetch_os()) - set(options_prefer))
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



def check_status(node, silent='no'):
    """ asdf
    """
    options = ['on', 'already on', 'off', 'already off']
    command = 'curl -s reboot{}/status;'.format(node)
    ans_cmd = run(command)

    if not ans_cmd['status'] or ans_cmd['output'] not in options:
        if silent is 'no':
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
    """ reset file
    """
    dir         = FILEDIR
    file_name   = FILENAME
    content = {}
    with open(os.path.join(dir, file_name), "w") as js:
        js.write(json.dumps(content)+"\n")
    print('INFO: file erased.')



def remove_session(user, session=None, node=None):
    """ clear session for user
    """
    dir         = FILEDIR
    file_name   = FILENAME
    with open(os.path.join(dir, file_name)) as data_file:
        try:
            content = json.load(data_file)
        except Exception as e:
            content = {}
    try:
        if session is None and node is None:
            del content[user]
        else:
            if node is None:
                del content[user][session]
            else:
                del content[user][session][node]
        with open(os.path.join(dir, file_name), "w") as js:
            js.write(json.dumps(content)+"\n")
    except Exception as e:
        pass

    if session is None:
        print('INFO: all sessions were removed.')
    else:
        print('INFO: session * {} * was removed.'.format(session))



def format_date(val=None):
    """ current date (2016-04-06)
    """
    if val is None:
        return datetime.now().strftime('%Y-%m-%d')
    else:
        return str(datetime.strptime(val, '%Y-%m-%d').date())



def valid_image(image):
    """ asdf
    """
    images = fetch_os()
    return (image in images)



def load_session(user, session):
    """ clear session for user
    """
    dir       = FILEDIR
    file_name = FILENAME
    with open(os.path.join(dir, file_name)) as data_file:
        try:
            content = json.load(data_file)
        except Exception as e:
            content = {}

    try:
        content[user][session]
    except Exception as e:
        print('ERROR: session  * {} *  does not exist.'.format(session))
        exit(1)

    print('INFO: loading * {} * session. This may take a while.'.format(session))
    the_images, the_nodes = group_nodes_and_images(content, user, session)
    if run_load(the_images, the_nodes):
        if given_on_off_status(content, user, session):
            print('INFO: session  * {} *  loaded. Enjoy!'.format(session))



def create_session(nodes, user, session, vimage=None, vstatus=None, load=None):
    """ include nodes in the list
    """
    dir       = FILEDIR
    file_name = FILENAME
    date      = format_date()
    nodes     = format_nodes(nodes)
    if nodes == []:
        print('ERROR: no nodes given.')
        exit(1)
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
            content[user][session].update( {node : {"status":status, "os":os_ver}} )
        except Exception as e:
            try:
                content[user].update( {session: {node : {"status":status, "os":os_ver}}} )
            except Exception as e:
                content.update( {user: {session: {node : {"status":status, "os":os_ver}}}} )

    with open(os.path.join(dir, file_name), "w") as js:
        js.write(json.dumps(content)+"\n")
    print('')
    print('INFO: session * {} * for {} node(s) was created.'.format(session, len(nodes)))

    if load is 'yes':
        load_session(user, session)
    else:
        print('INFO: session * {} * wont be loaded. You can load at any time. Type -h to see how to do it.'.format(session))
    print('')



def given_on_off_status(db, user, session):
    """ adsf
    """
    command_in_curl(range(1,38), 'off')
    print('INFO: arranging status for nodes... please wait.')
    time.sleep(10)
    failed = []
    nodes  = []
    command= ""
    for node in db[user][session]:
        status = db[user][session][node]['status']
        command = command + "curl reboot{}/{}; ".format(node,status)
        nodes.append(node)
    ans_cmd = run(command)
    print('INFO: checking status... almost there...')
    time.sleep(15)
    for node in db[user][session]:
        status = db[user][session][node]['status']
        command = "curl reboot{}/status; ".format(node)
        ans_cmd = run(command)
        if not ans_cmd['status'] or (status not in ans_cmd['output']):
            failed.append(node)

    if failed == []:
        return True
    else:
        print('ERROR: something went wrong in define the status for * {} * session. Failed nodes: {}!'.format(session, ", ".join(failed)))
        return False



def wait_and_update_progress_bar(wait_for):
    """ Print the progress bar when waiting for a while
    """
    for n in range(wait_for):
        time.sleep(1)
        print('.', end=''),
        sys.stdout.flush()
    print("")



def command_in_curl(nodes, action='status'):
    """ Transform the command to execute in CURL format
    """
    in_curl = map(lambda x:'curl reboot'+str('0'+str(x) if x<10 else x)+'/'+action, nodes)
    in_curl = '; '.join(in_curl)
    return in_curl



def run_load(images, nodes):
    """ adsf
    """
    failed = []
    for i,image in enumerate(images):
        n = ',fit'.join(nodes[i])
        n = 'fit'+n
        command = "rhubarbe-load {} -i {}; ".format(n, image)
        ans_cmd = run(command)
        loaded_nodes = parse_results_from_load(ans_cmd['output'])
        diff = list(set(nodes[i])-set(loaded_nodes))
        if diff != []:
            failed = failed + diff
    if failed == []:
        print('INFO: images loaded.')
        return True
    else:
        print('ERROR: something went wrong in load. Failed nodes: {}!'.format(", ".join(failed)))
        return False



def parse_results_from_load(text):
    """ return a list of the nodes found in the log/answer from load commmand
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



def group_nodes_and_images(db, user, session):
    """ adsf
    """
    grouped_nodes = []
    related_image = []
    for node in db[user][session]:
        image = db[user][session][node]['os']
        try:
            pos = related_image.index(image)
            grouped_nodes[pos].append(node)
        except Exception as e:
            related_image.append(image)
            grouped_nodes.append([node])

    return [related_image, grouped_nodes]



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



def view_session(user, session=None):
    """ list sessions
    """
    dir         = FILEDIR
    file_name   = FILENAME
    with open(os.path.join(dir, file_name)) as data_file:
        try:
            content = json.load(data_file)
        except Exception as e:
            content = {}

    if session is None:
        try:
            content[user]
        except Exception as e:
            print('ERROR: no sessions found for * {} * .'.format(user))
            exit(1)
    else:
        try:
            content[user][session]
        except Exception as e:
            print('ERROR: session  * {} *  not found.'.format(session))
            exit(1)
    if len(content) == 0:
        print('ERROR: no sessions found for * {} * .'.format(user))
        exit(1)
    else:
        print("INFO: session(s) found for * {} *.".format(user))
        try:
            if session is None:
                for s in content[user]:
                    print('--- session * {} * ---'.format(s))
                    for node in content[user][s]:
                        print('    node: #{}'.format(node))
                        ans = json.dumps(content[user][s][node], sort_keys=True, indent=3)
                        print(beautify(ans))
            else:
                print('--- session * {} * ---'.format(session))
                for node in content[user][session]:
                    print('    node: #{}'.format(node))
                    ans = json.dumps(content[user][session][node], sort_keys=True, indent=3)
                    print(beautify(ans))
        except Exception as e:
            print('ERROR: something went wrong in view sessions.')



def beautify(text):
    """ json print more readable
    """
    new_text = text.replace('\n', '').replace('\"', '')
    new_text = new_text.replace('os:', '\r      os:')
    new_text = new_text.replace('status:', '\r  status:')

    new_text = new_text.replace("{", '').replace("}", '\n').replace("[", '').replace("]", '').replace(",", '\n')
    new_text = new_text.replace("]", '\n')
    return new_text



def identify_on_nodes(nodes):
    """ asdf
    """
    nodes_on = []
    for node in nodes:
        if 'on' in check_status(node, 'yes'):
            nodes_on.append(node)
    return nodes_on



def copy_session(user, old_session, new_session):
    """ asdf
    """
    dir         = FILEDIR
    file_name   = FILENAME
    with open(os.path.join(dir, file_name)) as data_file:
        try:
            content = json.load(data_file)
        except Exception as e:
            content = {}
    try:
        the_old_one = content[user][old_session]
    except Exception as e:
        print('ERROR: session  * {} *  not found.'.format(old_session))
        exit(1)

    if new_session is None or new_session == '':
        print('ERROR: session name is not valid.')
        exit(1)

    content[user].update( {new_session : the_old_one} )

    with open(os.path.join(dir, file_name), "w") as js:
        js.write(json.dumps(content)+"\n")
    print('')
    print('INFO: session * {} * was created.'.format(new_session))



########################################
def main():
    user  = fetch_user()
    # nodes = identify_on_nodes(format_nodes(NODES))
    nodes = NODES

    # create_session(nodes=nodes, user=user, session='bla', vimage=None, vstatus=None , load='no')
    # create_session(nodes=[23], user=user, session='bla', vimage=None, vstatus=None, load='no')
    # remove_session(user, 'bla', '2')
    # remove_session(user, 'bla')
    # create_session(nodes=[13,14,15,16], user=user, session='bli', vimage='parallel.pyc', vstatus=None, load='yes')
    # load_session(user, 'bli')
    view_session(user)
    # view_session('nano', 'bla')
    # copy_session(user ,'bla', 'abc')


    #TODO#
    #Save actual image with an specific name (user_session_node) and update the file for future load
    return 0



if __name__ == '__main__':
    try:
        exit(main())
    except KeyboardInterrupt:
        exit_gracefully()
