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
on a single host (either server or client)

So e.g.
angle-measure.sh init-server 64 20MHz 
would setup the server-side wireless system to use channel 64 and 20MHz bands

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
    
def server_client(production):
    "returns a tuple (server, client)"
    if production:
        return "fit30", "fit31"
    else:
        return "fit04", "fit41"

# using external shell script like e.g.:
# angle-measure.sh init-server channel bandwidth

def show_app_trace(app, message):
    print ("--- STDOUT : setup stdout for {}:".format(message),
           ec.trace(app, "stdout"))
    print ("--- STDERR : setup stderr for {}:".format(message),
           ec.trace(app, "stderr"))


def main():
    parser = ArgumentParser()
    parser.add_argument("-p", "--production", dest='production', action='store_true',
                        default=False, help="Run in preplab")
    # tmp
    parser.add_argument("-s", "--server", default=None)
    parser.add_argument("-c", "--client", default=None)
    
    parser.add_argument("-v", "--verbose", dest='verbose', action='store_true',
                        default=False, help="Show selected nodes and exit")
    args = parser.parse_args()

    gwhost, gwuser, key = credentials(args.production)
    # get defaults for preplab or production
    servername, clientname = server_client(args.production)
    # but can always be overridden
    if args.server is not None:  servername = args.server
    if args.client is not None:  clientname = args.client

    if args.verbose:
        print("Using gateway {gwhost} with account {gwuser}\n"
              "Using server = {servername}, "\
              "Using client = {clientname}, "\
              .format(**locals()))
        exit(0)

    # the server node
    server = ec.register_resource(
        "linux::Node",
        username = 'root',
        hostname = servername,
        gateway = gwhost,
        gatewayUser = gwuser,
        identity = key,
        cleanExperiment = True,
        cleanProcesses = True,
        autoDeploy = True)

    # the client node
    client = ec.register_resource(
        "linux::Node",
        username = 'root',
        hostname = clientname,
        gateway = gwhost,
        gatewayUser = gwuser,
        identity = key,
        cleanExperiment = True,
        cleanProcesses = True,
        autoDeploy = True)

    # an app to init the server
    init_server = ec.register_resource(
        "linux::Application",
        code = "angle-measure.sh",
        command = "${CODE} init-server 64 HT20",
        autoDeploy = True,
        connectedTo = server)

    # an app to init the server
    init_client = ec.register_resource(
        "linux::Application",
        code = "angle-measure.sh",
        command = "${CODE} init-client 64 HT20",
        autoDeploy = True,
        connectedTo = client)

    ec.wait_finished( [init_server, init_client] )

    show_app_trace(init_server, "server init on {}".format(servername))
    show_app_trace(init_client, "client init on {}".format(clientname))

    ec.shutdown()

if __name__ == '__main__':
    main()
