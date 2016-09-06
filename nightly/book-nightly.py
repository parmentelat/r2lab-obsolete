#/usr/bin/env python3
# sample code to book leases
# expected to run on either faraday or r2lab

import os.path
import uuid
import asyncio
from argparse import ArgumentParser
from rhubarbe.omfsfaproxy import OmfSfaProxy
from datetime import datetime
import time


parser = ArgumentParser()
parser.add_argument("-b", "--begin", dest="begin",
                    help="Initial slice date time (Ex. 2016-10-10T10:00:00Z)")
parser.add_argument("-e", "--end", dest="end",
                    help="Final slice date time (Ex. 2016-10-10T10:00:00Z)")
parser.add_argument("-s", "--slice", dest="slice", default="onelab.inria.r2lab.nightly",
                    help="Slice name")
args = parser.parse_args()



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



def format_date(val=None):
    """ current date (2016-09-05T15:29:18Z)
    """
    if val is None:
        return datetime.now().strftime("%Y-%m-%d %H:%M")
    else:
        return str(datetime.strptime(val, "%Y-%m-%d %H:%M").date())



def main(args):
    """
    """
    begin = args.begin
    end   = args.end
    slice = args.slice

    if (begin is None or end is None or slice is None):
        print("ERROR: slice name, begin and final date must be present.")
        exit()
    else:
        print("INFO: slice {} starting at: {}, and finishing at: {}.".format(slice, begin,end))
        loop = asyncio.get_event_loop()
        js = loop.run_until_complete(co_add_lease(slice, begin, end))
        # print(js)



if __name__ == '__main__':
    exit(main(args))
