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

import os, os.path

import json

from argparse import ArgumentParser

# to locate the server when no -s option is provided:
# if this path exists we use localhost

omf_path = "/root/omf_sfa"

# otherwise this is the default hostname

default_hostname = 'faraday.inria.fr'
default_port_number=12346

rest_url_format = "https://{hostname}:{port_number}/resources/nodes"

# the cache file
tmp_json = "/tmp/db.json"

def fetch(hostname, port_number):
    rest_url = rest_url_format.format(hostname=hostname, port_number=port_number)
    curl_command = "curl -k {} -o {}".format(rest_url, tmp_json)
    print ("Running {}".format(curl_command))
    retcod = os.system (curl_command)
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

def main():

    if os.path.exists (omf_path):
        default_hostname = 'localhost'

    parser = ArgumentParser()
    parser.add_argument("-f","--fast",action='store_true', default=False,
                        help="use json file {} instead of fetching it again".format(tmp_json))
    parser.add_argument("-s","--omf-server",dest='omf_server',default=default_hostname,
                        help="specify hostname (default is {default})")
    parser.add_argument("-p","--port-number",dest='port_number',default=default_port_number,
                        help="specify port number (default is {default})")
    args=parser.parse_args()

    if not args.fast:
        fetch(hostname=args.omf_server, port_number=args.port_number)
    
    display()

if __name__ == '__main__':
    exit(main())
