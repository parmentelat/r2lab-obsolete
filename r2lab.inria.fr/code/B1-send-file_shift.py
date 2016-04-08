#!/usr/bin/env python3

# for using print() in python3-style even in python2
from __future__ import print_function

import os, os.path
import time
import logging
from argparse import ArgumentParser

# import nepi library and other required packages
from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState
from nepi.util.sshfuncs import logger


########## helpers
# this can run on the prep-lab for dry runs
def credentials():
    "returns a triple (hostname, username, key)"
    return 'faraday.inria.fr', 'onelab.inria.mario.tutorial', '~/.ssh/onelab.private'


########## how and where to store results
def get_app_trace(ec, app, appname, rundir, tracename, outfile):
    if not os.path.isdir(rundir):
        os.makedirs(rundir)
    outpath = os.path.join(rundir, outfile)
    with open(outpath, 'w') as f:
        f.write(ec.trace(app, tracename))
    print(4*'=', "Stored trace {} for app {} in {}"
          .format(tracename, appname, outpath))


def get_app_stdout(ec, app, appname, rundir):
    get_app_trace(ec, app, appname, rundir, "stdout", "{}.out".format(appname))


########## one experiment
def one_run(gwhost, gwuser, key, sendername, receivername, file, port, storage):
    # we keep all 'environment' data for one run in a dedicated subdir
    # using this name scheme to store results locally
    dataname = os.path.join(storage, "csi-{}-{}-{}-{}"
                            .format(receivername, sendername, file, port))

    summary = "{} --> {} file {}"\
        .format(sendername, receivername, file)

    #fixed params home dirs
    gateway_dir = '/home/{}/'.format(gwuser)
    node_dir = '/home/'
    node_usr = 'root'
    my_dir   = os.path.dirname(os.path.abspath(__file__))

    # creating an ExperimentController (EC) to manage the experiment
    # the exp_id name should be unique for your experiment
    # it will be used on the various resources
    # to store results and similar functions
    ec = ExperimentController(exp_id="B1-send-file-shift")

    # creating local node
    local = ec.register_resource(
        "linux::Node",
        hostname = 'localhost',
        cleanExperiment = True,
        cleanProcesses = True,
        autoDeploy = True)

    # creating the gateway node
    gateway = ec.register_resource(
        "linux::Node",
        username = gwuser,
        hostname = gwhost,
        identity = key,
        cleanExperiment = True,
        cleanProcesses = True,
        autoDeploy = True)

    # creating the sender node
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

    # creating the receiver node
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

    # application to copy file from local to gateway
    cmd = 'scp {}/{} {}@{}:{}{}; '.\
           format(my_dir,file,
                  gwuser, gwhost, gateway_dir, file)
    run_local = ec.register_resource(
        "linux::Application",
        command = cmd,
        connectedTo = local)

    # application to copy file to sender from gateway
    cmd = 'scp {}{} {}@{}:{}{}; '.\
           format(gateway_dir, file,
                  node_usr, sendername, node_dir, file)
    run_gateway = ec.register_resource(
        "linux::Application",
        command = cmd,
        connectedTo = gateway)

    # receiver will listen for the file at port n
    cmd = 'nc -dl {} > {}{}'.\
          format(port, node_dir, file)
    run_receiver = ec.register_resource(
        "linux::Application",
        depends = "netcat",
        command = cmd,
        connectedTo = receiver)

    # sender will transfer the file to receiver at port n
    cmd = 'nc {} {} < {}{}'.\
          format(receivername, port, node_dir, file)
    run_sender = ec.register_resource(
        "linux::Application",
        depends = "netcat",
        command = cmd,
        connectedTo = sender)

    # receiver will list the dir after all process to check if the file is there
    cmd = 'ls -la {}'.format(node_dir)
    run_ls_receiver = ec.register_resource(
        "linux::Application",
        command = cmd,
        connectedTo = receiver)

    # defining that the node gateway can copy the file to sender only after the file is copied to it from local
    ec.register_condition(run_gateway, ResourceAction.START, run_local, ResourceState.STOPPED)

    # defining that the node receiver can listen for the file from sender only after the file is copied to it from gateway
    ec.register_condition(run_receiver, ResourceAction.START, run_gateway, ResourceState.STOPPED)

    # defining that the node sender can transfer file only after node receiver is listening
    ec.register_condition(run_sender, ResourceAction.START, run_receiver, ResourceState.STARTED, "5s")

    # defining that the node receiver will list the dir after the transmition from sender finishes
    ec.register_condition(run_ls_receiver, ResourceAction.START, run_receiver, ResourceState.STOPPED)

    # deploy all applications
    ec.deploy([run_local, run_gateway, run_sender, run_receiver, run_ls_receiver])

    #wait ls application to recovery the results and present after
    ec.wait_finished(run_ls_receiver)

    # recovering the results of each application
    print ("\n--- INFO: listing directory on receiver:")
    print (ec.trace(run_local, "stdout"))
    print (ec.trace(run_gateway, "stdout"))
    print (ec.trace(run_sender, "stdout"))
    print (ec.trace(run_receiver, "stdout"))
    print (ec.trace(run_ls_receiver, "stdout"))
    # shutting down the experiment
    ec.shutdown()


def main():
#    logging.getLogger('sshfuncs').setLevel(logging.DEBUG)
#    logging.getLogger('application').setLevel(logging.DEBUG)

    parser = ArgumentParser()

    # select sender and receiver nodes
    parser.add_argument("-r", "--receivers", action='append', default=[],
                        help="hostnames for the receiver nodes, additive")
    parser.add_argument("-s", "--senders", action='append', default=[],
                        help="hostnames for the sender node, additive")

    parser.add_argument("-d", "--storage-dir", default=".",
                        help="specify a directory for storing all results")
    # select file, and how often they are sent
    parser.add_argument("-f", "--file", default='file.txt',
                        help="file to send")
    parser.add_argument("-p", "--port", type=int, default=1234,
                        help="netcat port")

    # partial runs, dry runs
    parser.add_argument("-n", "--dry-run", action='store_true',
                        default=False, help="Show experiment context and exit - do nothing")
    args = parser.parse_args()

    # get credentials
    gwhost, gwuser, key = credentials()

    file = args.file
    port = args.port

    # nodes to use
    if not args.receivers or not args.senders:
        parser.print_help()
        exit(1)

    def flatten(grandpa):
        return [x for father in grandpa for x in father if x]
    def select_nodes(parser_args):
        """
        normalize a list of incoming nodenames
        """
        nodenames = []
        for arg in parser_args:
            args = [ arg ]
            args = flatten([ arg.split(' ') for arg in args])
            args = flatten([ arg.split(',') for arg in args])
            args = [ arg.replace('fit', '') for arg in args]
            args = [ int(arg) for arg in args ]
            args = [ "fit{:02d}".format(arg) for arg in args]
            nodenames += args
        return nodenames

    receivernames = select_nodes(args.receivers)
    sendernames = select_nodes(args.senders)

    if args.dry_run:
        print(10*'-', "Using gateway {gwhost} with account {gwuser} and key {key}"
              .format(**locals()))
    for sendername in sendernames:
        for receivername in receivernames:
            ########## dry run : just display context
            if args.dry_run:
                print(4*'-', "{sendername} -> {receivername}, "
                      "Sending {file} file, through nc {port} port"
                      .format(**locals()))
            else:

                one_run(gwhost, gwuser, key, sendername, receivername,
                        file, port, args.storage_dir)


if __name__ == '__main__':
    main()
