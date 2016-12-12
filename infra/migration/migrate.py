#!/usr/bin/env python3

from __future__ import print_function

import sys
import os
import json

import ssl
import xmlrpc.client

from sfa.util.xrn import Xrn

all_mode = False
all_mode = True

unique_hostname = '37nodes.r2lab.inria.fr'

slice_blacklist = [
    "totoproj", "mario.tutorial", "r2lab.mario_test",
    "onelab.upmc.test2radomir",
    "upmc.test", "thierry.admin1"
] if not all_mode else []

# we need these if only for leases,
# but in omf they had no user so they get
# removed in the cleanup/selection process
manual_slices = [
    "onelab.inria.r2lab.tutorial",
    "onelab.inria.naoufal.mesh",
    "onelab.upmc.pltutorial.emulation",
]

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

def username_to_plc_sitename(username):
    ol, site, *_ = username.split('.')
    return "{}.{}".format(ol, site)

def plc_compliant_slicename(slicename):
    pieces = slicename.split('.')
    assert len(pieces) == 4

    ol, site, proj, sl = pieces
    return ("{}.{}_{}.{}".format(ol, site, proj, sl))

########## dump stuff
# run with migrate.py dump
# used in dump-all.sh that ran once on faraday to extract the data
def dump():
    accounts = parse_omf("DATA/ACCOUNTS", 'resources')
    # sample
    account = accounts[0]
    print("{} accounts in ACCOUNTS".format(len(accounts)))

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
    users = parse_omf("DATA/USERS", 'resources')
    user = users[0]
    print("{} users".format(len(users)))

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
    with open("DATA/USER-uuids", "w") as f:
        for user in users:
            f.write(user['uuid'] + "\n")

    keys = parse_omf("DATA/KEYS", 'resources')
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
        'users-details' : {},
    }
    with open("manually-selected") as f:
        for line in f.readlines():
            if not line or line[0] == "\n" or line.startswith(" ") or line.startswith('#'):
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
            elif len(line.split(' ')) == 4:
                assert mode == 'users'
                hrn, first_name, last_name, email = line.strip().split(' ')
                selected['users'].append(hrn)
                selected['users-details'][hrn] = (first_name, last_name, email)
            else:
                selected[mode].append(line.strip())
    return selected['accounts'], selected['users'],\
        selected['accounts-ren'], selected['users-details']

####################
def notify_start():
    os.system("rm -rf MAILS/NOTIFY*")

mail_message="""
Subject: R2lab migration - your new slice names

Hello {first_name}

This is an automated message from the R2lab Testbed

Our registration system has been totally rewritten,
and as part of this move your account has been
migrated into the new system with the following 
attributes:

first name : {first_name}
last name  : {last_name}
email      : {email}

Besides, you will find below the new names for the slices
that your account is granted access to.

So to be clear, the right-hand side names are the login names
that you can use to enter the R2lab gateway at faraday.inria.fr
through ssh.

"""

def notify_init(email, first_name, last_name):
    with open("NOTIFY-{}".format(email), 'a') as f:
        f.write(mail_message.format(**locals()))

def notify_record(email, old_hrn, new_hrn):
    with open("NOTIFY-{}".format(email), 'a') as f:
        f.write("{} \n  is now know as\t\t{}\n"
                .format(old_hrn, new_hrn))

def auth_plcapi():

    plc_host='r2labapi.pl.sophia.inria.fr'
    api_url = "https://%s:443/PLCAPI/"%plc_host
    auth = { 'AuthMethod' : 'password',
             'Username'   : 'root@r2lab.inria.fr',
             'AuthString' : 'onecalvin',
    }
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    context.check_hostname = False

    class AutoAuthApi(xmlrpc.client.ServerProxy):
        def __init__(self):
            xmlrpc.client.ServerProxy.__init__(
                self, api_url, allow_none=True, context=context)
            
        def __getattr__(self, attr):
            def fun(*args, **kwds):
                print(attr, *args, **kwds)
                actual_fun = xmlrpc.client.ServerProxy.__getattr__(
                    self, attr)
                try:
                    return actual_fun(auth, *args, **kwds)
                except Exception as e:
                    print("ignored exception in {} : {}"
                          .format(attr, e))
            return fun
    return AutoAuthApi()
                    

# a fake version
def dummy_auth_plcapi():
    class DummyApi:
        def __getattr__(self, attr):
            def fun(*args, **kwds):
                print(attr, "((", *args, **kwds)
            return fun
    return DummyApi()

####################
def rebuild():

    # the names that we have manually selected in 'manually-selected'
    sel_account_names, sel_user_names, account_renamings, users_details = parse_selected()
    print("SELECTED slices renaming")
    for old, new in account_renamings.items():
        print("{} -> {}".format(old, new))

    # the complete data
    accounts = parse_omf("DATA/ACCOUNTS", 'resources')
    users = parse_omf("DATA/USERS", 'resources')
    keys = parse_omf("DATA/KEYS", 'resources')
        
    print("{} accounts, {} users, {} keys".format(len(accounts), len(users), len(keys)))

    accounts_by_urn = { account['urn'] : account for account in accounts }
    accounts_by_hrn = { accountname(account) : account for account in accounts }
    sel_accounts = [ accounts_by_hrn.get(name, None) for name in sel_account_names ]
    sel_accounts = [ a for a in sel_accounts if a ]
    sel_accounts_by_hrn = { accountname(account) : account for account in sel_accounts }
    sel_accounts_by_urn = { account['urn'] : account for account in sel_accounts }
    sel_account_uuids = { account['uuid'] for account in sel_accounts }
    print(
        "all accounts", len(accounts),
        "all accounts by hrn", len(accounts_by_hrn),
        "all accounts by urn", len(accounts_by_urn),
        "sel account by hrn", len(sel_accounts_by_hrn),
        "sel account by urn", len(sel_accounts_by_urn),
    )
    
    users_by_urn = { user['urn'] : user for user in users }
    users_by_hrn = { username(user) : user for user in users }
    sel_users = [ users_by_hrn[name] for name in sel_user_names ]
    sel_users_by_hrn = { username(user) : user for user in sel_users }
    sel_users_by_urn = { user['urn'] : user for user in sel_users }
    sel_user_uuids = { user['uuid'] for user in sel_users }
    print(
        "all users", len(users),
        "all users by hrn", len(users_by_hrn),
        "all users by urn", len(users_by_urn),
        "sel user by hrn", len(sel_users_by_hrn),
        "sel user by urn", len(sel_users_by_urn),
    )

    print("============================== node and sites")
    notify_start()
    plcapi = auth_plcapi()


    plcapi.AddSite({'name' : 'Anechoic Chamber',
                    'login_base' : 'r2lab',
                    'abbreviated_name' : 'R2lab'})
    sitenames = { username_to_plc_sitename(hrn)
                  for hrn in sel_users_by_hrn.keys()}
    plcapi.AddNode('r2lab',
                   {'hostname' : unique_hostname,
                    'node_type' : 'reservable' })

    for sitename in sitenames:
        plcapi.AddSite(
            {'login_base' : sitename, 'name' : sitename,
             'abbreviated_name': sitename, 'max_slices' : 100 })
    
    # creating users and keys
    print("============================== users and keys")
    for hrn, user in sel_users_by_hrn.items():
        first_name, last_name, email = users_details[hrn]
#        print("USER", hrn, email, first_name, last_name)
        plcapi.AddPerson(
            {'email' : email, 'hrn' : hrn,
             'first_name' : first_name, 'last_name' : last_name})
        plcapi.UpdatePerson(email, {'enabled' : True})
        plcapi.AddRoleToPerson('user', email)
        sitename = username_to_plc_sitename(hrn)
        plcapi.AddPersonToSite(email, sitename)
        notify_init(email, first_name, last_name)
        user_uuid = user['uuid']
        keys = parse_omf("DATA/{}.keys".format(user_uuid), 'resources')
        for key in keys:
            plcapi.AddPersonKey(
                email,
                { 'key_type' : 'ssh',
                  'key' : key['ssh_key'] })

#    print("early exit")
#    exit(1)

    # creating slices
    print("============================== slices")
    for hrn, account in sel_accounts_by_hrn.items():
        new_hrn = account_renamings.get(hrn, hrn)
        new_hrn = plc_compliant_slicename(new_hrn)
        was_renamed = new_hrn != hrn
#        print("SLICE", "**" if was_renamed else "", new_hrn)
        plcapi.AddSlice({'name' : new_hrn})
        plcapi.AddSliceToNodes(new_hrn, [ unique_hostname ])
        for user in account['users']:
            userhrn = username(user)
            if userhrn in sel_users_by_hrn:
                _, _, email = users_details[userhrn]
                plcapi.AddPersonToSlice(email, new_hrn)
#                print('\t\t\t\t++++', userhrn)
                if was_renamed:
                    notify_record(email, hrn, new_hrn)

    

    # leases
    for slicename in manual_slices:
        new_hrn = plc_compliant_slicename(slicename)
        plcapi.AddSlice({'name' : new_hrn})
        plcapi.AddSliceToNodes(new_hrn, [ unique_hostname ])
    with open("DATA/LEASES.json") as f:
        leases = json.loads(f.read())
    for lease in leases:
        try:
            hrn, from_st, until_st, status = lease
            new_hrn = account_renamings.get(hrn, hrn)
            slname = plc_compliant_slicename(new_hrn)
            print("lease {} {}".format(slname, status))
            plcapi.AddLeases( [ unique_hostname ], slname,
                              int(from_st), int(until_st))
        except Exception as e:
            print("oops,", e)

    return 0


####################        
def main(*args):
    function_name = args[0]
    function = globals()[function_name]
    function(*args[1:])
    return 0

if __name__ == '__main__':
    exit(main(*sys.argv[1:]))
