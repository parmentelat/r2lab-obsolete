# #!/usr/bin/env python
# # -*- coding: utf-8 -*-

#----------------------------
# HELPER to talk nodes by a class
# Mario ZANCANARO <mario.zancanaro@inria.fr>
#----------------------------

from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceState, ResourceAction

class TalkNodeHelper(ExperimentController): 
  
  def __init__(self, id):
    self.id = id
    super(TalkNodeHelper, self).__init__()

  def create_node(self, type='linux::Node', **opt):
    gateway         = opt['gwy']
    gw_user         = opt['gus']
    gw_key          = opt['gky']
    node_host       = opt['nd']
    node_user       = opt['nus']

    if 'linux::Node' in type:
      node = self.register_resource(type)
      self.set(node, "username", node_user)
      self.set(node, "hostname", node_host)
      self.set(node, "identity", gw_key)
      self.set(node, "gateway", gateway)
      self.set(node, "gatewayUser", gw_user)
      self.set(node, "cleanExperiment", True)

    return node


  def create_app(self, node, type='linux::Application', cmd='date'):
    if 'linux::Application' in type:
      app = self.register_resource(type)
      self.set(app, "command", cmd)
      self.register_connection(app, node)

    return app


  def execute(self, apps):
    self.deploy()
    #self.ec.register_condition (apps[0], ResourceAction.START, apps[1], ResourceState.STOPPED)
    #self.ec.deploy(guids=apps)
    self.wait_finished(apps)

    for ap in apps:
      print self.trace(ap, "stdout")

    self.shutdown()


