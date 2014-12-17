#!/usr/bin/env python3

# somehow using pycurl I run into this
# pycurl.error: (56, 'GnuTLS recv error (-9): A TLS packet with unexpected length was received.')
#import pycurl 
#curl = pycurl.Curl()
#curl.setopt(pycurl.URL, rest_url)
#curl.setopt(pycurl.SSL_VERIFYPEER, 0)   
#curl.setopt(pycurl.SSL_VERIFYHOST, 0)
#curl.perform()
#info = curl.getinfo()

from os import system

import json

from argparse import ArgumentParser

rest_url_format = "https://{hostname}:8001/resources/nodes"

tmp_json = "/tmp/db.json"

def fetch(hostname):
    rest_url = rest_url_format.format(hostname=hostname)
    curl_command = "curl -k {} -o {}".format(rest_url, tmp_json)
    print ("Running {}".format(curl_command))
    retcod = system (curl_command)
    if retcod != 0:
        print ("Failed to fetch {} - exiting".format(tmp_json))
        exit(1)

def parse():
    with open(tmp_json) as feed:
        db = json.load(feed)
    return db

def display():
    raw = parse()
    resource_response = raw['resource_response']
    resources = resource_response['resources']
    for resource in sorted(resources, key=lambda r:r['name']):
        print ('hn:', resource['hostname'],
               'nm:', resource['name'],
               'cm:', resource['cmc']['ip']['address'],
               'st:', resource['status'],
               )

default_hostname = 'faraday.inria.fr'
        
def main():
    parser = ArgumentParser()
    parser.add_argument("-s","--speed",action='store_true', default=False,
                        help="use json file {} instead of fetching it again".format(tmp_json))
    parser.add_argument("-o","--omf-host",dest='omf_hostname',default=default_hostname,
                        help="specify hostname (default is {default})")
    args=parser.parse_args()

    if not args.speed:
        fetch(hostname=args.omf_hostname)
    
    display()

if __name__ == '__main__':
    exit(main())
