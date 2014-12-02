#!/usr/bin/env python

class Node(object):
    def __init__(self, number, mac, alt_mac):
        self.number = number
        self.mac = mac
        self.alt_mac = alt_mac

    def model(self):
        node2 = "{:02d}".format(self.number)
        nodename = "fit"+node2
        domain = 'faraday'
        return {
            "name": nodename,
            "hostname": nodename,
            "hardware_type": "PC-Icarus",
            "urn": "urn:publicid:IDN+omf:faraday+node+"+nodename,
            "interfaces": [
                {
                    "name": nodename+":if0",
                    "role": "control",
                    "mac": self.mac,
                    "ip": {
                        "address": "192.168.3.{}".format(self.number),
                        "netmask": "255.255.255.0",
                        "ip_type": "ipv4"
                    }
                },
                {
                    "name": nodename+":if1",
                    "role": "experimental",
                    "mac": self.alt_mac
                }
            ],
            "cmc": {
                "name": nodename+":cm",
                "mac": "02:00:00:00:00:"+node2,
                "ip": {
                    "address": "192.168.1.{}".format(self.number),
                    "netmask": "255.255.255.0",
                    "ip_type": "ipv4"
                }
            },
            "cpu": {
                "cpu_type": "Intel 4770kI7",
                "cores": 4,
                "threads": 8,
                "cache_l1": "n/a",
                "cache_l2": "8 Mb"
            },
            "ram": "8 GB",
            "ram_type": "DIMM Synchronous",
            "hd_capacity": "240 GB"
        }

########################################
import re
import csv
import json


mac_regexp = re.compile ('(?P<prefix>([0-9A-Fa-f]{2}:){5})(?P<last>[0-9A-Fa-f]{2})')

with open('fit.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile)
    nodes = []
    for lineno, line in enumerate(reader):
        try:
            number = int (line[1])
            mac = line[4]
            match = mac_regexp.match(mac)
            if match:
                prefix, last = match.group('prefix', 'last')
                byte = int (last, base=16)
                alt_last = str(byte-1)
                alt_mac = prefix+alt_last
                nodes.append(Node(number, mac, alt_mac))
            else:
                print lineno,'non-mac',mac
        except Exception as e:
            print 'skipping line',lineno,line

    with open ('fit.json', 'w') as jsonfile:
        models = [ node.model() for node in nodes ]
        json.dump (models, jsonfile)
        
