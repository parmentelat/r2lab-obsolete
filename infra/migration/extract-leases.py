#!/usr/bin/python3

# database location is defined
# in
# /root/omf_sfa/etc/omf-sfa/omf-sfa-am.yaml
# as
# database: postgres://omf_sfa:<pass>@localhost/inventory

from argparse import ArgumentParser
# pip3 install pygresql
from pg import DB

import json

dbname = "inventory"
dbuser = "omf_sfa"
dbhost = "localhost"

def retrieve_leases(password):

    db = DB(dbname = dbname,
            host   = dbhost,
            user   = dbuser,
            passwd = password)

    # this obviously is some kind of join...

    # get all leases
    leases    = db.query("""select id, valid_from, valid_until, status from leases""").getresult()

    # get list of leases - accounts
    leases_accounts = db.query("""select id, account_id from resources where type='OMF::SFA::Model::Lease'""").getresult()

    # get list of accounts
    account_names = db.query("""select id, name from resources where type='OMF::SFA::Model::Account'""").getresult()

    # hash account name from account id
    account_name_by_account_id = { account_id: name for account_id, name in account_names }

    # hash account name from lease_id
    account_name_by_lease_id = {
        lease_id : account_name_by_account_id[account_id]
        for lease_id, account_id in leases_accounts
        }

    # produce a list of tuples
    # slicename, valid_from, valid_until, status
    return [
        (account_name_by_lease_id[lease_id], valid_from, valid_until, status)
        for lease_id, valid_from, valid_until, status in leases
    ]

def sort_leases_by_slice(leases):
    leases.sort(key = lambda l: l[0])

def sort_leases_by_time(leases):
    leases.sort(key = lambda l: l[1])

def main():
    parser = ArgumentParser()
    parser.add_argument('-s', '--sort-slice', action='store_true', default=False,
                        help="sort by slicename instead of by time")
    parser.add_argument('-c', '--discard-cancelled', action='store_true', default=False,
                        help="discard leases marked as cancelled - whatever that means")
    # broken for now, datetime objects cannot be serialized
    #parser.add_argument('-j', '--json', metavar='json-file', help="produce JSON")
    parser.add_argument('password')
    args = parser.parse_args()
    password = args.password

    # retrieve from DB
    leases = retrieve_leases(password)

    # filter out cancelled leases if requested
    if args.discard_cancelled:
        leases = [lease for lease in leases if lease[3] != 'cancelled']

    # sort
    sort_leases_function = sort_leases_by_slice if args.sort_slice else sort_leases_by_time
    sort_leases_function(leases)

    # broken for now
    #write_json = args.json
    write_json = False
    if write_json:
        with open(args.json, 'w') as output:
            output.write(json.dumps(leases))
        print("(Over)wrote {}".format(args.json))
    else:
        for lease in leases:
            print(lease)


if __name__ == '__main__':
    main()    
