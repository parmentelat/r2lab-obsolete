#!/usr/bin/env python3

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

# for using print() in python3-style even in python2
from __future__ import print_function

from argparse import ArgumentParser

# import nepi library and other required packages
from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState
from nepi.util.sshfuncs import logger

ec = ExperimentController(exp_id="angle-measure")

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


# using external shell script like e.g.:
# angle-measure.sh init-sender channel bandwidth

def show_app_trace(app, message, logname):
    out_name = "{}.out".format(logname)
    out_trace = ec.trace(app, "stdout")
    with open(out_name, 'w') as out:
        out.write(out_trace)
    print ("--- STDOUT : setup stdout for {} -- also in {}:\n"
           .format(message, out_name, out_trace))
    
def main():
    parser = ArgumentParser()
    parser.add_argument("-p", "--production", dest='production', action='store_true',
                        default=False, help="Run in preplab")
    # tmp
    parser.add_argument("-s", "--sender", default=None)
    parser.add_argument("-c", "--receiver", default=None)
    
    parser.add_argument("--packets", type=int, default=10000,
                        help="nb of packets to send")
    parser.add_argument("--period", type=int, default=1000,
                        help="time between packets in micro-seconds")

    parser.add_argument("-v", "--verbose", dest='verbose', action='store_true',
                        default=False, help="Show selected nodes and exit")
    parser.add_argument("-i", "--skip-init", dest='skip_init', action='store_true',
                        default=False, help="Skip initialization")
    args = parser.parse_args()

    gwhost, gwuser, key = credentials(args.production)
    # get defaults for preplab or production
    sendername, receivername = sender_receiver(args.production)
    # but can always be overridden
    if args.sender is not None:  sendername = args.sender
    if args.receiver is not None:  receivername = args.receiver

    if args.verbose:
        print("Using gateway {gwhost} with account {gwuser}\n"
              "Using sender = {sendername}, "
              "Using receiver = {receivername}, "
              .format(**locals()))
        print("Sending {args.packets} packets, one each {args.period} micro-seconds"
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

    # init
    if not args.skip_init:
        print(10*'-', 'Initialization')
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

        ec.wait_finished( [init_sender, init_receiver] )
        show_app_trace(init_sender, "sender init on {}".format(sendername), "sender-init")
        show_app_trace(init_receiver, "receiver init on {}".format(receivername), "receiver-init")
        print("DONE")
        
    # an app to run the sender
    run_sender = ec.register_resource(
        "linux::Application",
        code = "angle-measure.sh",
        # beware of curly brackets with format
        command = "${{CODE}} run-sender {} {}".format(args.packets, args.period),
        autoDeploy = True,
        connectedTo = sender)

    # an app to run the receiver
    run_receiver = ec.register_resource(
        "linux::Application",
        code = "angle-measure.sh",
        # beware of curly brackets with format
        command = "${{CODE}} run-receiver {} {}".format(args.packets, args.period),
        autoDeploy = True,
        connectedTo = receiver)

    # run
    print(10*'-', 'Managing radio traffic')
    ec.wait_finished( [run_sender, run_receiver] )
    show_app_trace(run_sender, "sender run on {}".format(sendername), "sender-run")
    show_app_trace(run_receiver, "receiver run on {}".format(receivername), "receiver-run")

    
    # we're done
    ec.shutdown()

if __name__ == '__main__':
    main()
