import time
import asyncio

import telnetlib3

import re

class FrisbeeParser(telnetlib3.TerminalShell):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.bytes_line = b""
        self.total_chunks = 0

    def feed_byte(self, x):
        if x == b"\n":
            self.parse_line()
            self.bytes_line = b""
        else:
            self.bytes_line += x

    # parse frisbee output
    # tentatively ported from nitos_testbed ruby code but never tested
    matcher_new_style_progress = re.compile('[\.sz]{60,75}\s+\d+\s+(?P<remaining_chunks>\d+)')
    matcher_total_chunks = re.compile('.*team after (?P<time>[0-9\.]*).*File is (?P<total_chunks>[0-9]+) chunks.*')
    matcher_old_style_progress = re.compile('^Progress:\s+(?P<percent>[\d]+)%.*')
    matcher_final_report = re.compile('^Wrote\s+(?P<total>\d+)\s+bytes \((?P<actual>\d+).*')
    matcher_short_write = re.compile('.*Short write.*')
    matcher_status = re.compile('FRISBEE-STATUS=(?P<status>\d+)')

    def parse_line(self):
        line = self.bytes_line.decode().strip()
        #
        m = self.matcher_new_style_progress.match(line)
        if m:
            if self.total_chunks == 0:
                print("new frisbee: cannot report progress, missing total chunks")
                return
            percent = int ( 100 * (1 - int(m.group('remaining_chunks'))/self.total_chunks))
            self.send_percent(percent)
        #
        m = self.matcher_total_chunks.match(line)
        if m:
            self.total_chunks = int(m.group('total_chunks'))
            self.send_percent(1)
            return
        #
        m = self.matcher_old_style_progress.match(line)
        if m:
            self.send_percent(m.group('percent'))
            return
        #
        m = self.matcher_final_report.match(line)
        if m:
            print("FRISBEE END: total = {total} bytes, actual = {actual} bytes"
                  .format(total=m.group('total'), actual=m.group('actual')))
            self.send_percent(100)
            return
        #
        m = self.matcher_short_write.match(line)
        if m:
            print("Something went wrong with frisbee...")
            return
        #
        m = self.matcher_status.match(line)
        if m:
            status = int(m.group('status'))
            print("frisbee status ->{}".format(status))
            
    def send_percent(self, percent):
        print("PERCENTS:", percent)


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
        self._protocol = None

    def is_ready(self):
        # xxx for now we don't check that frisbee is installed and the expected version
        return self._protocol is not None

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

    Client = telnetlib3.TelnetClient
    
    @staticmethod
    def client_factory():
        return FrisbeeConnection.Client(encoding='utf-8', shell=FrisbeeParser)
#        return FrisbeeConnection.Client(encoding='utf-8', shell=telnetlib3.TerminalShell)

    @asyncio.coroutine
    def try_to_connect(self):
        yield from self.message_bus.put("{} : trying to telnet".format(self.hostname))
        try:
            self._transport, self._protocol = \
              yield from self.loop.create_connection(self.client_factory, self.hostname, 23)
            yield from self.message_bus.put("{}: telnet connected".format(self.hostname))
            return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            yield from self.message_bus.put("Could not connect - backing off for a while")
            # just making sure
            self._transport, self._protocol = None, None

    @asyncio.coroutine
    def run_client(self, bin, ip, multicast_group, port, hdd):
        # xxx probably too harsh
        assert self.is_ready()
        EOF = chr(4)
        EOL = '\n'
        self.command = \
          "{bin} -i {ip} -m {multicast_group} -p {port} {hdd}".format(**locals())

#        # tmp - dbg
#        self.command = "hostname"

        EOF = chr(4)
        EOL = '\n'
        # print out exit status
        command = self.command
        command = command + "; echo FRISBEE-STATUS=$?"
        # make sure the command is sent (EOL) and that the session terminates afterwards (exit + EOF)
        command = command + "; exit" + EOL + EOF
        yield from self.message_bus.put("{} sending command {}"
                                        .format(self.hostname, command))
        self._protocol.stream.write(self._protocol.shell.encode(command))

        print("run_client : command = {}".format(command))
        # xxx should maybe handle timeout here with some kind of loop...
        # wait for telnet to terminate
        yield from self._protocol.waiter_closed
