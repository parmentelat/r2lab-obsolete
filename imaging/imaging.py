#!/usr/bin/env python3

import asyncio
try:
    from asyncio import ensure_future
except:
    from asyncio import async as ensure_future

from argparse import ArgumentParser

from cmc import CMC
from selector import add_selector_arguments, selected_selector
from imageloader import ImageLoader

def load():
    parser = ArgumentParser()
    parser.add_argument("-v", "--verbose", action='store_true', default=False)
    add_selector_arguments(parser)
    args = parser.parse_args()

    selector = selected_selector(args)

    print(selector)

    cmcs = [ CMC(cmc_name) for cmc_name in selector.cmc_names() ]

    for cmc in cmcs:
        print("cmc: {} -> mac: {}".format(cmc, cmc.control_mac_address()))
        if not cmc.is_known():
            print("WARNING : cmc is not known to the inventory".format(cmc.hostname))

    # xxx config
    image_loader = ImageLoader(cmcs, timeout=60, idle=12)
    # direct pxelinux on frisbee, send reset and wait for all telnets
    image_loader.stage1()
    # run the frisbee session
    image_loader.stage2()
    # cleanup pxelinux all nodes again
#    image_loader.cleanup()
#    image_loader.reset()

def inventory():
    from inventory import the_inventory
    the_inventory.display(verbose=True)

def status():
    
    parser = ArgumentParser()
    parser.add_argument("-v", "--verbose", action='store_true', default=False)
    add_selector_arguments(parser)
    args = parser.parse_args()

    selector = selected_selector(args)

    cmcs = [ CMC(cmc_name) for cmc_name in selector.cmc_names() ]

    loop = asyncio.get_event_loop()
    tasks = [ensure_future(cmc.get_status_verbose()) for cmc in cmcs]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

import sys

supported_commands = [ 'load', 'status', 'inventory' ]

def main():
    command=sys.argv[0]
    for supported in supported_commands:
        if supported in command:
            main_function = globals()[supported]
            return main_function()
    print("Unknown command {}", command)

if __name__ == '__main__':
    main()
