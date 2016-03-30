
#!/usr/bin/env python3

# including nepi library and other required packages
from __future__ import print_function
from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState
from nepi.util.sshfuncs import logger
import os

# setting up the default host, onelab user and shh key credential
gateway_hostname  = 'faraday.inria.fr'
gateway_username  = 'root'#'onelab.inria.mario.tutorial'
gateway_key       = '~/.ssh/id_rsa'#'~/.ssh/onelab.private'

# setting up the credentials for the nodes
host11 = 'fit11'
host23 = 'fit23'
user11 = 'root'
user23 = 'root'

# distro version for OAI
version_host11 = 'oai-enb.ndz'
version_host23 = 'oai-ue.ndz'

# creating a new ExperimentController (EC) to manage the experiment
ec = ExperimentController(exp_id="D1-OAI")

# creating the gateway node
gateway = ec.register_resource("linux::Node",
                                username = gateway_username,
                                hostname = gateway_hostname,
                                identity = gateway_key,
                                cleanExperiment = True,
                                cleanProcesses = True,
                                autoDeploy = True)
# ec.deploy(gateway)

# application to load at fit11 and fit23 the fresh distro for OAI
# cmd   = 'rhubarbe-load -i {} -t 2000 {}; '.format(version_host11, host11)
# cmd  += 'rhubarbe-load -i {} -t 2000 {}; '.format(version_host23, host23)
# app_gateway = ec.register_resource("linux::Application",
                                    # command = cmd,
                                    # connectedTo = gateway)
# ec.deploy(app_gateway)

#wait application finish
# ec.wait_finished(app_gateway)

# creating the fit11 node
fit11   = ec.register_resource("linux::Node",
                                username = user11,
                                hostname = host11,
                                gateway = gateway_hostname,
                                gatewayUser = gateway_username,
                                identity = gateway_key,
                                cleanExperiment = True,
                                cleanProcesses = True,
                                autoDeploy = True)
# ec.deploy(fit11)

# creating the fit23 node
fit23   = ec.register_resource("linux::Node",
                                username = user23,
                                hostname = host23,
                                gateway = gateway_hostname,
                                gatewayUser = gateway_username,
                                identity = gateway_key,
                                cleanExperiment = True,
                                cleanProcesses = True,
                                autoDeploy = True)
# ec.deploy(fit23)

# fit11 will check for the current version
cmd  = "cd /root/openairinterface5g/; "
cmd += "chmod +x ./targets/bin/init_nas_nos1; "
cmd += "sudo ifconfig oai0 10.0.1.1 netmask 255.255.255.0 broadcast 10.0.1.255; "
cmd += "$OPENAIR_DIR/targets/bin/rb_tool -a -c0 -i0 -z0 -s 10.0.1.1 -t 10.0.1.9 -r 1; "
cmd += "cd $OPENAIR_HOME; $OPENAIR_HOME/targets/bin/lte-softmodem-nos1.Rel10 -O $OPENAIR_HOME/targets/PROJECTS/GENERIC-LTE-EPC/CONF/enb.band7.tm1.usrpb210.conf -S 2>&1 | tee eNB.log"
app_fit11 = ec.register_resource("linux::Application",
                                  command = cmd,
                                  connectedTo = fit11)

# fit23 will check for the current version
cmd = "cat /etc/*-release | uniq -u | awk /PRETTY_NAME=/ | awk -F= '{print $2}'"
app_fit23 = ec.register_resource("linux::Application",
                                  command = cmd,
                                  connectedTo = fit23)


# deploy the applications
ec.deploy([app_fit11, app_fit23])
# wait application to recovery the results
ec.wait_finished([app_fit11, app_fit23])

# recovering the results
print ("\n--- INFO: listing fit11 distro:")
print (ec.trace(app_fit11, "stdout"))
print ("\n--- INFO: listing fit23 distro:")
print (ec.trace(app_fit23, "stdout"))

# shutting down the experiment
ec.shutdown()
