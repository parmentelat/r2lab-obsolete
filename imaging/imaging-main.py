#!/usr/bin/env python3

import asyncio

from argparse import ArgumentParser
from logger import logger

from node import Node
from selector import add_selector_arguments, selected_selector
from imageloader import ImageLoader
from imagerepo import the_imagerepo
from config import the_config
import util

# for each of these there should be a symlink to imaging-main.py
# like imaging-load -> imaging-main.py
# and a function in this module with no arg
supported_commands = [ 'load', 'save', 'status', 'list' ]

####################
def load():
    default_image = the_imagerepo.default()
    default_timeout = the_config.value('nodes', 'load_default_timeout')
    default_bandwidth = the_config.value('networking', 'bandwidth')
                            
    parser = ArgumentParser()
    parser.add_argument("-v", "--verbose", action='store_true', default=False)
    parser.add_argument("-i", "--image", action='store', default=default_image,
                        help="Specify image to load (default is {})".format(default_image))
    parser.add_argument("-t", "--timeout", action='store', default=default_timeout, type=float,
                        help="Specify global timeout for the whole process, default={}"
                              .format(default_timeout))
    parser.add_argument("-b", "--bandwidth", action='store', default=default_bandwidth, type=int,
                        help="Set bandwidth in Mibps for frisbee uploading - default={}"
                              .format(default_bandwidth))

    add_selector_arguments(parser)

    # xxx this is truly more for debugging
    # I'd rather not have these in the help message...
    parser.add_argument("-1", "--skip-stage1", action='store_true', default=False)
    parser.add_argument("-2", "--skip-stage2", action='store_true', default=False)
    parser.add_argument("-3", "--skip-stage3", action='store_true', default=False)

    args = parser.parse_args()

    message_bus = asyncio.Queue()

    selector = selected_selector(args)
    nodes = [ Node(cmc_name, message_bus) for cmc_name in selector.cmc_names() ]

    message_bus.put_nowait({'selected_nodes' : selector})
    if args.verbose:
        message_bus.put_nowait('timeout', args.timeout)

    for node in nodes:
        if not node.is_known():
            logger.critical("WARNING : node {} is not known to the inventory".format(node.hostname))

    actual_image = the_imagerepo.locate(args.image)
    if not actual_image:
        print("Image file {} not found - emergency exit".format(args.image))
        exit(1)

    message_bus.put_nowait({'selected image' : actual_image})

    loader = ImageLoader(nodes, message_bus=message_bus, image=actual_image, bandwidth=args.bandwidth, timeout=args.timeout)
    return loader.main(
        skip_stage1 = args.skip_stage1,
        skip_stage2 = args.skip_stage2,
        skip_stage3 = args.skip_stage3
        )
 
####################
def save():
    print("save NYI")
    return 1

####################
def status():
    default_timeout = the_config.value('nodes', 'status_default_timeout')
    
    parser = ArgumentParser()
    parser.add_argument("-t", "--timeout", action='store', default=default_timeout, type=float,
                        help="Specify global timeout for the whole process, default={}"
                              .format(default_timeout))
    add_selector_arguments(parser)
    args = parser.parse_args()

    selector = selected_selector(args)
    message_bus = asyncio.Queue()
    
    print(selector)

    nodes = [ Node(cmc_name, message_bus) for cmc_name in selector.cmc_names() ]
    coros = [ node.get_status() for node in nodes ]
    
    loop = asyncio.get_event_loop()

    tasks = util.self_manage(asyncio.gather(*coros))
    wrapper = asyncio.wait_for(tasks, timeout = args.timeout)
    try:
        loop.run_until_complete(wrapper)
        for node in nodes:
            print("{}:{}".format(node.cmc_name, node.status))
        return 0
    except KeyboardInterrupt as e:
        print("imaging-status : keyboard interrupt - exiting")
        tasks.cancel()
        loop.run_forever()
        tasks.exception()
        return 1
    except asyncio.TimeoutError as e:
        print("imaging-status : timeout expired after {}s".format(args.timeout))
        return 1
    finally:
        loop.close()

####################
def list():
    parser = ArgumentParser()
    parser.add_argument("-c", "--config", action='store_true', default=False,
                        help="display configuration store")
    parser.add_argument("-i", "--images", action='store_true', default=False,
                        help="display available images")
    parser.add_argument("-n", "--inventory", action='store_true', default=False,
                        help="display nodes from inventory")
    parser.add_argument("-a", "--all", action='store_true', default=False)
    args = parser.parse_args()

    if args.config or args.all:
        the_config.display()
    if args.images or args.all:
        from imagerepo import the_imagerepo
        the_imagerepo.display()
    if args.inventory or args.all:
        from inventory import the_inventory
        the_inventory.display(verbose=True)
    return 0

####################
####################
####################
import sys

def main():
    command=sys.argv[0]
    for supported in supported_commands:
        if supported in command:
            main_function = globals()[supported]
            exit(main_function())
    print("Unknown command {}", command)

if __name__ == '__main__':
    main()
