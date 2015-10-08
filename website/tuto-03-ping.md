title: NEPI - Ping
tab: tutorial
---

Below is a very simple experiment sends 3 pings to r2lab.inria.fr server from one linux::Node.
The expected result is prints the output of the ping command.

<pre><code class="language-python">

#!/usr/bin/env python
#
#
#    NEPI, a framework to manage network experiments
#    Copyright (C) 2015 INRIA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as
#    published by the Free Software Foundation;
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Alina Quereilhac <alina.quereilhac@inria.fr>
#         Maksym Gabielkov <maksym.gabielkovc@inria.fr>
#
#
# This is a script used to simulate a sender-receiver file between two nodes A and B from
# INRIA testbed (R2Lab) before running a OMF experiment using Nitos nodes.
# For simplicity, the file should be already present in the node A (sender) and it call file1.txt
#
# Example of how to run this experiment (replace with your information):
#
# python ping.py -a <hostname> -u <username> -i ~/.ssh/id_rsa
#
#
from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState
import os
from nepi.util.sshfuncs import logger
import logging
from argparse import ArgumentParser

usage = ("usage: %prog -a <hostname> -u <username> -i <ssh-key>")

parser = ArgumentParser(usage = usage)
parser.add_argument("-a", "--hostname", dest="hostname", 
			 help="Remote host")
parser.add_argument("-u", "--username", dest="username", 
       help="SSH username to connect the host", default="username" )
parser.add_argument("-i", "--ssh-key", dest="ssh_key", 
       help="Path to private SSH key to be used for connection")

args = parser.parse_args()

# receive the arguments from command line
hostname    = args.hostname
username    = args.username
identity    = args.ssh_key

# create the experiment controller
ec = ExperimentController(exp_id="simple-ping")

# create a conexion to a linux node
node = ec.register_resource("linux::Node")
ec.set(node, "username", username)
ec.set(node, "hostname", hostname)
ec.set(node, "identity", identity)
ec.set(node, "cleanExperiment", True)
ec.set(node, "cleanProcesses", True)

# command to be executed
command = "ping -c3 r2lab.inria.fr"

# create the application
application = ec.register_resource("linux::Application")
ec.set(application, "command", command)

#connect the application to the node
ec.register_connection(application, node)

# deploy the code
ec.deploy()

# wait for the application exit
ec.wait_finished(application)

# recover the result
print ec.trace(application, "stdout")

# destroy the controller
ec.shutdown()

</code></pre>

