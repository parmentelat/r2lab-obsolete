title: NEPI - Load Images
tab: tutorial
---
<script type="text/javascript">loadMenu();</script>

Below we present an experiment which will conduct a load image usgin [NEPI](http://nepi.inria.fr/Install/WebHome) network tool at R2lab simulation testbed. 

You will be able load and control the most common Linux distros at R2lab testbed as root user. We provide the most recent Ubuntus and Fedoras for all users.

<br>

<ul id="myTabs" class="nav nav-tabs" role="tablist">
  <li role="presentation" class="active">
    <a href="#C1" id="C1-tab" role="tab" data-toggle="tab" aria-controls="C1" aria-expanded="true">C1</a>
  </li>
</ul>

<div id="contents" class="tab-content">

<div role="tabpanel" class="tab-pane fade active in" id="C1" aria-labelledby="home-tab">
  <br/>
  From your computer you will create and deploy <strong>gateway</strong> and <strong>fit01</strong> nodes. Once in R2lab <strong>gateway</strong> node you launch the code to load a fresh distro at <strong>fit01</strong> node. 
  <br><br>
  At the end, you will create also an application at the <strong>fit01</strong> node to check if the version corresponds as expected.

  <center>
    <img src="/assets/img/C1.png" alt="c1"><br>
    Download the <a href="/codes_examples/C1-load.py" download target="_blank">C1 experiment</a> code
  </center>
  

  <pre data-src="prism.js"  data-line="" class="line-numbers"><code class="language-python">
#!/usr/bin/env python

# including nepi library and other required packages
from &#95;&#95;future&#95;&#95; import print_function
from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState
from nepi.util.sshfuncs import logger
import os

# setting up the default host, onelab user and shh key credential
host_gateway  = 'faraday.inria.fr'
user_gateway  = '[your_onelab_user]'
user_identity = '~/.ssh/[your_public_ssh_key]'

# setting up the credentials for the nodes 
host01 = 'fit01'
user01 = 'root'

# distro version. Could be: 'ubuntu-14.10.ndz' or 'ubuntu-15.04.ndz' or 'fedora-21.ndz' or 'fedora-22.ndz'
version = 'fedora-21.ndz'

# creating a new ExperimentController (EC) to manage the experiment
ec = ExperimentController()

# creating the gateway node
gateway = ec.register_resource("linux::Node",
                                username = user_gateway,
                                hostname = host_gateway,
                                identity = user_identity,
                                cleanExperiment = True,
                                cleanProcesses = True)
ec.deploy(gateway)

# application to copy load at fit01 a fresh distro
app_gateway = ec.register_resource("linux::Application")
cmd  = 'omf6 load -t {} -i {};'.format(host01, version)
ec.set(app_gateway, "command", cmd)
ec.register_connection(app_gateway, gateway)
ec.deploy(app_gateway)

#wait application finish
ec.wait_finished(app_gateway)

# creating the fit01 node
fit01   = ec.register_resource("linux::Node",
                                username = user01,
                                hostname = host01,
                                gateway = host_gateway,
                                gatewayUser = user_gateway,
                                identity = user_identity,
                                cleanExperiment = True,
                                cleanProcesses = True)
ec.deploy(fit01)

# fit01 will check for the current version
app_fit01 = ec.register_resource("linux::Application")
cmd = "cat /etc/*-release | uniq -u | awk /PRETTY_NAME=/ | awk -F= '{print $2}'"
ec.set(app_fit01, "command", cmd)
ec.register_connection(app_fit01, fit01)
ec.deploy(app_fit01)

#wait application to recovery the results 
ec.wait_finished(app_fit01)

# recovering the results
print ("\n--- INFO: listing fit01 distro:")
print (ec.trace(app_fit01, "stdout"))

# shutting down the experiment
ec.shutdown()
  </code></pre>
  </div>
</div>

