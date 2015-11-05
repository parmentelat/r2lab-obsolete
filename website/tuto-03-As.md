title: NEPI - Pings
tab: tutorial
---
<script type="text/javascript">loadMenu();</script>

Below are a couple of experiments to get start with [NEPI](http://nepi.inria.fr/Install/WebHome) network tool and R2lab simulation testbed.

The experiments were made with an increment level from **A1** to **A4** to allow better subject understanding. Feel free to skip to the level that fits your knowledge.

From one experiment to other, like git style, we highlight the modifications, insert and delete actions by different colors to improve the user experience learning. In most of the experiments cases a picture explaining the scenario are presented to help the experiment comprehension.

<br>

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

<div role="tabpanel" class="tab-pane fade active in" id="A1" aria-labelledby="home-tab">
  <br/>
  The experiment below uses only one node. From your computer, you will create and connect the **gateway** (faraday.inria.fr) node. From the **gateway** node you will ping **google server** and recovery the answer of it.

  <center>
    ![a1](assets/img/A1.png)<br>
    Download the <a href="codes_examples/A1-ping.py" download target="_blank">A1 experiment</a> code
  </center>
  

  <pre data-src="prism.js" class="line-numbers"><code class="language-python">
#!/usr/bin/env python

# including nepi library and other required packages
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
# in this case we are creating the gateway node
# we are setting up the host, user and ssh key. 
node = ec.register_resource("linux::Node")
ec.set(node, "username", user)
ec.set(node, "hostname", host)
ec.set(node, "identity", key)
ec.set(node, "cleanExperiment", True)
ec.set(node, "cleanProcesses", True)
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
print "\n--- INFO: output:"
print ec.trace(app, "stdout")

# shutting down the experiment
ec.shutdown()
  </code></pre>
  </div>
  <div role="tabpanel" class="tab-pane fade" id="A2" aria-labelledby="profile-tab">
    <br/>
    The experiment below uses two nodes. From your computer, you will create the **gateway** (faraday.inria.fr) node and the **fit01** node. Once connected in the **gateway** node , you will ping **fit01** node at the **control interface** and recovery the answer of it.
    
    <center>
      ![a1](assets/img/A2.png)<br>
      Download the <a href="codes_examples/A2-ping.py" download target="_blank">A2 experiment</a> code
    </center>
 
  <pre data-src="prism.js" data-line-edit-line="9-12,19,21-29,46,50" data-line-inlcude-line="14-16,31-42" class="line-numbers"><code class="language-python">
#!/usr/bin/env python

# including nepi library and other required packages
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
gateway = ec.register_resource("linux::Node")
ec.set(gateway, "username", user_gateway)
ec.set(gateway, "hostname", host_gateway)
ec.set(gateway, "identity", user_identity)
ec.set(gateway, "cleanExperiment", True)
ec.set(gateway, "cleanProcesses", True)
# deploying the gateway node
ec.deploy(gateway)

# creating the fit01 node
fit01 = ec.register_resource("linux::Node")
ec.set(fit01, "username", user01)
ec.set(fit01, "hostname", host01)
# to reach the fit01 node it must go through the gateway, so let's assign the gateway infos
ec.set(fit01, "gateway", host_gateway)
ec.set(fit01, "gatewayUser", user_gateway)
ec.set(fit01, "identity", user_identity)
ec.set(fit01, "cleanExperiment", True)
ec.set(fit01, "cleanProcesses", True)
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
print "\n--- INFO: output:"
print ec.trace(app, "stdout")

# shutting down the experiment
ec.shutdown()
  </code></pre>
  </div>
  <div role="tabpanel" class="tab-pane fade" id="A3" aria-labelledby="profile-tab">
    <br/>
    The experiment below uses two nodes. From your computer you will create the **fit01** and the **fit02** nodes. Once connected at **fit01**, trough the gateway node, you will configure at both nodes the wired **experiment interface** (data) using DHCP. Once configured the interface, you will ping the **experiment interface** at **fit02** from **fit01**.
    
    <center>
      ![a1](assets/img/A3.png)<br>
      Download the <a href="codes_examples/A3-ping.py" download target="_blank">A3 experiment</a> code
    </center>
 
  <pre data-src="prism.js" data-line-remove-line="24-32"  data-line-edit-line="22,76-82,86" data-line-inlcude-line="18,19,47-58,60-66,68-74" class="line-numbers"><code class="language-python">
#!/usr/bin/env python

# including nepi library and other required packages
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

# # creating the gateway node
# gateway = ec.register_resource("linux::Node")
# ec.set(gateway, "username", user_gateway)
# ec.set(gateway, "hostname", host_gateway)
# ec.set(gateway, "identity", user_identity)
# ec.set(gateway, "cleanExperiment", True)
# ec.set(gateway, "cleanProcesses", True)
# # deploying the gateway node
# ec.deploy(gateway)

# creating the fit01 node
fit01 = ec.register_resource("linux::Node")
ec.set(fit01, "username", user01)
ec.set(fit01, "hostname", host01)
# to reach the fit01 node it must go through the gateway, so let's assign the gateway infos
ec.set(fit01, "gateway", host_gateway)
ec.set(fit01, "gatewayUser", user_gateway)
ec.set(fit01, "identity", user_identity)
ec.set(fit01, "cleanExperiment", True)
ec.set(fit01, "cleanProcesses", True)
# deploying the fit01 node
ec.deploy(fit01)

# creating the fit02 node 
fit02 = ec.register_resource("linux::Node")
ec.set(fit02, "username", user02)
ec.set(fit02, "hostname", host02)
# to reach the fit02 node it must go through the gateway, so let's assign the gateway infos
ec.set(fit02, "gateway", host_gateway)
ec.set(fit02, "gatewayUser", user_gateway)
ec.set(fit02, "identity", user_identity)
ec.set(fit02, "cleanExperiment", True)
ec.set(fit02, "cleanProcesses", True)
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
print "\n--- INFO: output:"
print ec.trace(app_ping_from_fit01_to_fit02, "stdout")

# shutting down the experiment
ec.shutdown()
  </code></pre>
  </div>
  <div role="tabpanel" class="tab-pane fade" id="A4" aria-labelledby="profile-tab">
    <br/>
    The experiment below uses two nodes and update the previous experiment A3. From your computer you will create the same **fit01** and the **fit02** nodes. Once connected at **fit01**, trough the gateway node, you will configure an AD-HOC network in both nodes ** wireless interface ** (wlan0). Once configured the interface, you will ping **fit01** and **fit02** each other using the **wireless interface**.
    
    <center>
      ![a1](assets/img/A4.png)<br>
      Download the <a href="codes_examples/A4-ping.py" download target="_blank">A4 experiment</a> code
    </center>
 
  <pre data-src="prism.js" data-line-remove-line="61,78" data-line-edit-line="31,93,95,109,110" data-line-inlcude-line="21-28,62-70,79-87,101-107,113-115" class="line-numbers"><code class="language-python">
#!/usr/bin/env python

# including nepi library and other required packages
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
fit01 = ec.register_resource("linux::Node")
ec.set(fit01, "username", user01)
ec.set(fit01, "hostname", host01)
# to reach the fit01 node it must go through the gateway, so let's assign the gateway infos
ec.set(fit01, "gateway", host_gateway)
ec.set(fit01, "gatewayUser", user_gateway)
ec.set(fit01, "identity", user_identity)
ec.set(fit01, "cleanExperiment", True)
ec.set(fit01, "cleanProcesses", True)
# deploying the fit01 node
ec.deploy(fit01)

# creating the fit02 node 
fit02 = ec.register_resource("linux::Node")
ec.set(fit02, "username", user02)
ec.set(fit02, "hostname", host02)
# to reach the fit02 node it must go through the gateway, so let's assign the gateway infos
ec.set(fit02, "gateway", host_gateway)
ec.set(fit02, "gatewayUser", user_gateway)
ec.set(fit02, "identity", user_identity)
ec.set(fit02, "cleanExperiment", True)
ec.set(fit02, "cleanProcesses", True)
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
print "\n--- INFO: output fit01:"
print ec.trace(app_ping_from_fit01_to_fit02, "stdout")

# recovering the results fit02
print "\n--- INFO: output fit02:"
print ec.trace(app_ping_from_fit02_to_fit01, "stdout")

# shutting down the experiment
ec.shutdown()
  </code></pre>
  </div>
</div>

