#/usr/bin/env python3
#
# Author file: Mario Zancanaro <mario.zancanaro@inria.fr>
#
"""
The book-nightly is a script used to book leases for the nightly routine which runs in faraday
The code will search for all WEDNESDAYs and SUNDAYs between a given period to schedule 1 hour task (3am until 4am)
in each day found.
If no period is given, the whole year period is assumed based in the current year.

Be careful in use a different slice name because: onelab.inria.r2lab.nightly is hardcoded in run/book r2lab pages
to present special contents linked with this name.
"""

import os.path
import uuid
import asyncio
from argparse import ArgumentParser
from rhubarbe.omfsfaproxy import OmfSfaProxy
from datetime import datetime, timedelta
import time
from itertools import islice
from pytz import timezone

parser = ArgumentParser()
parser.add_argument("-p", "--period", dest="period", nargs=2, type=str, default=[None,None],
                    help="Each WED and SUN between a given period")
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
    """ return formated date
    """
    if val is None:
        return str(datetime.now().strftime("%Y-%m-%d"))
    else:
        return str(datetime.strftime(val, "%Y-%m-%d"))



def intersections(weekday, start_date=None, end_date=None):
    """ generate dates where the given weekday and day of month intersect.
    If the optional start_date is not given, uses the value of the datetime.today().
    """
    dates = []
    if start_date is None:
        date = datetime.today()
    else:
        date = start_date
    while date.strftime('%F%H%M%S') <= end_date.strftime('%F%H%M%S'):
        if date.isoweekday() == weekday:
            dates.append(date)
        date += timedelta(days=1)

    return dates



def main(args):
    """
    """
    paris = timezone('Europe/Paris')
    period_begin = args.period[0]
    period_end   = args.period[1]
    slice        = args.slice

    if period_begin is None:
        period_begin = datetime(datetime.today().year,  1, 1, tzinfo=paris)
    else:
        yyyy, mm, dd = period_begin.split('-')
        period_begin = datetime(int(yyyy), int(mm), int(dd), tzinfo=paris)

    if period_end is None:
        period_end   = datetime(datetime.today().year, 12, 31, tzinfo=paris)
    else:
        yyyy, mm, dd = period_end.split('-')
        period_end   = datetime(int(yyyy), int(mm), int(dd), tzinfo=paris)

    WEDNESDAY = 3
    SUNDAY    = 7

    if (period_begin is None or period_end is None or slice is None):
        print("ERROR: slice name, begin and final date must be present.")
        exit()
    else:
        wed_occurrences = intersections(WEDNESDAY, period_begin, period_end)
        sun_occurrences = intersections(SUNDAY   , period_begin, period_end)
        for occurrence in wed_occurrences + sun_occurrences:
            slice_beg = occurrence + timedelta(hours=3)
            slice_end = slice_beg  + timedelta(hours=1)
            #the book happens here
            loop = asyncio.get_event_loop()
            js = loop.run_until_complete(co_add_lease(slice, str(slice_beg), str(slice_end)))

        print("INFO: {} slices {} between {} and {} were added.".format(len(wed_occurrences+sun_occurrences),slice, format_date(period_begin), format_date(period_end)))



if __name__ == '__main__':
    exit(main(args))
