title: NEPI - Ping
tab: tutorial
---

<script type="text/javascript">loadMenu();</script>

Below is a very simple experiment sends 3 pings to r2lab.inria.fr server from one linux::Node.
The expected result is prints the output of the ping command.

Download the <a href="codes_examples/ping.py" download target="_blank">ping</a> code

<pre data-src="prism.js" class="language-javascript line-numbers"><code class="language-python">#!/usr/bin/env python
# Example of how to run this experiment (replace with your information):
#
# python ping.py -a &lt;hostname&gt; -u &lt;username&gt; -i ~/.ssh/id_rsa
#
from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState
import os
from nepi.util.sshfuncs import logger
import logging
from argparse import ArgumentParser

usage = ("usage: %prog -a &lt;hostname&gt; -u &lt;username&gt; -i &lt;ssh-key&gt;")

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

# deploy the experiment
ec.deploy()

# wait for the experiment exit
ec.wait_finished(application)

# recover and print the result
print ec.trace(application, "stdout")

# destroy the controller
ec.shutdown()
</code>
</pre>
