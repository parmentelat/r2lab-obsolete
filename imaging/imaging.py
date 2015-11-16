#!/usr/bin/env python3

import asyncio
try:
    from asyncio import ensure_future
except:
    from asyncio import async as ensure_future

from argparse import ArgumentParser

from selector import add_selector_arguments, selected_selector
from cmc import CMC

def load():
    parser = ArgumentParser()
    parser.add_argument("-v", "--verbose", action='store_true', default=False)
    add_selector_arguments(parser)
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
