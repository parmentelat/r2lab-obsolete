#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
#     This file contains a class that inherits ExperimentController from NEPI framework
#     used at INRIA testbed (R2Lab) with Nitos nodes.  
#               
# Author: Mario ZANCANARO <mario.zancanaro@inria.fr>
# 
from tools import Simulation, Node, VirtualTable
import time

# MAIN CALL
def main():
    
    random = (time.strftime("%m%d%Y%H%M%S"))

    s1 = Simulation.new('my-experiment'+random)

    fit10 = Node.new('Fit10')
    #fit10.on()
    fit10.ping('www.inria.fr')
    fit10.free_command('hostname')
    
    fit13 = Node.new('Fit13')
    #fit13.on()
    fit13.free_command('date')
    fit13.free_command('hostname')
    fit13.free_command('date')
    
    s1.ping('www.something.com', 3, fit10,fit13)
    
    fit10.commands.state()
    fit13.commands.state()

    #fit02 = Node.clone('Fit02', fit10)
    
    #s1.execute(fit10, fit13)
    #s1.execute(fit10)

if __name__ == '__main__':
    exit(main())


