#/usr/bin/env python3
# sample code to book leases
# expected to run on either faraday or r2lab

import os.path
import uuid
import asyncio

from rhubarbe.omfsfaproxy import OmfSfaProxy

def locate_credentials():
    locations = [
        '/etc/rhubarbe/root.pem',
        '/root/.omf/user_cert.pem',
    ]
    for location in locations:
        if os.path.exists(location):
            return location

@asyncio.coroutine
def co_add_lease(slicename, valid_from, valid_until):
    credentials = locate_credentials()
    if not credentials:
        print("ERROR: cannot find credentials")
        exit(1)
    # the omf-sfa API
    omf_sfa_proxy = OmfSfaProxy("faraday.inria.fr", 12346,
                                # the root certificate has the private key embedded
                                credentials, None,
                                "37nodes")

    node_uuid = yield from omf_sfa_proxy.fetch_node_uuid()
    lease_request = {
        'name' : str(uuid.uuid1()),
        'valid_from' : valid_from,
        'valid_until' : valid_until,
        'account_attributes' : { 'name' : slicename },
        'components' : [ {'uuid' : node_uuid } ],
    }

    print("INFO: omf_sfa POST request {}".format(lease_request))
    result = yield from omf_sfa_proxy.REST_as_json("leases", "POST", lease_request)
    print("INFO: omf_sfa POST -> {}".format(result))
    return result


beg, end = "2016-08-08T10:00:00Z", "2016-08-08T11:00:00Z"
slice = "onelab.inria.r2lab.nightly"

loop = asyncio.get_event_loop()
js = loop.run_until_complete(co_add_lease(slice, beg, end))
print(js)
