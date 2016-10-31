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

    async def probe(self, verbose):
        # xxx could use a 'is_connected' method here
        if not self.gateway.conn:
            await self.gateway.connect_lazy()
            if verbose:
                print("Connected -> {}".format(self.gateway))
        try:
            self.gateway.formatter.start_capture()
            retcod = await self.gateway.run("{} shell \"settings get global airplane_mode_on\""
                                            .format(self.adb_bin))
            result = self.gateway.formatter.get_capture().strip()
            airplane_mode = 'on' if result == '1' else 'off'
            info = { 'id' : self.id, 'airplane_mode' : airplane_mode}
            if verbose:
                print("probed phone {} : retcod={} result={} -> emitting {}"
                  .format(self.adb_id, retcod, result, info))
            self.reconnectable.emit_info(sidecar_channel, info)
                                         
        except Exception as e:
            print("Could not probe {} -> {}".format(self.adb_id, e))
            # force ssh reconnect
            self.gateway.conn = None
        await asyncio.sleep(2)

    async def probe_forever(self, verbose):
        while True:
            await self.probe(verbose)


class Monitor:
    def __init__(self, phone_specs):
        reconnectable = ReconnectableSocketIO(sidecar_hostname,
                                              sidecar_port)
        self.phones = [ MonitorPhone(reconnectable = reconnectable, **spec) for spec in phone_specs ]

    def main(self):
        parser = ArgumentParser()
        parser.add_argument("-v", "--verbose", default=False, action='store_true')
        args = parser.parse_args()
        results = asyncio.gather(*[phone.probe_forever(args.verbose) for phone in self.phones])
        loop = asyncio.get_event_loop()
        loop.run_until_complete(results)
        return 0
    
Monitor(phone_specs).main()
