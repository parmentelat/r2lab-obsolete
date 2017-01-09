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
    print('INFO: fetching nightly leases...')
    fetching_leases()
    print('INFO: done')
    return 0


def fetching_leases():
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
                    command = 'python /root/r2lab/nightly/nightly.py -N 25 -e mario.zancanaro@inria.fr /var/log/nightly.log 2>&1;'
                    ans_cmd = run(command)
                    if not ans_cmd['status']:
                        print('ERROR: something went wrong in run nightly.')
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
