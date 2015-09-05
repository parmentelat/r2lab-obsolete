#!/usr/bin/env python

# XXX - todo
# it would make a lot of sense to make sure that changes (as written in news)
# get reflected in the complete status file as well


import random
import json
import time

from argparse import ArgumentParser

#
complete_filename = 'r2lab-complete.json'
news_filename = 'r2lab-news.json'

# in s
default_cycle = 1
default_runs = 0

node_ids = range(1, 38)
default_max_nodes_impacted = 10
field_values = {
    'cmc_on_off' : [ 'on', 'off', 'fail' ],
    'control_ping' : [ 'on', 'off' ],
    'control_ssh' : [ 'on', 'off' ],
    'os_release' : [ 'fedora-21', 'ubuntu-15.04', 'fedora-21-gnuradio', 'fail' ],
# not supported yet
#    'data_ping' : [ 'on', 'off' ],
}

def init_status(verbose):
    complete = [ random_status(id) for id in node_ids ]
    with open(complete_filename, 'w') as f:
        if verbose:
            print 'Creating ' + complete_filename
        f.write(json.dumps(complete))

def random_ids(max_nodes_impacted):
    how_many = random.randint(1, max_nodes_impacted)
    return [ random.choice(node_ids) for i in range(how_many)]

# heuristics to avoid too inconsistent data
def normalize_status(node_info):
    if node_info['os_release'] != 'fail':
        node_info.update({'cmc_on_off' : 'on',
                          'control_ping' : 'on',
                          'control_ssh' : 'on',
        })
    return node_info

def random_status(id, index=0):
    # for testing incomplete news on the livemap side
    # we expose one or the other or both
    # however the default always expose the full monty
    node_info = { 'id' : id }
    # fill node_info with all known keys
    node_info.update( { field : random.choice(values) 
                       for field, values in field_values.iteritems() })
    # make sure this is mostly consistent
    normalize_status(node_info)
    # index == 0 means we need a complete record
    # otherwise let's remove some
    items_to_remove = index % len(field_values)
    keys_to_remove = random.sample(field_values.keys(), items_to_remove)
    for field in keys_to_remove:
        del node_info[field]
    return node_info
    
def main():
    parser = ArgumentParser()
    parser.add_argument('-c', '--cycle', dest='cycle', default=default_cycle,
                        type=float,
                        help="Cycle duration in seconds (default={})".format(default_cycle))
    parser.add_argument('-r', '--runs', dest='runs', default=default_runs,
                        type=int,
                        help="How many runs (default={}; 0 means forever)".format(default_runs))
    parser.add_argument('-n', '--nodes', dest='max_nodes_impacted', default=default_max_nodes_impacted,
                        type=int,
                        help="Maximum number of nodes impacted by each cycle")
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    args = parser.parse_args()

    cycle = args.cycle
    
    init_status(args.verbose)
    
    if args.verbose:
        print "Using cycle {}s".format(cycle)
    counter = 0
    while True:
        output = [ random_status(id, index)
                   for index, id in enumerate(random_ids(args.max_nodes_impacted))]
        with open(news_filename, 'w') as f:
            if args.verbose:
                print output
            f.write(json.dumps(output))
        counter += 1
        if args.runs and counter >= args.runs:
            break
        time.sleep(cycle)

if __name__ == '__main__':
    main()
