#!/usr/bin/env python

"""
Assumptions here:
(*) node with physical number 33 has its CM card burned with 
    MAC address 02:00:00:00:00:33 
(*) when eth0 has MAC address xx.xx.xx.xx.xx.81 then 
    eth1 has MAC address xx.xx.xx.xx.xx.80
    this is probably too strong an assumption 
    but is hopefully good enough for now
"""

import re
import csv
import json

from argparse import ArgumentParser

from collections import OrderedDict

########################################
mac_regexp = re.compile ('(?P<prefix>([0-9A-Fa-f]{2}:){5})(?P<last>[0-9A-Fa-f]{2})')

class Node(object):
    """
    a single node, defined with its physycal number (given once and for good)
    a logical number (the actual slot in the testbed where this node sits)
    and a mac addredd (the one attached to its physical eth device)
    ---
    """
    def __init__(self, phy_num, log_num, mac, alt_mac):
        self.phy_num = phy_num
        self.log_num = log_num
        self.mac = mac
        self.alt_mac = alt_mac

    def phy_str(self):
        "physical number on 2 chars as a str"
        return "{:02d}".format(self.phy_num)
    def log_str(self):
        "logical number on 2 chars as a str"
        return "{:02d}".format(self.log_num)
    
    def phy_name(self):
        "external name based on physical number, like phy33"
        return "phy"+self.phy_str()
    def log_name(self):
        "external name based on logical number, like fit33"
        return "fit"+self.log_str()

    subnets = ( (1, 'cm'), (2, 'data'), (3, 'control') )

    def json_model(self):
        domain = 'faraday'
        return {
            "name": self.phy_name(),
            "hostname": self.log_name(),
            "hardware_type": "PC-Icarus",
            "urn": "urn:publicid:IDN+omf:faraday+node+"+self.log_name(),
            "interfaces": [
                {
                    "name": self.log_name()+":if0",
                    "role": "control",
                    "mac": self.mac,
                    "ip": {
                        "address": "192.168.3.{}".format(self.log_num),
                        "netmask": "255.255.255.0",
                        "ip_type": "ipv4"
                    }
                },
                {
                    "name": self.log_name()+":if1",
                    "role": "experimental",
                    "mac": self.alt_mac
                }
            ],
            "cmc": {
                "name": self.log_name()+":cm",
                "mac": "02:00:00:00:00:"+self.phy_str(),
                "ip": {
                    "address": "192.168.1.{}".format(self.log_num),
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

    def nagios_host_cfg_subnet(self, sn_ip, sn_name):
        log_name=self.log_name()
        phy_str=self.phy_str()
        sn_ip=sn_ip
        sn_name=sn_name
### NOTE: format uses { } already so for inserting a { or } we need to double them
        return """define host {{
use fit-node
host_name {log_name}-{sn_name}
address 192.168.{sn_ip}.{phy_str}
check_command my_ping
}}
""".format(**locals())

    def nagios_host_cfg(self):
        return "".join([self.nagios_host_cfg_subnet(i,n) for (i,n) in self.subnets])

########################################
class Nodes(OrderedDict):
    """
    a repository of known nodes, indexed by physical number
    """
    def __init__(self, csv_filename, out_basename, verbose):
        OrderedDict.__init__(self)
        self.csv_filename = csv_filename
        self.out_basename = out_basename
        self.verbose = verbose

    def load(self):
        with open(self.csv_filename, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            for lineno, line in enumerate(reader):
                try:
                    phy_num = int (line[1])
                    log_num = int (line[3])
                    # discard nodes that are not on-site
                    if not log_num:
                        print "Ignoring physical node {phy_num} - not deployed".format(phy_num)
                        continue
                    mac = line[5]
                    match = mac_regexp.match(mac)
                    if match:
                        prefix, last = match.group('prefix', 'last')
                        byte = int (last, base=16)
                        alt_last = str(byte-1)
                        alt_mac = prefix+alt_last
                        self[phy_num] = Node(phy_num, log_num, mac, alt_mac)
                    else:
                        print lineno,'non-mac',mac
                except Exception as e:
                    print 'skipping line',lineno,line
                    if self.verbose:
                        import traceback
                        traceback.print_exc()
    
    def write_json (self):
        out_filename = self.out_basename+".json"
        with open (out_filename, 'w') as jsonfile:
            json_models = [ node.json_model() for node in self.itervalues() ]
            json.dump (json_models, jsonfile)
    
        print ("(Over)wrote {out_filename} from {self.csv_filename}".format(**locals()))


    def write_nagios(self):
        out_filename = self.out_basename+"-nagios-nodes.cfg"
        with open(out_filename, 'w') as nagiosfile:
            for node in self.values():
                nagiosfile.write(node.nagios_host_cfg())
        print ("(Over)wrote {out_filename} from {self.csv_filename}".format(**locals()))
        
########################################        
def main():
    parser = ArgumentParser()
    parser.add_argument("-v", "--verbose")
    parser.add_argument("-o", "--output", default=None)
    parser.add_argument("input", nargs='?', default='fit.csv')
    args = parser.parse_args()

    nodes = Nodes(args.input, args.output or args.input.replace(".csv",""), args.verbose)
    nodes.load()

    nodes.write_json()
    nodes.write_nagios()

    return 0

if __name__ == '__main__':
    exit(main())
