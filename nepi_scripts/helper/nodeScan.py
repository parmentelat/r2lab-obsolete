#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#     ***** nodeScan.py
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
#			talkNodeF or talknodeC must be included to help the manipulation. File talkNodeC uses class,
#			File talkNodeF uses functions		
#     The options could be passed by command line or defined by default between lines 59 and 64.
#     The options passed by command line overrides the defaults defined by default below.     
#     
#			Example of how to run this experiment (replace with your information or set the options between lines 59 and 64):
# 			$ cd <path-where-you-saved/this>
# 			python nodeScan.py -g <your.server.com> -u <your_user_name> -k <your_ssh_key_path> ... -nd node01,node02
#
#			-If you want to use the helper through functions, line 51 and 52 must be uncommented
#				In this case the experiment example is given between lines 84 and 88
#			OR (comment the lines of the option you won't use)
#			-If you want to use the helper through class, lines 50 must be uncommented
#				In this case the experiment example is given between lines 77 and 81
#
# Author: Mario ZANCANARO <mario.zancanaro@inria.fr>
# 

from optparse import OptionParser
from talkNodeC import TalkNodeHelper
# from talkNodeF import *
# from nepi.execution.ec import ExperimentController #if talkNodeF is imported

# MAIN CALL
def main():

	# Values by default or add in your line call the options -g <your_gataway>, etc ...
	parser = OptionParser()
	parser.add_option('-g',		'--gwy'		,default='<your_server>'			,dest='gwy'		,type="str"		,help='gateway to conect the node.')
	parser.add_option('-u',		'--gus'		,default='<your_user_server>'	,dest='gus'		,type="str"		,help='gateway username.')
	parser.add_option('-k',		'--gky'		,default='<your_key_path>'		,dest='gky'		,type="str"		,help='gateway ssh key.')
	parser.add_option('-i',		'--id'		,default='my-experiment'			,dest='id'		,type="str"		,help='experiment identification.')
	parser.add_option('-n',		'--nd'		,default='<your_node>'				,dest='nd'									,help='ip/alias nodes to verify, node01,node02,...,node n.')
	parser.add_option('-s',		'--nus'		,default='<your_user_node>'		,dest='nus'		,type="str"		,help='node(s) username.')

	(opt, args) = parser.parse_args()
	node_hosts		= opt.nd.split(',')
	connOpt = eval(str(opt))
	

	# This block will be executed for each node configured at [nd] option
	for node in node_hosts:
		connOpt['nd'] = node
		print "-- execution for node #{} --".format(node)

		# Using talkNodeC (through class)
		tkA = TalkNodeHelper('my-ping')
		nodeA = tkA.create_node(**connOpt)
		app_A = tkA.create_app(nodeA, cmd='ping -c1 nepi.inria.fr')
		app_B = tkA.create_app(nodeA, cmd='date')		
		tkA.execute([app_A,app_B])

		# Using talkNodeF (through functions)
		# ec = ExperimentController('my-ping')
		# nodeA = create_node(ec, **connOpt)
		# app_A = create_app(ec, nodeA, cmd='ping -c1 nepi.inria.fr')
		# app_B = create_app(ec, nodeA, cmd='date')
		# execute(ec, [app_A,app_B])


if __name__ == '__main__':
	exit(main())
