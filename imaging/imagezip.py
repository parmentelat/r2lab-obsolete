import re
from logger import logger

import asyncio
import telnetlib3

from telnet import TelnetProxy

from frisbee import FrisbeeParser as ImageZipParser

#class ImageZipParser(telnetlib3.TerminalShell):
#    def __init__(self, *args, **kwds):
#        super().__init__(*args, **kwds)
#        self.bytes_line = b""
#        self.total_chunks = 0
#
#    def feed_byte(self, x):
#        if x == b"\n":
#            self.parse_line()
#            self.bytes_line = b""
#        else:
#            self.bytes_line += x
#
#    def ip(self):
#        return self.client.proxy.control_ip
#    def feedback(self, field, msg):
#        self.client.proxy.message_bus.put_nowait({'ip': self.ip(), field: msg})
#    def send_percent(self, percent):
#        self.feedback('progress', percent)
#
#    # parse imagezip output ????
#    def parse_line(self):
#        line = self.bytes_line.decode().strip()
#        #
#        self.feedback('imagezip_raw', line)
        
class ImageZip(TelnetProxy):
    @asyncio.coroutine
    def connect(self):
        yield from self._try_to_connect(shell=ImageZipParser)

    @asyncio.coroutine
    def wait(self):
        yield from self._wait_until_connect(shell=ImageZipParser)

    @asyncio.coroutine
    def run(self, port):
        from config import the_config
        server_ip = the_config.local_control_ip()
        imagezip = the_config.value('frisbee', 'imagezip')
        netcat = the_config.value('frisbee', 'netcat')
        hdd = the_config.value('frisbee', 'hard_drive')
        self.command = \
          "{imagezip} -o -z1 {hdd} - | {netcat} {server_ip} {port}".format(**locals())

        logger.info("on {} : running command {}".format(self.control_ip, self.command))
        yield from self.feedback('frisbee_status', "starting imagezip on {}".format(self.control_ip))
        
        EOF = chr(4)
        EOL = '\n'
        # print out exit status so the parser can catch it and expose it
        command = self.command
        command = command + "; echo FRISBEE-STATUS=$?"
        # make sure the command is sent (EOL) and that the session terminates afterwards (exit + EOF)
        command = command + "; exit" + EOL + EOF
        self._protocol.stream.write(self._protocol.shell.encode(command))

        # xxx should maybe handle timeout here with some kind of loop...
        # wait for telnet to terminate
        yield from self._protocol.waiter_closed
