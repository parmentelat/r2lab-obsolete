#!/usr/bin/env python3

import asyncio
try:
    from asyncio import ensure_future
except:
    from asyncio import async as ensure_future

import os
from argparse import ArgumentParser

from selector import Selector
from cmc import CMC


def add_range_arguments(parser):
    parser.add_argument(
        "-a", "--all-nodes", action='store_true', default=False,
        help="""
        add the contents of the ALL_NODES env. variable in the mix
        this can be combined with ranges, like e.g.
        -a ~4-16-2
        """)
    parser.add_argument(
        "ranges", nargs="*",
        help="""
        nodes can be specified one by one, like 1 004 fit01 reboot01
        by range (inclusive) like 2-12, fit4-reboot12,
        by range+step like 4-16-2 which would be all even numbers from 4 to 16,
        ranges can also be excluded with ~; so ~1-4 means remove 1,2,3,4
        """)
        
def selected_selector(parser_args):        
    ranges = parser_args.ranges
    
    # our naming conventions
    selector = Selector('fit', 'reboot')
    # nothing set on the command line : let's use $NODES
    if parser_args.all_nodes:
        selector.add_range(os.environ["ALL_NODES"])
    if not ranges:
        for node in os.environ["NODES"].split():
            selector.add_range(node)
    else:
        for range in ranges:
            selector.add_range(range)

    return selector


def load():
    parser = ArgumentParser()
    parser.add_argument("-v", "--verbose", action='store_true', default=False)
    add_range_arguments(parser)
    args = parser.parse_args()

    selector = selected_selector(args)

    if args.verbose:
        for node in selector.node_names():
            print(node)
    exit()

    cmcs = ( CMC(cmc_name) for cmc_name in selector.cmc_names() )

    loop = asyncio.get_event_loop()
    tasks = [ensure_future(cmc.ensure_reset()) for cmc in cmcs]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

if __name__ == '__main__':
    load()
