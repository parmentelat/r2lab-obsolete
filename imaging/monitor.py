import time
import asyncio

import util

# message_bus is just an asyncio.Queue

class Monitor:
    def __init__(self, message_bus):
        self.message_bus = message_bus
        self.alive = True
        self.start = None

    @asyncio.coroutine
    def listener(self):
        self.start = time.time()
        
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
    def stop(self):
        yield from self.message_bus.put("END-MONITOR")

    def dispatch(self, message):
        timestamp = time.strftime("%H:%M:%S")
        # in case the message is sent before the event loop has started
        duration = "+{:03}s".format(int(time.time()-self.start)) \
          if self.start is not None \
          else 5*'-'
        print("{} - {}: {}".format(timestamp, duration , message))

    run = listener

    
