# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
#     ***** talkNodeC.py
#
#    NEPI, a framework to manage network experiments
#    Copyright (C) 2015 INRIA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as
#    published by the Free Software Foundation;
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Alina Quereilhac <alina.quereilhac@inria.fr>
#         Maksym Gabielkov <maksym.gabielkovc@inria.fr>
#
#     This file contains a class that inherits ExperimentController from Nepi framework
#     used at INRIA testbed (R2Lab) with Nitos nodes. The class add an identification attribute
#     and group the main commands of Nepi reusing codes that create and deploy nodes     
#     To have access of the class just include the file in your script file like:
#     from talkNodeC import TalkNodeHelper
# 
# Author: Mario ZANCANARO <mario.zancanaro@inria.fr>
# 

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


