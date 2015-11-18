import time
import asyncio

import telnetlib3

class FrisbeeConnection:
    """
    a convenience class that help us
    * wait for the telnet server to come up
    * invoke frisbee
    """
    def __init__(self, hostname, message_bus, port=23, interval=1., loop=None):
        self.hostname = hostname
        self.message_bus = message_bus
        self.port = port
        # how often to chec kfor the connection
        self.interval = interval
        self.loop = loop if loop is not None else asyncio.get_event_loop()
        # internals
        self._transport = None
        self._connection = None

    def is_ready(self):
        # xxx for now we don't check that frisbee is installed and the expected version
        return self._connection is not None

    @asyncio.coroutine
    def wait(self):
        """
        wait for the telnet server to come up
        this has no native timeout mechanism
        """
        while True:
             yield from self.try_to_connect()
             if self.is_ready():
                 return True
             else:
                 yield from asyncio.sleep(self.interval)

    @asyncio.coroutine
    def try_to_connect(self):
        yield from self.message_bus.put("{} : trying to telnet".format(self.hostname))
        try:
            self._transport, self._connection = \
              yield from self.loop.create_connection(telnetlib3.TelnetClient, self.hostname, 23)
            yield from self.message_bus.put("{}: telnet connected".format(self.hostname))
            return True
        except OSError as e:
            yield from self.message_bus.put("Could not connect - backing off for a while")
            # just making sure
            self._transport, self._connection = None, None
