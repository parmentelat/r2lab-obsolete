title: NEPI - File Exchange
tab: tutorial
---
<script type="text/javascript">loadMenu();</script>

Below are a couple of experiments as a second level of learning [NEPI](http://nepi.inria.fr/Install/WebHome) network tool and R2lab simulation testbed.

The experiments were made with an increment level from **B1** to **B2** to allow better subject understanding. Feel free to skip to the level that fits your knowledge.

From one experiment to other, like git style, we highlight the modifications, insert and delete actions by different colors to improve the user experience learning. In most of the experiments cases a picture explaining the scenario are presented to help the experiment comprehension.

Note that in these examples, differently from the previous experiments (A1-A4), we introduced two skills of NEPI. 

You will use **dependent** and **condition** NEPI instructions. Respectively lines **80/87** and **98/101/104/107**, highlighted in the code at **B1** experiment.

The dependent condition will install for us NC (netcat) tool prerequisites and the condition instruction will ensure that the **fit01** node will send the file only after **fit02** is done and listening on it.

<br>

<ul id="myTabs" class="nav nav-tabs" role="tablist">
  <li role="presentation" class="active">
    <a href="#B1" id="B1-tab" role="tab" data-toggle="tab" aria-controls="B1" aria-expanded="true">B1</a>
  </li>
  <li role="presentation" class="">
    <a href="#B2" role="tab" id="B2-tab" data-toggle="tab" aria-controls="B2" aria-expanded="false">B2</a>
  </li>
</ul>

<div id="contents" class="tab-content">

<div role="tabpanel" class="tab-pane fade active in" id="B1" aria-labelledby="home-tab">
  <br/>
  The experiment below uses four nodes. From your computer you will create and deploy **local**, **gateway**, **fit01** and **fit02** nodes. 
  <br><br>
  From **local** you will copy "file.txt" to R2lab **gateway** node, which in turn will copy the same file to **fit02** node. Both copy file will use "scp command".
  <br><br>
  Once the file is present in **fit02** node, you will start NC (netcat) at **fit01** to listen in port 1234. After **fit01** starts listening in 1234 port, **fit02** node will transmit the file also using NC. The transmission from **fit02** to **fit01** use the wired **control interface**.

  <center>
    ![a1](assets/img/B1.png)<br>
    Download the <a href="codes_examples/B1-send-file.py" download target="_blank">B1 experiment</a> code
  </center>
  

  <pre data-src="prism.js"  data-line="81,88,99,102,105,108" class="line-numbers"><code class="language-python">
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
gateway_dir   = '/home/[your_onelab_user]/'

# setting up the credentials for the nodes 
host01 = 'fit01'
user01 = 'root'
host01_dir = '/home/'

host02 = 'fit02'
user02 = 'root'
host02_dir = '/home/'
port   = 1234

local_file = '[some_file.txt]'
local_dir  = '[some_file_path]'

# creating a new ExperimentController (EC) to manage the experiment
ec = ExperimentController(exp_id="B1-send-file")

# creating local
local   = ec.register_resource("linux::Node",
                              hostname = localhost,
                              cleanExperiment = True,
                              cleanProcesses = True)

# creating the gateway node
gateway = ec.register_resource("linux::Node",
                              username = user_gateway,
                              hostname = host_gateway,
                              identity = user_identity,
                              cleanExperiment = True,
                              cleanProcesses = True)

# creating the fit01 node
fit01   = ec.register_resource("linux::Node",
                              username = user01,
                              hostname = host01,
                              gateway = host_gateway,
                              gatewayUser = user_gateway,
                              identity = user_identity,
                              cleanExperiment = True,
                              cleanProcesses = True)

# creating the fit02 node 
fit02   = ec.register_resource("linux::Node",
                              username = user02,
                              hostname = host02,
                              gateway = host_gateway,
                              gatewayUser = user_gateway,
                              identity = user_identity,
                              cleanExperiment = True,
                              cleanProcesses = True)

# application to copy file from local to gateway
app_local = ec.register_resource("linux::Application")
cmd  = 'scp {}{} {}@{}:{}{}; '.format(local_dir, local_file, user_gateway, host_gateway, gateway_dir, local_file)
ec.set(app_local, "command", cmd)
ec.register_connection(app_local, local)

# application to copy file to fit02 from gateway
app_gateway = ec.register_resource("linux::Application")
cmd  = 'scp {}{} {}@{}:{}{}; '.format(gateway_dir, local_file, user02, host02, host02_dir, local_file)
ec.set(app_gateway, "command", cmd)
ec.register_connection(app_gateway, gateway)

# fit01 will receive the file from fit02, then we start listening in the port
app_fit01 = ec.register_resource("linux::Application")
cmd = 'nc -dl {} > {}{}'.format(port, host01_dir, local_file)
ec.set(app_fit01, "depends", "netcat")
ec.set(app_fit01, "command", cmd)
ec.register_connection(app_fit01, fit01)

# fit02 will send the file to fit01 
app_fit02 = ec.register_resource("linux::Application")
cmd = 'nc {} {} < {}{}'.format(host01, port, host02_dir, local_file)
ec.set(app_fit02, "depends", "netcat")
ec.set(app_fit02, "command", cmd)
ec.register_connection(app_fit02, fit02)

# fit02 will list the dir after all process 
app_fit02_ls = ec.register_resource("linux::Application")
cmd = 'ls -la {}'.format(host02_dir)
ec.set(app_fit02_ls, "command", cmd)
ec.register_connection(app_fit02_ls, fit02)

# defining that the node gateway can copy the file to fit02 only after the file is copied to it from local
ec.register_condition(app_gateway, ResourceAction.START, app_local, ResourceState.STOPPED) 

# defining that the node ftt02 can send the file to fit01 only after the file is copied to it from gateway
ec.register_condition(app_fit02, ResourceAction.START, app_gateway, ResourceState.STOPPED) 

# defining that the node fit02 can send only after node fit01 is listening
ec.register_condition(app_fit02, ResourceAction.START, app_fit01, ResourceState.STARTED)

# defining that the node fit02 can send only after node fit01 is listening
ec.register_condition(app_fit02_ls, ResourceAction.START, app_fit02, ResourceState.STOPPED) 

# deploy all applications
ec.deploy([local, gateway, fit01, fit02, app_local, app_gateway, app_fit01, app_fit02, app_fit02_ls])

#wait ls application to recovery the results and present after
ec.wait_finished(app_fit02_ls)

# recovering the results
print ("\n--- INFO: listing directory on fit02:")
print (ec.trace(app_fit02_ls, "stdout"))

# shutting down the experiment
ec.shutdown()
  </code></pre>
  </div>
  <div role="tabpanel" class="tab-pane fade" id="B2" aria-labelledby="profile-tab">
    <br/>
    The experiment below are the same as the previous (B1), however here, to send the file from **fit02** to **fit01**, you will use the wireless interface instead the wired one.
    
    <center>
      ![a1](assets/img/B2.png)<br>
      Download the <a href="codes_examples/B2-send-file.py" download target="_blank">B2 experiment</a> code
    </center>
 
  
<pre data-src="prism.js" data-line-edit-line="39,126,150" data-line-edit-line="" data-line-inlcude-line="26-36,75-103" class="line-numbers"><code class="language-python">
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
gateway_dir   = '/home/[your_onelab_user]/'

# setting up the credentials for the nodes 
host01 = 'fit01'
user01 = 'root'
host01_dir = '/home/'

host02 = 'fit02'
user02 = 'root'
host02_dir = '/home/'
port   = 1234

local_file = '[some_file.txt]'
local_dir  = '[some_file_path]'

wifi_interface = 'wlan2' 
wifi_channel   = '4'
wifi_name      = 'ad-hoc'
wifi_key       = '1234567890'

wifi_net_mask  = '/24'
wifi_ip_fit01  = '172.16.1.1'
wifi_ip_fit02  = '172.16.1.2'

# creating a new ExperimentController (EC) to manage the experiment
ec = ExperimentController(exp_id="B2-send-file")

# creating local
local   = ec.register_resource("linux::Node",
                              hostname = localhost,
                              cleanExperiment = True,
                              cleanProcesses = True)

# creating the gateway node
gateway = ec.register_resource("linux::Node",
                              username = user_gateway,
                              hostname = host_gateway,
                              identity = user_identity,
                              cleanExperiment = True,
                              cleanProcesses = True)

# creating the fit01 node
fit01   = ec.register_resource("linux::Node",
                              username = user01,
                              hostname = host01,
                              gateway = host_gateway,
                              gatewayUser = user_gateway,
                              identity = user_identity,
                              cleanExperiment = True,
                              cleanProcesses = True)

# creating the fit02 node 
fit02   = ec.register_resource("linux::Node",
                              username = user02,
                              hostname = host02,
                              gateway = host_gateway,
                              gatewayUser = user_gateway,
                              identity = user_identity,
                              cleanExperiment = True,
                              cleanProcesses = True)

# application to setup data interface on fit01 node
app_adhoc_fit01 = ec.register_resource("linux::Application")
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
ec.set(app_adhoc_fit01, "command", cmd)
ec.register_connection(app_adhoc_fit01, fit01)

# application to setup data interface on fit02 node
app_adhoc_fit02 = ec.register_resource("linux::Application")
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
ec.set(app_adhoc_fit02, "command", cmd)
ec.register_connection(app_adhoc_fit02, fit02)

# application to copy file from local to gateway
app_local = ec.register_resource("linux::Application")
cmd  = 'scp {}{} {}@{}:{}{}; '.format(local_dir, local_file, user_gateway, host_gateway, gateway_dir, local_file)
ec.set(app_local, "command", cmd)
ec.register_connection(app_local, local)

# application to copy file to fit02 from gateway
app_gateway = ec.register_resource("linux::Application")
cmd  = 'scp {}{} {}@{}:{}{}; '.format(gateway_dir, local_file, user02, host02, host02_dir, local_file)
ec.set(app_gateway, "command", cmd)
ec.register_connection(app_gateway, gateway)

# fit01 will receive the file from fit02, then we start listening in the port
app_fit01 = ec.register_resource("linux::Application")
cmd = 'nc -dl {} > {}{}'.format(port, host01_dir, local_file)
ec.set(app_fit01, "depends", "netcat")
ec.set(app_fit01, "command", cmd)
ec.register_connection(app_fit01, fit01)

# fit02 will send the file to fit01 
app_fit02 = ec.register_resource("linux::Application")
cmd = 'nc {} {} < {}{}'.format(wifi_ip_fit01, port, host02_dir, local_file)
ec.set(app_fit02, "depends", "netcat")
ec.set(app_fit02, "command", cmd)
ec.register_connection(app_fit02, fit02)

# fit02 will list the dir after all process 
app_fit02_ls = ec.register_resource("linux::Application")
cmd = 'ls -la {}'.format(host02_dir)
ec.set(app_fit02_ls, "command", cmd)
ec.register_connection(app_fit02_ls, fit02)

# defining that the node gateway can copy the file to fit02 only after the file is copied to it from local
ec.register_condition(app_gateway, ResourceAction.START, app_local, ResourceState.STOPPED) 

# defining that the node ftt02 can send the file to fit01 only after the file is copied to it from gateway
ec.register_condition(app_fit02, ResourceAction.START, app_gateway, ResourceState.STOPPED) 

# defining that the node fit02 can send only after node fit01 is listening
ec.register_condition(app_fit02, ResourceAction.START, app_fit01, ResourceState.STARTED)

# defining that the node fit02 can send only after node fit01 is listening
ec.register_condition(app_fit02_ls, ResourceAction.START, app_fit02, ResourceState.STOPPED) 

# deploy all applications
ec.deploy([local, gateway, fit01, fit02, app_local, app_gateway, app_adhoc_fit01, app_fit01, app_adhoc_fit02, app_fit02, app_fit02_ls])

#wait ls application to recovery the results and present after
ec.wait_finished(app_fit02_ls)

# recovering the results
print ("\n--- INFO: listing directory on fit02:")
print (ec.trace(app_fit02_ls, "stdout"))

# shutting down the experiment
ec.shutdown()
  </code></pre>
  </div>

</div>

