import time

import asyncio

import util

# message_bus is just an asyncio.Queue

class Monitor:
    def __init__(self, message_bus, timeout):
        self.message_bus = message_bus
        self.timeout = timeout
        self.alive = True

    @asyncio.coroutine
    def listener(self):

        while True:
            message = yield from self.message_bus.get()
            if message == 'END-MONITOR':
                self.alive = False
                break
            self.dispatch(message)
            # this is new in 3.4.4
            if 'task_done' in dir(self.message_bus):
                self.message_bus.task_done()

    @asyncio.coroutine
    def timeout_watcher(self):

        # timeout implementation
        # this really is coarse grained
        self.start = time.time()

        while True and self.alive:
            yield from asyncio.sleep(1.)
            if time.time() - self.start >= self.timeout:
                print("TIMEOUT STOPPING")
                self.stop()
                asyncio.get_event_loop().stop()
                
    @asyncio.coroutine
    def stop(self):
        yield from self.message_bus.put("END-MONITOR")

    @asyncio.coroutine
    def run(self):
        yield from asyncio.gather(
            util.self_manage(self.listener()),
            util.self_manage(self.timeout_watcher()))

    def dispatch(self, message):
        timestamp = time.strftime("%H:%M:%S")
        print("{} - +{:03}s: {}".format(timestamp, int(time.time()-self.start), message))
