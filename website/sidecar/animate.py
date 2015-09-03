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
default_cycle = 0.5
default_runs = 0

node_ids = range(1, 38)
default_max_nodes_impacted = 10
busy_values = [ 'busy', 'free' ]
status_values = [ 'on', 'off' ]

def init_status(verbose):
    complete = [ random_status(id) for id in node_ids ]
    with open(complete_filename, 'w') as f:
        if verbose:
            print 'Creating ' + complete_filename
        f.write(json.dumps(complete))

def random_ids(max_nodes_impacted):
    how_many = random.randint(1, max_nodes_impacted)
    return [ random.choice(node_ids) for i in range(how_many)]

def random_status(id):
    return {
        'id' : id,
        'busy' : random.choice(busy_values),
        'status' : random.choice(status_values)
        }
    
def main():
    parser = ArgumentParser()
    parser.add_argument('-c', '--cycle', dest='cycle', default=default_cycle,
                        type=float,
                        help="Cycle duration in seconds (default={})".format(default_cycle))
    parser.add_argument('-r', '--runs', dest='runs', default=default_runs,
                        type=int,
                        help="How many runs (default={}; 0 means forever)".format(default_cycle))
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
        output = [ random_status(id) for id in random_ids(args.max_nodes_impacted)]
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
