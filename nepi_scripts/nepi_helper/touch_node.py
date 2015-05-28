#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#     ***** touch_node.py
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
#     This file contains the main call to manipulate Linux simulations using Nepi framework.
#			talkNodeF or talknodeC must be included to help the manipulation. File talk_node_c uses class,
#			File talk_node_f uses functions		
#     The options could be passed by command line or defined by default between lines 53 and 58.
#     The options passed by command line overrides the defaults defined by default below.     
#     
#			Example of how to run this experiment (replace with your information or set the options between lines 59 and 64):
# 			$ cd <path-where-you-saved/this>
# 			python touch_node.py -g <your.server.com> -u <your_user_name> -k <your_ssh_key_path> ... -nd node01,node02
#
#			-If you want to use the helper through functions, line 45 and 46 must be uncommented
#				In this case the experiment example is given between lines 84 and 88
#			OR (comment the lines of the option you won't use)
#			-If you want to use the helper through class, lines 44 must be uncommented
#				
#
# Author: Mario ZANCANARO <mario.zancanaro@inria.fr>
# 

from optparse import OptionParser
from talk_node_c import TalkNodeHelper
# from talk_node_f import *
# from nepi.execution.ec import ExperimentController #if talk_node_f is imported

# MAIN CALL
def main():

	# Values by default or add in your line call the options -g <your_gataway>, etc ...
	parser = OptionParser()
	parser.add_option('-g',		'--gateway'			,default='faraday.inria.fr'		,dest='gateway'			,type="str"		,help='gateway to conect the node.')
	parser.add_option('-u',		'--gateway_user'	,default='mario'				,dest='gateway_user'	,type="str"		,help='gateway username.')
	parser.add_option('-k',		'--gateway_user_key',default='~/.ssh/id_rsa'		,dest='gateway_user_key',type="str"		,help='gateway ssh key.')
	parser.add_option('-i',		'--experiment_id'	,default='my-experiment'		,dest='experiment_id'	,type="str"		,help='experiment identification.')
	parser.add_option('-n',		'--node_name'		,default='fit02'				,dest='node_name'						,help='ip/alias nodes to verify, node01,node02,...,node n.')
	parser.add_option('-s',		'--node_user'		,default='root'					,dest='node_user'		,type="str"	,help='node(s) username.')

	(opt, args) = parser.parse_args()
	node_hosts		= opt.node_name.split(',')
	connOpt = eval(str(opt))


	# This block will be executed for each node configured at [nd] option
	#for node in node_hosts:
	#connOpt['nd'] = node
	id = connOpt['experiment_id']

	# Using talkNodeC (through class)
	tk = TalkNodeHelper(id)


	######################################	
	# EXECUTION DIRECTLY IN GATEWAY
	print "-- connect gateway"
	nodeGw = tk.new_node_gateway(**connOpt)

	#free = tk.free_cmd('curl 192.168.1.02/info', nodeGw)
	#tk.execute([free])

	#onoff = tk.turn_node('192.168.1.02','on')
	#tk.execute([onoff])

	#reset = tk.reset_node('192.168.1.02')
	#tk.execute([reset])

	#info = tk.info_node('192.168.1.02')
	#tk.execute([info])

	######################################
	# EXECUTION FOR NODES FROM GATEWAY
	connOpt['node_name'] = 'fit02'
	print "-- execution for node #{} --".format(connOpt['node_name'])
	node = tk.new_node(**connOpt)

	#turn_wlan = tk.turn_wlan(1, 'down', node)
	#tk.execute([turn_wlan])	

	turn_wlan = tk.turn_wlan(1, 'up', node)
	tk.execute([turn_wlan])	

	turn_wlan = tk.turn_wlan(2, 'up', node)
	tk.execute([turn_wlan])	

	#status_wlan = tk.status_wlan(2, node)
	#tk.execute([status_wlan])	

	tk.change_interface('wlan1')
	ping1 = tk.simple_ping(1, node)
	
	tk.change_interface('wlan2')
	ping2 = tk.simple_ping(1, node)

	tk.change_interface('p2p1')
	ping3 = tk.simple_ping(1, node)
	
	tk.execute([ping1, ping2, ping3])

	#free = tk.free_cmd('ping -c1 nepi.inria.fr', node)
	#tk.execute([free])

	#connOpt['node_name'] = 'fit03'
	#print "-- execution for node #{} --".format(connOpt['node_name'])
	#nodeB = tk.newNode(**connOpt)

	tk.shutdown()

if __name__ == '__main__':
	exit(main())
