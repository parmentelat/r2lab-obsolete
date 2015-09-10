#!/usr/bin/env python3

"""
given a set of nodes on the command line - either numbers or complete hostnames
we compute a news feed for livemap

this is as optimized as we can think about it
* first step on CMC status - all nodes reported as off will
  * get {'cmc_on_off' : 'off'}
  * be ignored in further steps
* second step is on attempting an ssh connection to retrieve OS release
  the ones that succeed with ubuntu/fedora 
  * get { 'cmc_on_off' : 'on', 'os_release' : <>}
  * be ignored in further steps
* remaining nodes where an ssh connection can be achieved to run 'hostname' will
  * get { 'cmc_on_off' : 'on', 'os_release' : 'other' }
  * be ignored in further steps
* others will have a ping attempted on control, they get either
  * get { 'cmc_on_off' : 'on', 'control_ping' : 'on' or 'off'}
"""

default_nodes = range(1, 38)

import sys
import re
import subprocess
import json
import signal
from argparse import ArgumentParser

def hostname(node_id, prefix="fit"):
    return "{prefix}{node_id:02d}".format(**locals())

verbose = None

########## timeouts (floats are probably OK but I have not tried)
# this should amply enough
timeout_curl = 2
# ssh should fail in 3s in normal conditions
# seeing ssh hang in some pathological situations is the reason
# for these timeouts in the first place
timeout_ssh = 4
# here again should be amply enough
timeout_ping = 2

########## helper
def display(*args, **keywords):
    keywords['file'] = sys.stderr
    print("livemap", *args, **keywords)
    sys.stderr.flush()

def debug(*args, **keywords):
    if verbose:
        display(*args, **keywords)

##########
# a convenience function that adds a timeout to subprocess.check_output
# stolen in http://stackoverflow.com/questions/1191374/subprocess-with-timeout
class AlarmDeep(Exception): pass
class Alarm(Exception): pass

def alarm_handler(signum, frame):
    raise AlarmDeep

def check_output_timeout(command, timeout, **keywords):
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(timeout)
    try:
        check_output = subprocess.check_output(command, **keywords)
        signal.alarm(0)
        return check_output
    except AlarmDeep as e:
        raise Alarm("timeout after {timeout} seconds".format(timeout=timeout))

def check_call_timeout(command, timeout, **keywords):
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(timeout)
    try:
        check_call = subprocess.check_call(command, **keywords)
        signal.alarm(0)
        return check_call
    except AlarmDeep as e:
        raise Alarm("timeout after {timeout} seconds".format(timeout=timeout))
    

##########
def insert_or_refine(id, infos, override=None):
    """
    locate an info in infos with that id (or create one)
    then update it with override if provided
    returns infos
    """
    node_info = None
    for scan in infos:
        if scan['id'] == id:
            node_info = scan
            break
    if not node_info:
        node_info = {'id' : id,
                    'cmc_on_off' : 'off',
                    'control_ping' : 'off',
                    'os_release' : 'fail',
                }
        infos.append(node_info)
    if override:
        node_info.update(override)
    return infos

##########
def pass1_on_off(node_ids, infos):
    """
    check for CMC status
    the ones that are OFF - or where status fails 
    are kept out of the next pass
    
    performs insertions in infos 
    returns the list of nodes that still need to be probed
    """
    remaining_ids = []
    for id in node_ids:
        debug("pass1 : {id} (CMC status via curl)".format(**locals()))
        reboot = hostname(id, "reboot")
        command = [ "curl", "--silent", "http://{reboot}/status".format(**locals()) ]
        result = check_output_timeout(command, timeout_curl, universal_newlines=True).strip()
        try:
            if result == 'off':
                insert_or_refine(id, infos)
            elif result == 'on':
                insert_or_refine(id, infos, {'cmc_on_off' : 'on'})
                remaining_ids.append(id)
            else:
                raise Exception("unexpected result on CMC status request " + result)
        except Exception as e:
            debug(e)
            insert_or_refine(id, infos, {'cmc_on_off' : 'fail'})
    return remaining_ids


##########
ubuntu_matcher = re.compile("DISTRIB_RELEASE=(?P<ubuntu_version>[0-9.]+)")
fedora_matcher = re.compile("Fedora release (?P<fedora_version>\d+)")

def pass2_os_release(node_ids, infos):
    """
    check for an os_release 
    the ones that do answer are kept out of the next passes

    same mechanism as pass1 in terms of side-effects and return value
    """
    remaining_ids = []
    for id in node_ids:
        debug("pass2 : {id} (os_release via ssh)".format(**locals()))
        control = hostname(id)
        remote_command_1 = "cat /etc/lsb-release /etc/fedora-release /etc/gnuradio-release 2> /dev/null | grep -i release"
        remote_command_2 = "gnuradio-config-info --version 2> /dev/null || echo NO GNURADIO"
        ssh_command = [
            "ssh",
            "root@{control}".format(**locals()),
            remote_command_1 + ";" + remote_command_2
        ]
        try:
            output = check_output_timeout(ssh_command, timeout_ssh, universal_newlines=True)
            # there should be 2 lines in general
            line1, line2 = output.strip().split("\n")
            # line1
            os_release = None
            match = ubuntu_matcher.match(line1)
            if match:
                version = match.group('ubuntu_version')
                os_release = "ubuntu-{version}".format(**locals())
            match = fedora_matcher.match(line1)
            if match:
                version = match.group('fedora_version')
                os_release = "fedora-{version}".format(**locals())
            if not os_release:
                os_release = 'other'
            # xxx ignore gnuradio for now
            insert_or_refine(id, infos, {'os_release' : os_release, 'control_ping' : 'on'})
        except:
            insert_or_refine(id, infos, {'os_release' : 'fail'})
            remaining_ids.append(id)
    return remaining_ids

def pass3_control_ping(node_ids, infos):
    """
    check for control_ping 
    the ones that do answer are kept out of the next passes (should be empty)

    same mechanism as pass1 in terms of side-effects and return value
    """
    remaining_ids = []
    for id in node_ids:
        debug("pass3 : {id} (control_ping via ping)".format(**locals()))
        # -c 1 : one packet -- -t 1 : wait for 1 second max
        control = hostname(id)
        command = [ "ping", "-c", "1", "-t", "1", control ]
        try:
            check_call_timeout(command, timeout_ping)
            insert_or_refine(id, infos, {'control_ping' : 'on'})
        except Exception as e:
            debug(e)
            insert_or_refine(id, infos, {'control_ping' : 'off'})
    return remaining_ids
                    

##########
arg_matcher = re.compile('[^0-9]*(?P<id>\d+)')
def normalize(cli_arg):
    if isinstance(cli_arg, int):
        id = cli_arg
    else:
        match = arg_matcher.match(cli_arg)
        if match:
            id = match.group('id')
        else:
            display("discarded malformed argument {cli_arg}".format(**locals()), file=sys.stderr)
            return None
    return int(id)


def main():
    parser = ArgumentParser()
    parser.add_argument("-v", "--verbose", action='store_true', default=False)
    parser.add_argument("-o", "--output", action='store', default=None)
    parser.add_argument("nodes", nargs='*')
    args = parser.parse_args()
    global verbose
    verbose = args.verbose
    if not args.nodes:
        args.nodes = default_nodes
    
    ### elaborate global focus
    node_ids = [ normalize(x) for x in args.nodes ]
    node_ids = [ x for x in node_ids if x]

    ### init    
    remaining_ids = node_ids
    infos = []

    remaining_ids = pass1_on_off(remaining_ids, infos)
    remaining_ids = pass2_os_release(remaining_ids, infos)
    remaining_ids = pass3_control_ping(remaining_ids, infos)

    with open(args.output, 'w') if args.output else sys.stdout as output:
        print(json.dumps(infos), file=output)

    if remaining_ids:
        display("OOPS - unexpected remaining nodes = ", remaining_ids, file=sys.stderr)
    

if __name__ == '__main__':
    main()
    sys.exit(0)
