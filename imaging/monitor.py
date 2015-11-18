import asyncio

# message_bus is just an asyncio.Queue

class Monitor:
    def __init__(self, message_bus):
        self.message_bus = message_bus

    @asyncio.coroutine
    def run(self):
        while True:
            message = yield from self.message_bus.get()
            if message == 'END-MONITOR':
                break
            self.dispatch(message)
            # this is new in 3.4.4
            if 'task_done' in dir(self.message_bus):
                self.message_bus.task_done()
        print("Monitor is really stopping now")

    def dispatch(self, message):
        print("monitor: ==========", message)

    @asyncio.coroutine
    def stop(self):
        print("MONITOR is STOPPING...")
        yield from self.message_bus.put("END-MONITOR")
