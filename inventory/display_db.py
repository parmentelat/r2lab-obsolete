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

rest_url = "https://localhost:8001/resources/nodes"

tmp_json = "/tmp/db.json"

def fetch():
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
    for resource in resources:
        print ('hostname:', resource['hostname'],
               'name:', resource['name'],
               'status:', resource['status'],
               )
        
def main():
    parser = ArgumentParser()
    parser.add_argument("-s","--speed",action='store_true', default=False,
                        help="use json file {} instead of fetching it again".format(tmp_json))
    args=parser.parse_args()

    if not args.speed:
        fetch()
    
    display()

if __name__ == '__main__':
    exit(main())
