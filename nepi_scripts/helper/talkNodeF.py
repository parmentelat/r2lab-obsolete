# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
#     ***** talkNodeF.py
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
#     This file contain a couple of functions to reuse codes and help use Nepi simulator
#     framework used at INRIA testbed (R2Lab) with Nitos nodes.
#     The functions groups the main commands of nepi reusing codes that create and deploy nodes.
#     To have access of the functions, just include the file in your script file like:
#     from talkNodeF import *
#     
# Author: Mario ZANCANARO <mario.zancanaro@inria.fr>
# 

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


