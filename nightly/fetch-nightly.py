#!/usr/bin/env python3
#
# Author file: Mario Zancanaro <mario.zancanaro@inria.fr>
#
"""
The nightly-fetch script will search for occurrences of nightly leases
already schedule in the r2lab UI and launch the nightly routine
"""

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

LEASE_NIGHTLY = 'inria_r2lab.nightly'
def main():

    parser = ArgumentParser()
    parser.add_argument("-N", "--nodes", dest="nodes", default="all",
                        help="Comma separated list of nodes")
    parser.add_argument("-a", "--avoid", dest="avoid_nodes", default="0",
                        help="Comma separated list of nodes to avoid")
    parser.add_argument("-V", "--version", default="fedora-23.ndz", dest="version",
                        help="O.S version to load")
    parser.add_argument("-t", "--text-dir", default="/root/r2lab/nightly/", dest="text_dir",
                        help="Directory to save text file")
    parser.add_argument("-e", "--email", default="fit-r2lab-users@inria.fr", dest="send_to_email",
                        help="Email to receive the execution results")
    #parser.add_argument("-d", "--days", dest="days", default=['wed','sun'],
    #                    help="Comma separated list of weekday to run")
    args = parser.parse_args()

    send_to_email  = args.send_to_email
    nodes          = args.nodes
    version        = args.version
    dir_name       = args.text_dir
    avoid_nodes    = args.avoid_nodes
    send_results_to= str(send_to_email)

    print('INFO: fetching nightly leases...')
    fetching_leases(nodes, avoid_nodes, version, dir_name, send_results_to)
    print('INFO: done')
    return 0


def fetching_leases(nodes, avoid_nodes, version, dir_name, send_results_to):
    """recovering the leases list"""
    command = "rhubarbe-leases | awk 'FNR > 1{{print $4} {print $6} {print $8} {print $10}}'"
    ans_cmd = run(command)
    if not ans_cmd['status']:
        print('ERROR: something went wrong in fetch leases.')
        print(ans_cmd['output'])
        exit()
    else:
        leases_details = ans_cmd['output'].split('\n')
        for i in range(3,len(leases_details),4):
            lease_name = leases_details[i]
            if LEASE_NIGHTLY == lease_name:
                dd, st, en = leases_details[i-3], leases_details[i-2], leases_details[i-1]
                cur = now()
                bgn = given_date('{},{},{},{},{}'.format(cur.year, dd.split('-')[0], dd.split('-')[1], st.split(':')[0], st.split(':')[1]))
                end = given_date('{},{},{},{},{}'.format(cur.year, dd.split('-')[0], dd.split('-')[1], en.split(':')[0], en.split(':')[1]))
                if(cur >= bgn and cur < end):
                    print('INFO: should run: {}  {}'.format(lease_name, cur.strftime('%Y-%m-%d %H:%M')))
                    command = 'python /root/r2lab/nightly/nightly.py -N {} -a {} -V {} -t {} -e {} > /var/log/nightly.log 2>&1;'.format(nodes, avoid_nodes, version, dir_name, send_results_to)
                    ans_cmd = run(command)
                    if not ans_cmd['status']:
                        print('ERROR: something went wrong in run nightly.')
                        print(ans_cmd['output'])
                        exit()
                    print('INFO: sync results...')
                    command = '/root/r2lab/infra/scripts/sync-nightly-results-at-r2lab.sh'
                    ans_cmd = run(command)
                    if not ans_cmd['status']:
                        print('ERROR: something went wrong in sync results.')
                        print(ans_cmd['output'])
                        exit()


def given_date(datestr):
    """parse date time year, month, day, hour, minute"""
    return datetime.strptime(datestr, '%Y,%m,%d,%H,%M')


def now():
    """ current datetime
    """
    return datetime.now()


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


if __name__ == "__main__":
    main()
