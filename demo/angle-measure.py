#!/usr/bin/env python2

"""
This NEPI script is for orchestrating an experiment on R2lab

Purpose is to reproduce the measurement of the angle of arrival
of a wireless flow between
* a sender that uses a single antenna
* a receiver that uses 3 aligned antennas, iso-spaced by 3cm:

     (1) <-- 3cm --> (2) <-- 3cm --> (3)
  
You can see this python script as a description of the dependencies between
* initializations, i.e. setting up wireless drivers, devices,
  antennas and monitoring for data capture
* running (actually sending traffic)
* data retrieval 

The details of each of these steps are written as a single shell
script code (angle-measure.sh) that gives the details of each of these steps 
on a single host (either sender or receiver)

So e.g.
angle-measure.sh init-sender 64 20MHz 
would setup the sender-side wireless system to use channel 64 and 20MHz bands

"""

########################################
# for using print() in python3-style even in python2
from __future__ import print_function

import os, os.path
import time
import logging
from argparse import ArgumentParser

# import nepi library and other required packages
from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState

ec = ExperimentController(exp_id="angle-measure")

# using external shell script like e.g.:
# angle-measure.sh init-sender channel bandwidth

########## helpers
# this can run on the prep-lab for dry runs
def credentials(production):
    "returns a triple (hostname, username, key)"
    if production:
        return 'faraday.inria.fr', 'onelab.inria.mario.tutorial', '~/.ssh/onelab.private'
    else:
        return 'bemol.pl.sophia.inria.fr', 'regular', '~/.ssh/onelab.private'
    
def sender_receiver(production):
    "returns a tuple (sender, receiver)"
    if production:
        return "fit30", "fit31"
    else:
        return "fit04", "fit41"

########## how and where to store results
def get_app_trace(app, appname, rundir, tracename, outfile):
    if not os.path.isdir(rundir):
        os.makedirs(rundir)
    outpath = os.path.join(rundir, outfile)
    with open(outpath, 'w') as f:
        f.write(ec.trace(app, tracename))
    print(4*'=', "Stored trace {} for app {} in {}"
          .format(tracename, appname, outpath))

def get_app_stdout(app, appname, rundir):
    get_app_trace(app, appname, rundir, "stdout", "{}.out".format(appname))

########## the experiment
def main():

#    logging.getLogger('sshfuncs').setLevel(logging.DEBUG)
#    logging.getLogger('application').setLevel(logging.DEBUG)

    parser = ArgumentParser()
    parser.add_argument("-p", "--production", dest='production', action='store_true',
                        default=False, help="Run in preplab")

    # select sender and receiver nodes
    parser.add_argument("-s", "--sender", default=None)
    parser.add_argument("-r", "--receiver", default=None)
    
    # select how many packets, and how often they are sent
    parser.add_argument("-a", "--packets", type=int, default=10000,
                        help="nb of packets to send")
    parser.add_argument("-e", "--period", type=int, default=1000,
                        help="time between packets in micro-seconds")

    # partial runs, dry runs
    parser.add_argument("-n", "--dry-run", action='store_true',
                        default=False, help="Show experiment context and exit - do nothing")
    parser.add_argument("-i", "--skip-init", dest='skip_init', action='store_true',
                        default=False, help="Skip initialization")
    args = parser.parse_args()

    # get credentials, depending on target testbed (preplab or production chamber)
    gwhost, gwuser, key = credentials(args.production)

    # get defaults for target nodes, either on preplab or production
    sendername, receivername = sender_receiver(args.production)
    # but can always be overridden
    if args.sender is not None:  sendername = args.sender
    if args.receiver is not None:  receivername = args.receiver

    packets = args.packets
    period = args.period

    # we keep all 'environment' data for one run in a dedicated subdir
    # using this name scheme to store results locally
    dataname = "csi-{}-{}-{}-{}".format(
        receivername, sendername, packets, period)

    ########## display context and exit if -n is provided
    if args.dry_run:
        print("Using gateway {gwhost} with account {gwuser}\n"
              "Using sender = {sendername}, "
              "Using receiver = {receivername}, "
              .format(**locals()))
        print("Sending {packets} packets, one each {period} micro-seconds"
              .format(**locals()))
        exit(0)

    # the sender node
    sender = ec.register_resource(
        "linux::Node",
        username = 'root',
        hostname = sendername,
        gateway = gwhost,
        gatewayUser = gwuser,
        identity = key,
        cleanExperiment = True,
        cleanProcesses = True,
        autoDeploy = True)

    # the receiver node
    receiver = ec.register_resource(
        "linux::Node",
        username = 'root',
        hostname = receivername,
        gateway = gwhost,
        gatewayUser = gwuser,
        identity = key,
        cleanExperiment = True,
        cleanProcesses = True,
        autoDeploy = True)

    # an app to init the sender
    init_sender = ec.register_resource(
        "linux::Application",
        code = "angle-measure.sh",
        command = "${CODE} init-sender 64 HT20",
        autoDeploy = True,
        connectedTo = sender)

    # an app to init the receiver
    init_receiver = ec.register_resource(
        "linux::Application",
        code = "angle-measure.sh",
        command = "${CODE} init-receiver 64 HT20",
        autoDeploy = True,
        connectedTo = receiver)

    # init phase
    if not args.skip_init:
        print(10*'-', 'Drivers Initialization')
        ec.wait_finished( [init_sender, init_receiver] )
        get_app_stdout(init_sender, "sender-init", dataname)
        get_app_stdout(init_receiver, "receiver-init", dataname)
        
    # an app to run the sender
    run_sender = ec.register_resource(
        "linux::Application",
        code = "angle-measure.sh",
        # beware of curly brackets with format
        command = "${{CODE}} run-sender {} {}".format(packets, period),
        autoDeploy = True,
        connectedTo = sender)

    # an app to run the receiver
    run_receiver = ec.register_resource(
        "linux::Application",
        code = "angle-measure.sh",
        # beware of curly brackets with format
        command = "${{CODE}} run-receiver {} {}".format(packets, period),
        autoDeploy = True,
        splitStderr = True,
        connectedTo = receiver)

    # run
    print(10*'-', 'Managing radio traffic')
    ec.wait_finished( [run_sender, run_receiver] )

    # collect data
    print(10*'-', 'Collecting data in {}'.format(dataname))
    get_app_stdout(run_sender, "sender-run", dataname)
    get_app_trace(run_receiver, "receiver-run", dataname,
                  "stderr", "receiver-run.err")
    # raw data gets to go in the current directory as it's more convenient to manage
    # also it's safe to wait for a little while
    time.sleep(5)
    get_app_trace(run_receiver, "receiver-run", ".", "stdout", dataname+".raw")
    
    # we're done
    ec.shutdown()

if __name__ == '__main__':
    main()
