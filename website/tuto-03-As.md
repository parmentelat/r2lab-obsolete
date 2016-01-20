title: NEPI - Pings
tab: tutorial
---
<script type="text/javascript">loadMenu();</script>

Below are a couple of experiments to get started with
[NEPI](http://nepi.inria.fr/Install/WebHome) experiment orchestration
tool, and with R2lab simulation testbed.

This suite of experiments, labelled **A1** to **A4**, are designed as
a suite of small incremental changes, to allow better subject
understanding. Feel free to skip to the level that fits your
knowledge.

From one experiment to the other, we highlight the required changes in
a git-like style: inserted and deleted lines are shown with a
different color, so readers can see what is new in this tutorial. 

<br/>

<ul id="myTabs" class="nav nav-tabs" role="tablist">
  <li role="presentation" class="active">
    <a href="#A1" id="A1-tab" role="tab" data-toggle="tab" aria-controls="A1" aria-expanded="true">A1</a>
  </li>
  <li role="presentation" class="">
    <a href="#A2" role="tab" id="A2-tab" data-toggle="tab" aria-controls="A2" aria-expanded="false">A2</a>
  </li>
  <li role="presentation" class="">
    <a href="#A3" role="tab" id="A3-tab" data-toggle="tab" aria-controls="A3" aria-expanded="false">A3</a>
  </li>
  <li role="presentation" class="">
    <a href="#A4" role="tab" id="A4-tab" data-toggle="tab" aria-controls="A4" aria-expanded="false">A4</a>
  </li>
</ul>

<div id="contents" class="tab-content">
<!------------ A1 ------------>
<div role="tabpanel" class="tab-pane fade active in" id="A1" aria-labelledby="home-tab">
  <br/>
  In this experiment example, from your computer, you will create and deploy an application to connect to the R2lab
  <strong>gateway</strong> (faraday.inria.fr).
  <br/><br/>
  Once there, from the <strong>gateway</strong>, you will ping a <strong>google server</strong> and recover its answer.
<center>
  <img src="/assets/img/A1.png" alt="a1"> <br/>
  Download the <a href="/codes_examples/A1-ping.py" download target="_blank">A1 experiment</a> code
</center>
<pre data-src="prism.js" class="line-numbers"><code class="language-python">
#!/usr/bin/env python

# including nepi library and other required packages
from &#95;&#95;future&#95;&#95; import print_function
from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState
from nepi.util.sshfuncs import logger
import os

# setting up the default host, onelab user and shh key credential
host  = 'faraday.inria.fr'
user  = '[your_onelab_user]'
key   = '~/.ssh/[your_public_ssh_key]'

# creating a new ExperimentController (EC) to manage the experiment
ec = ExperimentController(exp_id="A1-ping")

# creating a node using the already filled credentials
node = ec.register_resource("linux::Node",
                            username = user,
                            hostname = host,
                            identity = key,
                            cleanExperiment = True,
                            cleanProcesses = True)
# deploying the node
ec.deploy(node)

# creating an application
app = ec.register_resource("linux::Application")
cmd = 'ping -c1 google.fr'
# given to the application a command to execute
ec.set(app, "command", cmd)
# registering the application to be executed in the node
ec.register_connection(app, node)
# deploying the application
ec.deploy(app)
# waiting the app finish its job
ec.wait_finished(app)

# recovering the results
print ("\n--- INFO: output:")
print (ec.trace(app, "stdout"))

# shutting down the experiment
ec.shutdown()
</code></pre>
</div>
<!------------ A2 ------------>
<div role="tabpanel" class="tab-pane fade" id="A2" aria-labelledby="profile-tab">
    <br/>
    In this experiment example, from your computer, you will create and deploy two application nodes. The first one to connect to the R2lab gateway (faraday.inria.fr) and, from there, reach the <strong>fit01</strong> node. 
    <br/><br/>
    Once connected at the R2lab gateway, you will ping the <strong>fit01</strong> node at its <strong>control interface</strong> (available as the <code>control</code> device under linux).
    At the end you will retrieve the answer of the experiment.
<center>
  <img src="/assets/img/A2.png" alt="a2"><br/>
  Download the <a href="/codes_examples/A2-ping.py" download target="_blank">A2 experiment</a> code
</center>
<pre data-src="prism.js" data-line-edit-line="10-13,20,22-30,47,51" data-line-inlcude-line="15-17,32-43" class="line-numbers">
<code class="language-python">
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

# setting up the credentials for one fit01 node 
host01 = 'fit01'
user01 = 'root'

# creating a new ExperimentController (EC) to manage the experiment
ec = ExperimentController(exp_id="A2-ping")

# creating the gateway node
gateway = ec.register_resource("linux::Node",
                                username = user_gateway,
                                hostname = host_gateway,
                                identity = user_identity,
                                cleanExperiment = True,
                                cleanProcesses = True)
# deploying the gateway node
ec.deploy(gateway)

# creating the fit01 node
fit01   = ec.register_resource("linux::Node",
                                username = user01,
                                hostname = host01,
                                # to reach the fit01 node it must go through the gateway, so let's assign the gateway infos
                                gateway = host_gateway,
                                gatewayUser = user_gateway,
                                identity = user_identity,
                                cleanExperiment = True,
                                cleanProcesses = True)
# deploying the fit01 node
ec.deploy(fit01)

# creating an application to ping the control inteface of fit01 node from the gateway
app = ec.register_resource("linux::Application")
cmd = 'ping -c1 192.168.03.01'
# given to the application a command to execute
ec.set(app, "command", cmd)
# registering the application to be executed in the fit01 node
ec.register_connection(app, gateway)
# deploying the application
ec.deploy(app)
# waiting the app finish its job
ec.wait_finished(app)

# recovering the results
print ("\n--- INFO: output:")
print (ec.trace(app, "stdout"))

# shutting down the experiment
ec.shutdown()
</code></pre>
</div>
<!------------ A3 ------------>
  <div role="tabpanel" class="tab-pane fade" id="A3" aria-labelledby="profile-tab">
    <br/>
    The experiment below uses two wireless nodes. From your computer you will create and deploy <strong>fit01</strong> and <strong>fit02</strong> nodes. You will configure in both nodes the wired <strong>experiment interface</strong> (available as <code>data</code> under linux) using DHCP.
    <br/><br/>
    Once configured the interface in both nodes, you will be able to ping the <strong>experiment interface</strong> at </strong>fit02</strong> from <strong>fit01</strong>.
<center>
   <img src="/assets/img/A3.png" alt="a3"><br/>
    Download the <a href="/codes_examples/A3-ping.py" download target="_blank">A3 experiment</a> code
</center>
<pre data-src="prism.js" data-line-remove-line="25-33"  data-line-edit-line="23,77-83,87" data-line-inlcude-line="19,20,48-59,61-67,69-75" class="line-numbers">
<code class="language-python">
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

host02 = 'fit02'
user02 = 'root'

# creating a new ExperimentController (EC) to manage the experiment
ec = ExperimentController(exp_id="A3-ping")

# creating the gateway node
# gateway = ec.register_resource("linux::Node",
#                                 username = user_gateway,
#                                 hostname = host_gateway,
#                                 identity = user_identity,
#                                 cleanExperiment = True,
#                                 cleanProcesses = True)
# deploying the gateway node
# ec.deploy(gateway)

# creating the fit01 node
fit01 = ec.register_resource("linux::Node",
                            username = user01,
                            hostname = host01,
# to reach the fit01 node it must go through the gateway, so let's assign the gateway infos
                            gateway = host_gateway,
                            gatewayUser = user_gateway,
                            identity = user_identity,
                            cleanExperiment = True,
                            cleanProcesses = True)
# deploying the fit01 node
ec.deploy(fit01)

# creating the fit02 node 
fit02 = ec.register_resource("linux::Node",
                            username = user02,
                            hostname = host02,
# to reach the fit02 node it must go through the gateway, so let's assign the gateway infos
                            gateway = host_gateway,
                            gatewayUser = user_gateway,
                            identity = user_identity,
                            cleanExperiment = True,
                            cleanProcesses = True)
# deploying the fit02 node
ec.deploy(fit02)

# application to setup data interface on fit01 node
app_fit01 = ec.register_resource("linux::Application")
cmd = 'sudo ip link set dev data down; sudo dhclient data;'
ec.set(app_fit01, "command", cmd)
ec.register_connection(app_fit01, fit01)
ec.deploy(app_fit01)
ec.wait_finished(app_fit01)

# application to setup data interface on fit02 node
app_fit02 = ec.register_resource("linux::Application")
cmd = 'sudo ip link set dev data down; sudo dhclient data;'
ec.set(app_fit02, "command", cmd)
ec.register_connection(app_fit02, fit02)
ec.deploy(app_fit02)
ec.wait_finished(app_fit02)

# creating an application to ping the experiment inteface of fit02 from the fit01
app_ping_from_fit01_to_fit02 = ec.register_resource("linux::Application")
cmd = 'ping -c1 192.168.02.02; '
ec.set(app_ping_from_fit01_to_fit02, "command", cmd)
ec.register_connection(app_ping_from_fit01_to_fit02, fit01)
ec.deploy(app_ping_from_fit01_to_fit02)
ec.wait_finished(app_ping_from_fit01_to_fit02)

# recovering the results
print ("\n--- INFO: output:")
print (ec.trace(app_ping_from_fit01_to_fit02, "stdout"))

# shutting down the experiment
ec.shutdown()
</code></pre>
</div>


<!------------ A4 ------------>
<div role="tabpanel" class="tab-pane fade" id="A4" aria-labelledby="profile-tab">
  <br/>
    The experiment below uses two nodes and is an incremental change from previous experiment A3.
    From your computer you will create the same fit01 and fit02 nodes.
    This time however, you will configure an <em>ad-hoc</em> network between both nodes <strong>wireless interfaces</strong> (exposed in linux as <code>wlan0</code>).
    <br/><br/>
    Once the interfaces configured, you will ping fit01 and fit02 from one another using the <strong>wireless interface</strong>.
<center>
  <img src="/assets/img/A4.png" alt="a4"><br/>
  Download the <a href="/codes_examples/A4-ping.py" download target="_blank">A4 experiment</a> code
</center>
<pre data-src="prism.js" data-line-remove-line="62,79" data-line-edit-line="32,94,96,110,111" data-line-inlcude-line="22-29,63-71,80-88,102-108,114-116" class="line-numbers">
<code class="language-python">
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

host02 = 'fit02'
user02 = 'root'

wifi_interface = 'wlan0' 
wifi_channel   = '4'
wifi_name      = 'ad-hoc'
wifi_key       = '1234567890'

wifi_net_mask  = '/24'
wifi_ip_fit01  = '172.16.1.1'
wifi_ip_fit02  = '172.16.1.2'

# creating a new ExperimentController (EC) to manage the experiment
ec = ExperimentController(exp_id="A4-ping")

# creating the fit01 node
fit01 = ec.register_resource("linux::Node",
                            username = user01,
                            hostname = host01,
# to reach the fit01 node it must go through the gateway, so let's assign the gateway infos
                            gateway = host_gateway,
                            gatewayUser = user_gateway,
                            identity = user_identity,
                            cleanExperiment = True,
                            cleanProcesses = True)
# deploying the fit01 node
ec.deploy(fit01)

# creating the fit02 node
fit02 = ec.register_resource("linux::Node",
                            username = user02,
                            hostname = host02,
# to reach the fit02 node it must go through the gateway, so let's assign the gateway infos
                            gateway = host_gateway,
                            gatewayUser = user_gateway,
                            identity = user_identity,
                            cleanExperiment = True,
                            cleanProcesses = True)
# deploying the fit02 node
ec.deploy(fit02)

# application to setup data interface on fit01 node
app_fit01 = ec.register_resource("linux::Application")
#cmd = 'sudo ip link set dev data down; sudo dhclient data;'
# configuring the ad-hoc for node fit01
cmd  = "ip addr flush dev {}; ".format(wifi_interface)
cmd += "sudo ip link set {} down; ".format(wifi_interface)
cmd += "sudo iwconfig {} mode ad-hoc; ".format(wifi_interface)
cmd += "sudo iwconfig {} channel {}; ".format(wifi_interface, wifi_channel)
cmd += "sudo iwconfig {} essid '{}'; ".format(wifi_interface, wifi_name)
cmd += "sudo iwconfig {} key {}; ".format(wifi_interface, wifi_key)
cmd += "sudo ip link set {} up; ".format(wifi_interface)
cmd += "sudo ip addr add {}{} dev {}; ".format(wifi_ip_fit01, wifi_net_mask, wifi_interface)
ec.set(app_fit01, "command", cmd)
ec.register_connection(app_fit01, fit01)
ec.deploy(app_fit01)
ec.wait_finished(app_fit01)

# application to setup data interface on fit02 node
app_fit02 = ec.register_resource("linux::Application")
#cmd = 'sudo ip link set dev data down; sudo dhclient data;'
# configuring the ad-hoc for node fit01
cmd  = "ip addr flush dev {}; ".format(wifi_interface)
cmd += "sudo ip link set {} down; ".format(wifi_interface)
cmd += "sudo iwconfig {} mode ad-hoc; ".format(wifi_interface)
cmd += "sudo iwconfig {} channel {}; ".format(wifi_interface, wifi_channel)
cmd += "sudo iwconfig {} essid '{}'; ".format(wifi_interface, wifi_name)
cmd += "sudo iwconfig {} key {}; ".format(wifi_interface, wifi_key)
cmd += "sudo ip link set {} up; ".format(wifi_interface)
cmd += "sudo ip addr add {}{} dev {}; ".format(wifi_ip_fit02, wifi_net_mask, wifi_interface)
ec.set(app_fit02, "command", cmd)
ec.register_connection(app_fit02, fit02)
ec.deploy(app_fit02)
ec.wait_finished(app_fit02)

# ping fit02 inteface from fit01
app_ping_from_fit01_to_fit02 = ec.register_resource("linux::Application")
cmd = 'ping -c5 -I {} {}'.format(wifi_interface, wifi_ip_fit02)
ec.set(app_ping_from_fit01_to_fit02, "command", cmd)
ec.register_connection(app_ping_from_fit01_to_fit02, fit01)
ec.deploy(app_ping_from_fit01_to_fit02)
ec.wait_finished(app_ping_from_fit01_to_fit02)

# ping fit01 inteface from fit02
app_ping_from_fit02_to_fit01 = ec.register_resource("linux::Application")
cmd = 'ping -c5 -I {} {}'.format(wifi_interface, wifi_ip_fit01)
ec.set(app_ping_from_fit02_to_fit01, "command", cmd)
ec.register_connection(app_ping_from_fit02_to_fit01, fit02)
ec.deploy(app_ping_from_fit02_to_fit01)
ec.wait_finished(app_ping_from_fit02_to_fit01)

# recovering the results of fit01
print ("\n--- INFO: output fit01:")
print (ec.trace(app_ping_from_fit01_to_fit02, "stdout"))

# recovering the results fit02
print ("\n--- INFO: output fit02:")
print (ec.trace(app_ping_from_fit02_to_fit01, "stdout"))

# shutting down the experiment
ec.shutdown()
</code></pre>
</div>

</div>

