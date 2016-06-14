import threading
import time
import sys
from nepi.execution.ec import ExperimentController
from nepi.execution.resource import ResourceAction, ResourceState
from argparse import ArgumentParser
import os
from nepi.util.sshfuncs import logger
from datetime import datetime


exitFlag = 0

class Parallel (threading.Thread):
    """ Run process in parallel """

    def __init__(self, command, host_name='localhost', host_user='root', key='node'):
        threading.Thread.__init__(self)
        self.command    = command
        self.host_name  = host_name
        self.host_user  = host_user
        self.key        = key

    def run(self):
        self.output = execute(self.command, self.host_name, self.host_user, self.key)


    def stop(self):
        self._Thread__stop()


    def alive(self):
        return self.isAlive()


    def output(self):
        return self.output


def execute(command, host_name='localhost', host_user='root', key='node'):
    """ Execute the command in host """

    ec = ExperimentController()

    node = ec.register_resource("linux::Node")
    ec.set(node, "hostname", host_name)
    ec.set(node, "username", host_user)
    ec.set(node, "cleanExperiment", True)
    ec.set(node, "cleanProcesses", False)
    ec.set(node, "cleanProcessesAfter", False)
    ec.deploy(node)

    app = ec.register_resource("linux::Application")
    ec.set(app, "command", command)
    ec.register_connection(app, node)
    ec.deploy(app)
    ec.wait_finished(app)

    stdout    = ec.trace(app, "stdout")
    exitcode  = ec.trace(app, 'exitcode')

    results = {}
    results.update({ str(key) : {'exitcode' : exitcode, 'stdout' : stdout}})

    return results
