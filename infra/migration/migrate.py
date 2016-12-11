#!/usr/bin/env python

from __future__ import print_function

import sys
import json

from sfa.util.xrn import Xrn

all_mode = False
#all_mode = True

slice_blacklist = [
    "totoproj", "mario.tutorial", "r2lab.mario_test",
    "onelab.upmc.test2radomir",
    "upmc.test", "thierry.admin1"
] if not all_mode else []

special_user_urns = [
    "urn:publicid:IDN+onelab+user+myslice",
    "urn:publicid:IDN+onelab:upmc+user+loic_baron",
] if not all_mode else []

users_blacklist = [
    "myslice", "test",
] if not all_mode else []

########## helpers

def parse_omf(inputname, key):
    try:
        with open(inputname) as feed:
#            print("Parsing file {}".format(inputname))
            return json.loads(feed.read())['resource_response'][key]
    except Exception as e:
        print("Could not parse {} -- {}".format(inputname, e))
        exit(1)


def urn_to_hrn(urn):
    return Xrn(urn).get_hrn()

def accountname(account):
    c1 = account.get('name', None)
    if c1:
        return c1
    c2 = account.get('urn', None)
    if c2:
        return urn_to_hrn(c2)
    return "ANON account"
    

def username(user):
    c1 = user.get('name', None)
    if c1:
        return c1
    c2 = user.get('urn', None)
    if c2:
        return urn_to_hrn(c2)
    return 'ANON user'

########## dump stuff
# run with migrate.py dump
# used in dump-all.sh that ran once on faraday to extract the data
def dump():
    accounts = parse_omf("ACCOUNTS", 'resources')
    # sample
    account = accounts[0]
    print("{} accounts, sample = ".format(len(accounts)),
          accountname(account), account.keys())

    # blacklist
    def is_black_listed(account):
        for bl in slice_blacklist:
            if bl in accountname(account):
                return True
        return False
    accounts = [account for account in accounts
                if not is_black_listed(account)]
    print("{} not blacklisted accounts".format(len(accounts)))

    def is_meaningful(account):
        # no user : discard
        if 'users' not in account or not account['users']:
            return False
        # only the myslice user : discard
        if len(account['users']) == 1 \
           and account['users'][0]['urn'] in special_user_urns:
            return False
        return True
    accounts = [ account for account in accounts if is_meaningful(account)]
    print("{} meaningful accounts".format(len(accounts)))
    
    print("---------------------------------------- {} ACCOUNTS"
          .format(len(accounts)))
    for account in accounts:
        print("{} ".format(accountname(account)))
        if 'users' not in account:
            print("  no users")
        else:
            for user in account['users']:
                print("  {}".format(username(user)))
    print("---------------------------------------- end accounts")

    ########################################
    users = parse_omf("USERS", 'resources')
    user = users[0]
    print("{} users, sample = {} - {}"
          .format(len(users), user['name'], user.keys()))
    print("users account sample {}".format(user['accounts'][0]))

    # blacklist
    def is_black_listed(user):
        for bl in users_blacklist:
            if bl in username(user):
                return True
        return False
    users = [user for user in users
                if not is_black_listed(user)]
    print("{} not blacklisted users".format(len(users)))

    print("---------------------------------------- {} USERS"
          .format(len(users)))
    for user in users:
        print("{} ".format(username(user)))
        if 'accounts' not in user:
            print("  no accounts")
        else:
            for account in user['accounts']:
                print("  {}".format(accountname(account)))
    print("----------------------------------------end users")

    ##########
    with open("USER-uuids", "w") as f:
        for user in users:
            f.write(user['uuid'] + "\n")

    keys = parse_omf("KEYS", 'resources')
    key = keys[0]
    print("{} keys, sample = {} / {}"
          .format(len(keys), key['user_id'], key.keys()))

    ##########
    print("{} accounts, {} users and {} keys"
          .format(len(accounts), len(users), len(keys)))

####################
# the names that we have manually selected in 'manually-selected'
def parse_selected():
    mode = None
    selected = {
        'accounts' : [], 'users' : [],
        'accounts-ren' : {},
        'users-ren' : {}
    }
    with open("manually-selected") as f:
        for line in f.readlines():
            if not line or line[0] == "\n" or line.startswith(" "):
                continue
            elif line.startswith("ACCOUNTS"):
                mode = 'accounts'
            elif line.startswith("USERS"):
                mode = 'users'
            elif not mode:
                continue
            elif ' - ' in line:
                old, new = line.strip().split(' - ')
                selected[mode + '-ren' ][old] = new
                selected[mode].append(old)
            else:
                selected[mode].append(line.strip())
    return selected['accounts'], selected['users'], selected['accounts-ren']

def rebuild():

    # the names that we have manually selected in 'manually-selected'
    sel_account_names, sel_user_names, account_renamings = parse_selected()
    print(len(sel_account_names), len(sel_user_names))
    print("SELECTED slices renaming")
    for old, new in account_renamings.items():
        print("{} -> {}".format(old, new))

    # the complete data
    accounts = parse_omf("ACCOUNTS", 'resources')
    users = parse_omf("USERS", 'resources')
    keys = parse_omf("KEYS", 'resources')
        
    print(len(accounts), len(users), len(keys))

    accounts_by_urn = { account['urn'] : account for account in accounts }
    accounts_by_hrn = { accountname(account) : account for account in accounts }
    sel_accounts = [ accounts_by_hrn[name] for name in sel_account_names ]
    sel_account_uuids = { account['uuid'] for account in sel_accounts }
    print(len(accounts_by_hrn), len(accounts_by_urn),
          len(sel_account_uuids))
    

    return 0


####################        
def main(*args):
    function_name = args[0]
    function = globals()[function_name]
    function(*args[1:])
    return 0

if __name__ == '__main__':
    exit(main(*sys.argv[1:]))
