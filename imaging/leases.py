import asyncio
import aiohttp
import os
import time, calendar
from datetime import datetime
import json

from config import the_config
from inventory import the_inventory

debug = False

# Nov 2015
# what we get from omf_sfa is essentially something like this
#      {
#        "urn": "urn:publicid:IDN+omf:r2lab+lease+715f6987-0a4d-4ac1-8be0-112b9ef5e327",
#        "uuid": "715f6987-0a4d-4ac1-8be0-112b9ef5e327",
#        "resource_type": "lease",
#        "valid_from": "2015-11-25T14:30:00Z",
#        "valid_until": "2015-11-25T15:30:00Z",
#        "status": "active",
#        "client_id": "e78dbc52-290e-4f9a-a577-9ae7a3836743",
#        "components": [
#          {
#            "name": "fit01",
#            "urn": "urn:publicid:IDN+omf:r2lab+node+fit01",
#            "uuid": "c9ab033a-3546-472d-a363-a408b96d2065",
#            "resource_type": "node",
#            "domain": "omf:r2lab",
#            "available": true,
#            "status": "unknown",
#            "exclusive": true
#          }
#        ],
#        "account": {
#          "name": "onelab.inria.foo1",
#          "urn": "urn:publicid:IDN+onelab:inria+slice+foo1",
#          "uuid": "20a34274-8db5-414f-af6d-14bff79f8215",
#          "resource_type": "account",
#          "created_at": "2015-11-17T10:22:10Z",
#          "valid_until": "2015-12-08T15:13:52Z"
#        }
#      },

class MyLease:

    timeformat = "%Y-%m-%dT%H:%M:%S%Z"

    """
    a simple extract from the omf_sfa loghorrea
    """
    def __init__(self, omf_sfa_resource):
        r = omf_sfa_resource
        try:
            self.owner = r['account']['name']
            self.subjects = set(c['name'] for c in r['components'])
            sfrom = r['valid_from']
            suntil = r['valid_until']
            # turns out that datetime.strptime() does not seem to like
            # the terminal 'Z', so let's do this manually
            if sfrom[-1] == 'Z': sfrom = sfrom[:-1] + 'UTC'
            if suntil[-1] == 'Z': suntil = suntil[:-1] + 'UTC'
            self.ifrom = calendar.timegm(time.strptime(sfrom, self.timeformat))
            self.iuntil = calendar.timegm(time.strptime(suntil, self.timeformat))
        except Exception as e:
            # not made monitor-friendly yet
            print("Could not read omf sfa lease: {}".format(e))

    def __repr__(self):
        now = time.time()
        if self.iuntil < now:
            time_message = 'expired'
        elif self.ifrom < now:
            time_message = "from now until {}".format(self.i_to_s(self.iuntil))
        else:
            time_message = 'from {} until {}'.format(
                self.i_to_s(self.ifrom),
                self.i_to_s(self.iuntil))
        return "<Lease for {} on {} - {}>"\
            .format(self.owner, self.subjects, time_message)

    @staticmethod
    def i_to_s(epoch):
        return time.strftime(MyLease.timeformat, time.localtime(epoch))

    def is_valid(self, owner):
        if not self.owner == owner:
            if debug: print("{} : wrong owner - wants {}".format(self, owner))
            return False
        if not self.ifrom <= time.time() <= self.iuntil:
            if debug: print("{} : wrong timerange".format(self))
            return False
        if not self.subjects.intersection(set(the_inventory.all_control_hostnames())):
            if debug: print("{} : wrong subjects".format(self))
            return False
        return True

####################
class Leases:
    # the details of the omf_sfa instance where to look for leases
    def __init__(self, message_bus, login=None):
        self.hostname = the_config.value('permissions', 'leases_server')
        self.port = the_config.value('permissions', 'leases_port')
        self.message_bus = message_bus
        self.login = login if login is not None else os.getlogin()
        self.myleases = None

    def __repr__(self):
        return "<Leases for login {} - omf_sfa@{}:{}>"\
            .format(self.login, self.hostname, self.port)

    @asyncio.coroutine
    def feedback(self, field, msg):
#        yield from self.message_bus.put({field: msg})
        print("pseudo feedback {} {}".format(field, msg))

    @asyncio.coroutine
    def is_valid(self):
        if self.login == 'root':
            return True
        try:
            yield from self.fetch()
            return self._is_valid()
        except Exception as e:
            self.feedback('info', "Could not fetch leases : {}".format(e))
            return False

# TCPConnector with verify_ssl = False
# or ProxyConnector (that inherits TCPConnector) ?
    @asyncio.coroutine
    def fetch(self):
        if self.myleases is not None:
            return
        self.myleases = []
        try:
            connector = aiohttp.TCPConnector(verify_ssl=False)
            url = "https://{}:{}/resources/leases".format(self.hostname, self.port)
            response = yield from aiohttp.get(url, connector=connector)
            text = yield from response.text()
            omf_sfa_answer = json.loads(text)
            resources = omf_sfa_answer['resource_response']['resources']
            self.myleases = [MyLease(resource) for resource in resources]
        except Exception as e:
            self.feedback('leases_error', 'cannot get leases from {}'.format(self))
        
    def _is_valid(self):
        valid_leases = [lease.is_valid(self.login) for lease in self.myleases]
        return valid_leases and valid_leases[0]

    def display(self):
        print("Leases for login {}".format(self.login))
        for i, mylease in enumerate(self.myleases):
            print("{}: {}".format(i, mylease))

if __name__ == '__main__':
    try:
        login = sys.argv[1]
    except:
        login = 'onelab.inria.foo1'
    @asyncio.coroutine
    def foo(leases):
        print("leases {}".format(leases))
        valid = yield from leases.is_valid()
        print("valid = {}".format(valid))
        leases.display()
    leases = Leases(asyncio.Queue(), login)
    loop = asyncio.get_event_loop()
    task = foo(leases)
    loop.run_until_complete(task)
