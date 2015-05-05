# #!/usr/bin/env python
# # -*- coding: utf-8 -*-

# ----------------------------
# HELPER to talk nodes by functions
# Mario ZANCANARO <mario.zancanaro@inria.fr>
# ----------------------------

from nepi.execution.resource import ResourceState, ResourceAction

def create_node(ec, type='linux::Node', **opt):
  gateway         = opt['gwy']
  gw_user         = opt['gus']
  gw_key          = opt['gky']
  node_host       = opt['nd']
  node_user       = opt['nus']

  if 'linux::Node' in type:
    node = ec.register_resource(type)
    ec.set(node, "username", node_user)
    ec.set(node, "hostname", node_host)
    ec.set(node, "identity", gw_key)
    ec.set(node, "gateway", gateway)
    ec.set(node, "gatewayUser", gw_user)
    ec.set(node, "cleanExperiment", True)

    return node

def create_app(ec, node, type='linux::Application', cmd='date'):
  if 'linux::Application' in type:
    app = ec.register_resource(type)
    ec.set(app, "command", cmd)
    ec.register_connection(app, node)

    return app

def execute(ec, apps):
  ec.deploy()
  #self.ec.register_condition (apps[0], ResourceAction.START, apps[1], ResourceState.STOPPED)
  #self.ec.deploy(guids=apps)
  ec.wait_finished(apps)

  for ap in apps:
    print ec.trace(ap, "stdout")

  ec.shutdown()


