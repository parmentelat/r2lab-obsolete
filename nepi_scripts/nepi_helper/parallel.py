import threading
import time
import tools


exitFlag = 0

class Parallel (threading.Thread):
    """ Run process in parallel """

    def __init__(self, node):
        threading.Thread.__init__(self)
        self.node = node

    def run(self):
        print "Starting ..." + self.node.node
        #print_time(self.name, 5)
        self.fork(self.node)
        print "Exiting ..." + self.node.node


    def fork(self, node):
        random = (time.strftime("%m%d%Y%H%M%S"))
        temp = tools.Simulation.new('parallel_{}_'.format(node.node)+random)

def print_time(threadName, counter=None, delay=None):
    """ Function to print time in parallel """

    if delay is None:
        delay   = 1
    if counter is None:
        counter = 5

    while counter:
        if exitFlag:
            thread.exit()
        time.sleep(delay)
        print "%s: %s" % (threadName, time.ctime(time.time()))
        counter -= 1
