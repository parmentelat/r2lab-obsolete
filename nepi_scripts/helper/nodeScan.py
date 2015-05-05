#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------
# Main call to operate with the helper using one or a couple of nodes
# File talkNodeC uses class, File talkNodeF uses functions
# Both to operate using NEPI in Linux nodes.
# Mario ZANCANARO <mario.zancanaro@inria.fr>
# ----------------------------

from optparse import OptionParser
from talkNodeC import TalkNodeHelper
# from talkNodeF import *
# from nepi.execution.ec import ExperimentController #if talkNodeF is imported

# MAIN CALL
def main():

	# Values by default or add in your line call the options -g <your_gataway>, etc ...
	parser = OptionParser()
	parser.add_option('-g',		'--gwy'		,default='<your_server>' 			,dest='gwy'		,type="str"		,help='gateway to conect the node.')
	parser.add_option('-u',		'--gus'		,default='<your_user_server>'	,dest='gus'		,type="str"		,help='gateway username.')
	parser.add_option('-k',		'--gky'		,default='<your_key_path>'		,dest='gky'		,type="str"		,help='gateway ssh key.')
	parser.add_option('-i',		'--id'		,default='my-experiment'			,dest='id'		,type="str"		,help='experiment identification.')
	parser.add_option('-n',		'--nd'		,default='<your_node>'				,dest='nd'									,help='ip/alias nodes to verify, node01,node02,...,node n.')
	parser.add_option('-s',		'--nus'		,default='<your_user_node>'		,dest='nus'		,type="str"		,help='node(s) username.')

	(opt, args) = parser.parse_args()
	node_hosts		= opt.nd.split(',')
	connOpt = eval(str(opt))
	

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
