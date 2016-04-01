
#!/usr/bin/env python3

# including nepi library and other required packages
from __future__ import print_function
from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState
from nepi.util.sshfuncs import logger
import os
import time

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

# application to load at fit11 and fit23 the fresh distro for OAI
cmd   = 'rhubarbe-load -i {} -t 2000 {}; '.format(version_host11, host11)
cmd  += 'rhubarbe-load -i {} -t 2000 {}; '.format(version_host23, host23)
app_gateway = ec.register_resource("linux::Application",
                                    command = cmd,
                                    connectedTo = gateway)
ec.deploy(app_gateway)
# wait application finish
ec.wait_finished(app_gateway)

print ("Nodes loaded... Waiting to start (30 sec.)...")
time.sleep(35)

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

# fit11 will check for the current version
cmd  = "export OPENAIR_HOME=/root/openairinterface5g; "
cmd += "export OPENAIR_DIR=/root/openairinterface5g; " #The OPENAIR_DIR is used inside of "init_nas_nos1" file.
cmd += "cd $OPENAIR_HOME; "
cmd += "chmod +x ./targets/bin/init_nas_nos1; "
cmd += "./targets/bin/init_nas_nos1 eNB; "
cmd += "cd $OPENAIR_HOME; $OPENAIR_HOME/targets/bin/lte-softmodem-nos1.Rel10 -O $OPENAIR_HOME/targets/PROJECTS/GENERIC-LTE-EPC/CONF/enb.band7.tm1.usrpb210.conf -S 2>&1 | tee eNB.log "
app_fit11 = ec.register_resource("linux::Application",
                                  command = cmd,
                                  connectedTo = fit11)

# fit23 will check for the current version
cmd  = "export OPENAIR_HOME=/root/openairinterface5g; "
cmd += "export OPENAIR_DIR=/root/openairinterface5g; " #The OPENAIR_DIR is used inside of "init_nas_nos1" file.
cmd += "cd $OPENAIR_HOME; "
cmd += "chmod +x ./targets/bin/init_nas_nos1; "
cmd += "./targets/bin/init_nas_nos1 UE; "
cmd += "cd $OPENAIR_HOME; $OPENAIR_HOME/targets/bin/lte-softmodem-nos1.Rel10 -U -C2680000000 -r25 --ue-scan-carrier --ue-txgain 85 2>&1 | tee UE.log"
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
