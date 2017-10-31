#!/usr/bin/env python3

"""
Rewritten nightly script.

Features:

(*) designed to be run on an hourly basis, at typically nn:01
    will check for a lease being currently held by nightly slice; returns if not
(*) defaults to all nodes but can exclude some hand-picked ones on the command-line
(*) updates sidecar status (available) 
(*) sends status mail 

Performed checks on all nodes:

(*) turn node on - check it answers ping
(*) turn node off - check it does not answer ping
(*) uses 2 reference images (typically fedora and ubuntu)
(*) uploads first one, check for running image 
(*) uploads second one, check for running image 

"""

import sys
from argparse import ArgumentParser

import asyncio

from asynciojobs import Scheduler, Job
from apssh import SshNode, SshJob

from rhubarbe.config import Config
from rhubarbe.imagesrepo import ImagesRepo
from rhubarbe.display import Display

from rhubarbe.main import check_reservation
from rhubarbe.node import Node
from rhubarbe.selector import Selector, add_selector_arguments, selected_selector, MisformedRange
from rhubarbe.imageloader import ImageLoader
from rhubarbe.ssh import SshProxy as SshWaiter

### globals
# each image is defined by a tuple
#  0: image name (for rload)
#  1: string to expect in /etc/rhubarbe-image
images_to_try = [
    ( "ubuntu", "ubuntu-16.04" ),
    ( "fedora", "fedoraxxx"),
]



# not sure how progressbar would behave in unattended mode with no terminal
# and so no width to display a progressbar..
class NoProgressBarDisplay(Display):
    def dispatch_ip_percent_hook(self, *args):
        print('.', end='', flush=True)
    def dispatch_ip_tick_hook(self, *args):
        print('.', end='', flush=True)



class Nightly:

    def __init__(self, selector, test):
        # work selector; will remove nodes as they fail 
        self.selector = selector
        self.test = test
        ##########
        # keep a backup of initial scope for proper cleanup
        self.all_names = selector.cmc_names()
        # retrieve bandwidth from rhubarbe config
        config = Config()
        self.bandwidth = int(config.value('networking', 'bandwidth'))
        self.backoff = int(config.value('networking', 'ssh_backoff'))
        #self.cmc_timeout = float(config.value('nodes', 'cmc_default_timeout'))
        self.load_timeout = float(config.value('nodes', 'load_default_timeout'))
        self.wait_timeout = float(config.value('nodes', 'wait_default_timeout'))
        
        # accessories
        self.bus = asyncio.Queue()
        self.testmsg("focus is {}"
                     .format(" ".join(selector.node_names())))

    
    def testmsg(self, *args):
        if self.test:
            print("test:", *args)

    def mark_and_exclude(self, node):
        """ 
        what to do when a node is found as being non-nominal
        (*) remove it from further actions
        (*) mark it as unavailable
        """ 
        self.selector.add_or_delete(node.id, add_if_true=False)
        print("TODO: node {} should be marked unavailable"
              .format(node.id))


    def global_send_action(self, mode):
        delay = 5.
        self.testmsg("delay={}".format(delay))
        nodes = { Node(x, self.bus) for x in self.selector.cmc_names() }
        actions = (node.send_action(message=mode, check=True, check_delay=delay)
                   for node in nodes)
        result = asyncio.get_event_loop().run_until_complete(
            asyncio.gather(*actions)
        )
        message = "turn on" if mode == 'on' \
                  else "turn off" if mode == 'off' \
                       else "reset"
        for node in nodes:
            if node.action:
                print("{}: {} OK"
                      .format(node.control_hostname(), message))
            else:
                print("{}: COULD NOT {} - marked as FAIL"
                      .format(node.control_hostname(), message))
                self.mark_and_exclude(node)
                      

    def global_load_image(self, image_name):

        # locate image
        the_imagesrepo = ImagesRepo()
        actual_image = the_imagesrepo.locate_image(image_name, look_in_global=True)
        if not actual_image:
            print("Image file {} not found - emergency exit"
                  .format(image_name))
            exit(1)

        # load image
        nodes = { Node(x, self.bus) for x in self.selector.cmc_names() }
        display = NoProgressBarDisplay(nodes, self.bus)
        self.testmsg("image={}".format(actual_image))
        self.testmsg("bandwidth={}".format(self.bandwidth))
        self.testmsg("timeout={}".format(self.load_timeout))
        loader = ImageLoader(nodes, image=actual_image,
                             bandwidth=self.bandwidth,
                             message_bus=self.bus, display=display)
        loader.main(reset=True, timeout=self.load_timeout)

    def global_wait_ssh(self):
        # wait for nodes to be ssh-reachable 
        nodes = { Node(x, self.bus) for x in self.selector.cmc_names() }
        display = NoProgressBarDisplay(nodes, self.bus)
        print("Waiting for {} nodes (timeout={})"
              .format(len(nodes), self.wait_timeout))
        sshs = [SshWaiter(node, verbose=self.test) for node in nodes]
        jobs = [Job(ssh.wait_for(self.backoff), critical=False) for ssh in sshs]

        scheduler = Scheduler(Job(display.run(), forever=True), *jobs)
        if not scheduler.orchestrate(timeout = self.wait_timeout):
            self.test and scheduler.debrief()
        # exclude nodes that have not behaved
        for node, job in zip(nodes, jobs):
            print("node-> {} job -> done={} exc={}"
                  .format(node.id, job.is_done(), job.raised_exception()))

            if job.raised_exception():
                self.mark_and_exclude(node)

    def global_check_image(self, check_string):
        # on the remaining nodes: check image marker
        nodes = { Node(x, self.bus) for x in self.selector.cmc_names() }
        display = NoProgressBarDisplay(nodes, self.bus)
        print("Checking {} nodes against {} in /etc/rhubarbe-image"
              .format(len(nodes), check_string))

        check_command = "tail -1 /etc/rhubarbe-image | grep -q {}"\
                        .format(check_string)
        jobs = [
            SshJob(node = SshNode(hostname=node.control_hostname()),
                   command = check_command,
                   critical=False)
            for node in nodes
        ]
        
        scheduler = Scheduler(Job(display.run(), forever=True), *jobs)
        if not scheduler.orchestrate(timeout = self.wait_timeout):
            self.test and scheduler.debrief()
        # exclude nodes that have not behaved
        for node, job in zip(nodes, jobs):
            if not job.is_done() or job.raised_exception():
                self.testmsg("S/t badly wrong with {}".format(node))
                self.mark_and_exclude(node)
                continue
            if not job.result() == 0:
                self.testmsg("Wrong image found on {}".format(node))
                self.mark_and_exclude(node)
                continue

    def check_lease(self):
        """
        """
        return check_reservation(
            message_bus=self.bus,
            verbose = self.test)
        

    def run(self):
        """
        does everything and returns True if all nodes are fine
        """

        if not self.check_lease():
            print("no lease - exiting")
            exit(0)

        self.global_send_action('on')
        self.global_send_action('reset')
        self.global_send_action('off')
        # it's no use trying to send reset to a node that is off

        for image, check_string in images_to_try:
            # xxx could use a flag a bit like --reset to skip this one
            self.global_load_image(image)
            self.global_wait_ssh()
            self.global_check_image(check_string)

        # True means everything is OK
        return True
        

####################    
usage = """
Run nightly check procedure on R2lab
"""

def main(*argv):
    parser = ArgumentParser(usage=usage)
    parser.add_argument("-t", "--test", action='store_true', default=False,
                        help="for testing purposes only")
    add_selector_arguments(parser)

    args = parser.parse_args(argv)

    selector = selected_selector(args)
    nightly = Nightly(selector, args.test)
    
    return 0 if nightly.run() else 1

if __name__ == '__main__':
    try:
        exit(main(*sys.argv[1:]))
    except MisformedRange as e:
        print("ERROR: ", e)
        exit(1)
