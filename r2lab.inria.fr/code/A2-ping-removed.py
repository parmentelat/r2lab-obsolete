









host_gateway  = 'faraday.inria.fr'
user_gateway  = '[your_onelab_user]'
user_identity = '~/.ssh/[your_public_ssh_key]'


host01 = 'fit01'
user01 = 'root'


ec = ExperimentController(exp_id="A2-ping")


gateway = ec.register_resource("linux::Node",
                                username = user_gateway,
                                hostname = hoast_gateway,
                                identity = user_identity,
                                cleanExperiment = True,
                                cleanProcesses = True)

ec.deploy(gateway)


fit01   = ec.register_resource("linux::Node",
                                username = user01,
                                hostname = host01,
                                # to reach the fit01 node it must go through the gateway, so let's assign the gateway infos
                                gateway = host_gateway,
                                gatewayUser = user_gateway,
                                identity = user_identity,
                                cleanExperiment = True,
                                cleanProcesses = True)

ec.deploy(fit01)



cmd = 'ping -c1 192.168.03.01'















