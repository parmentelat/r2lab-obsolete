#!/usr/bin/env python3

import asyncio

from argparse import ArgumentParser
from logger import logger

from node import Node
from selector import add_selector_arguments, selected_selector
from imageloader import ImageLoader
from imagerepo import ImageRepo

# for each of these there should be a symlink to imaging-main.py
# like imaging-load -> imaging-main.py
# and a function in this module with no arg
supported_commands = [ 'load', 'save', 'list', 'status', 'inventory' ]

####################
def load():
    image_repo = ImageRepo()
    default_image = image_repo.default()

    parser = ArgumentParser()
    parser.add_argument("-v", "--verbose", action='store_true', default=False)
    parser.add_argument("-i", "--image", action='store', default=default_image,
                        help="Specify image to load (default is {})".format(default_image))
    parser.add_argument("-1", "--skip-stage1", action='store_true', default=False)
    parser.add_argument("-2", "--skip-stage2", action='store_true', default=False)
    parser.add_argument("-3", "--skip-stage3", action='store_true', default=False)
                        
    add_selector_arguments(parser)
    args = parser.parse_args()

    message_bus = asyncio.Queue()

    selector = selected_selector(args)
    nodes = [ Node(cmc_name, message_bus) for cmc_name in selector.cmc_names() ]

    for node in nodes:
        if not node.is_known():
            logger.critical("WARNING : node {} is not known to the inventory".format(node.hostname))

    actual_image = image_repo.locate(args.image)
    if not actual_image:
        print("Image file {} not found - emergency exit".format(args.image))
        exit(1)

    ImageLoader(nodes, message_bus, actual_image).main(
        skip_stage1 = args.skip_stage1,
        skip_stage2 = args.skip_stage2,
        skip_stage3 = args.skip_stage3
        )
 
####################
def list():
    ImageRepo().display()

####################
def status():
    
    parser = ArgumentParser()
    parser.add_argument("-v", "--verbose", action='store_true', default=False)
    add_selector_arguments(parser)
    args = parser.parse_args()

    selector = selected_selector(args)
    message_bus = asyncio.Queue()
    
    nodes = [ Node(cmc_name, message_bus) for cmc_name in selector.cmc_names() ]

    for node in nodes:
        asyncio.Task(node.get_status_verbose())
    asyncio.get_event_loop().run_forever()
    asyncio.get_event_loop().close()

####################
def inventory():
    from inventory import the_inventory
    the_inventory.display(verbose=True)

####################
####################
####################
import sys

def main():
    command=sys.argv[0]
    for supported in supported_commands:
        if supported in command:
            main_function = globals()[supported]
            return main_function()
    print("Unknown command {}", command)

if __name__ == '__main__':
    main()
