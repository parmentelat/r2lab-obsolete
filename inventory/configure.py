#!/usr/bin/env python


class Node(object):
    def __init__(self, phy_num, log_num, mac, alt_mac):
        self.phy_num = phy_num
        self.log_num = log_num
        self.mac = mac
        self.alt_mac = alt_mac

    def json_model(self):
        phy2 = "{:02d}".format(self.phy_num)
        log2 = "{:02d}".format(self.log_num)
        phyname = "phy"+phy2
        logname = "fit"+phy2
        domain = 'faraday'
        return {
            "name": phyname,
            "hostname": logname,
            "hardware_type": "PC-Icarus",
            "urn": "urn:publicid:IDN+omf:faraday+node+"+logname,
            "interfaces": [
                {
                    "name": logname+":if0",
                    "role": "control",
                    "mac": self.mac,
                    "ip": {
                        "address": "192.168.3.{}".format(self.log_num),
                        "netmask": "255.255.255.0",
                        "ip_type": "ipv4"
                    }
                },
                {
                    "name": logname+":if1",
                    "role": "experimental",
                    "mac": self.alt_mac
                }
            ],
            "cmc": {
                "name": logname+":cm",
                "mac": "02:00:00:00:00:"+phy2,
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

########################################
def write_json (input, output, verbose):
    with open(input, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        nodes = []
        for lineno, line in enumerate(reader):
            try:
                phy_num = int (line[1])
                log_num = int (line[3])
                mac = line[5]
                match = mac_regexp.match(mac)
                if match:
                    prefix, last = match.group('prefix', 'last')
                    byte = int (last, base=16)
                    alt_last = str(byte-1)
                    alt_mac = prefix+alt_last
                    nodes.append(Node(phy_num, log_num, mac, alt_mac))
                else:
                    print lineno,'non-mac',mac
            except Exception as e:
                print 'skipping line',lineno,line
                if verbose:
                    import traceback
                    traceback.print_exc()
    
        with open (output, 'w') as jsonfile:
            json_models = [ node.json_model() for node in nodes ]
            json.dump (json_models, jsonfile)

    print ("(Over)wrote {output} from {input}".format(**locals()))

########################################
import re
import csv
import json

from argparse import ArgumentParser

mac_regexp = re.compile ('(?P<prefix>([0-9A-Fa-f]{2}:){5})(?P<last>[0-9A-Fa-f]{2})')


def main():
    parser = ArgumentParser()
    parser.add_argument("-v", "--verbose")
    parser.add_argument("-o", "--output", default=None)
    parser.add_argument("input", type=str, default="fit.csv")
    args = parser.parse_args()

    out_basename = args.output or args.input.replace(".csv","")

    out_json = out_basename +".json"
    
    write_json (args.input, out_json, args.verbose)

    return 0

if __name__ == '__main__':
    exit(main())
