#!/usr/bin/env python3

# this simple tool works a bit like rhubarbe.monitor but on our phones
# for now it probes for airplane_mode, but does not probe for the state of
# the wifi service because I could not get to work the magic sentences
# like 'adb shell svc enable wifi' and similar that I have found on the web
#
# it is rustic in the sense that
# (*) the configuration for now is built in the script instead of
#     loading .json or other .ini files
# (*) imports rhubarbe's ReconnectableSocketIO object for a
#     auto-reconnect behaviour
# (*) for now it has no systemctl service defined

import asyncio
from argparse import ArgumentParser

from socketIO_client import SocketIO, LoggingNamespace

from apssh.sshproxy import SshProxy
from apssh.formatters import CaptureFormatter

from rhubarbe.monitor import ReconnectableSocketIO

sidecar_hostname = "r2lab.inria.fr"
sidecar_port = 443
sidecar_channel = 'info:phones'

# should be in some JSON file somewhere
phone_specs = [
    {
        'id' : 1,
        'gw_host' : 'macphone',
        'gw_user' : 'tester',
        'gw_key'  : "/home/faraday/r2lab/inventory/macphone",
        # path in the gateway
        'adb_bin' : "/Users/tester/nexustools/adb",
        'adb_id'  : '062337da0051af9f',
    }
]

class MonitorPhone:

    # id is what you get through adb devices
    def __init__(self, id, gw_host, gw_user, gw_key, adb_bin, adb_id, reconnectable):
        self.id = id
        self.gateway = SshProxy(
            hostname = gw_host,
            username = gw_user,
            keys = [gw_key],
            formatter = CaptureFormatter(verbose = False)
        )
        self.adb_bin = adb_bin
        self.adb_id = adb_id
        self.reconnectable = reconnectable
        self.info = { 'id' : self.id }

    def emit(self):
        self.reconnectable.emit_info(sidecar_channel, self.info, wrap_in_list=True)

    async def probe(self, verbose):

        # connect or reconnect if needed
        # xxx could use a 'is_connected' method here
        if not self.gateway.conn:
            try:
                await self.gateway.connect_lazy()
                if verbose:
                    print("Connected -> {}".format(self.gateway))
            except:
                print("Could not connect -> {}".format(self.gateway))
                self.info['airplane_mode'] = 'fail'
                self.emit()
                return

        try:
            self.gateway.formatter.start_capture()
            retcod = await self.gateway.run("{} shell \"settings get global airplane_mode_on\""
                                            .format(self.adb_bin))
            result = self.gateway.formatter.get_capture().strip()
            airplane_mode = 'fail' if retcod != 0 else 'on' if result == '1' else 'off'
            if verbose:
                print("probed phone {} : retcod={} result={} -> airplane_mode = {}"
                      .format(self.adb_id, retcod, result, airplane_mode))
            self.info['airplane_mode'] = airplane_mode
                                         
        except Exception as e:
            print("Could not probe {} -> {}".format(self.adb_id, e))
            self.info['airplane_mode'] = 'fail'
            # force ssh reconnect
            self.gateway.conn = None
        self.emit()

    async def probe_forever(self, verbose):
        while True:
            await self.probe(verbose)
            
            await asyncio.sleep(2)

class Monitor:
    def __init__(self, phone_specs):
        reconnectable = ReconnectableSocketIO(sidecar_hostname,
                                              sidecar_port)
        self.phones = [ MonitorPhone(reconnectable = reconnectable, **spec) for spec in phone_specs ]

    def main(self):
        parser = ArgumentParser()
        parser.add_argument("-s", "--silent", dest='verbose', default=True, action='store_false')
        parser.add_argument("-v", "--verbose", action='store_true')
        args = parser.parse_args()
        results = asyncio.gather(*[phone.probe_forever(args.verbose) for phone in self.phones])
        loop = asyncio.get_event_loop()
        loop.run_until_complete(results)
        return 0
    
Monitor(phone_specs).main()
