#!/usr/bin/env python3

# expects a single input argument that is the CMC IP address

from argparse import ArgumentParser

# see also http://nagios.sourceforge.net/docs/3_0/pluginapi.html

import pycurl 

from io import BytesIO

def nagios_on_off(cmc_ip):
    """
    Open a http connection to this IP on /status
    returns
    0 if node is on
    1 if node is off
    3 if no answer
    """
    url = "http://{}/status".format(cmc_ip)
    buffer = BytesIO()

    curl = pycurl.Curl()
    curl.setopt(curl.URL, url)
    curl.setopt(curl.WRITEDATA, buffer)
    curl.setopt(curl.TIMEOUT_MS, 2000)
    try:
        curl.perform()
        curl.close()
        raw = buffer.getvalue().decode('UTF-8').strip()
        if 'on' in raw:
            print("NODE controlled by {} is ON".format(cmc_ip))
            return 0
        elif 'off' in raw:
            print("NODE controlled by {} is OFF".format(cmc_ip))
            return 1
        else:
            print("{} is UNREACHABLE".format(cmc_ip))
            return 3
    except pycurl.error as e:
            print("{} is UNREACHABLE ({})".format(cmc_ip,e))
            return 3
        

def main():
    parser = ArgumentParser()
    parser.add_argument('cmc_ip')
    args = parser.parse_args()
    return nagios_on_off(args.cmc_ip)

if __name__ == '__main__':
    exit(main())
