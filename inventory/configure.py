#!/usr/bin/env python3

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
import json
# as of June 2015, we don't use a csv file as input but r2lab.map instead
#import csv

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
        self.mac = mac.lower()
        self.alt_mac = alt_mac.lower()

    def phy_str0(self):
        "physical number on 2 chars as a str"
        return "{:02d}".format(self.phy_num)
    def phy_name(self):
        "external name based on physical number, like phy33"
        return "phy"+self.phy_str0()

    def log_str0(self):
        "logical number on 2 chars as a str"
        return "{:02d}".format(self.log_num)
    def log_name(self, prefix='fit'):
        "external name based on logical number, like fit33"
        return "{prefix}{:02d}".format(self.log_num, prefix=prefix)

    subnets = ( (1, 'reboot'), (2, 'data'), (3, 'control') )

    @staticmethod
    def degree_to_float(tuple):
        deg, min, sec = tuple
        return deg + min/60 + sec/3600
        
    # all nodes get the same position for now
    def latitude(self):
        return self.degree_to_float( (7, 4, 9.30) )
    def longitude(self):
        return self.degree_to_float( (43, 36, 52.30) )
    
    def json_model(self):
        domain = 'r2lab'
        return OrderedDict (
            cmc_attributes = {
                "name": "{}:cm".format(self.log_name()),
                "mac": "02:00:00:00:00:{}".format(self.phy_str0()),
                "ip_attributes": {
                    # we cannot change the IP address of the CMC ...
                    "address": "192.168.1.{}".format(self.phy_num),
                    "netmask": "255.255.255.0",
                    "ip_type": "ipv4"
                }
            },
            cpus_attributes = [ {
                "cpu_type": "Intel 4770kI7",
                "cores": 4,
                "threads": 8,
                "cache_l1": "n/a",
                "cache_l2": "8 Mb"
            }],
            domain = 'omf:r2lab',
            gateway = 'faraday.inria.fr',
            hardware_type = "PC-Icarus",
            hd_capacity = "240 GB",
            hostname = self.phy_name(),
            interfaces_attributes = [
                {
                    "role": "control",
                    "name": "{}:if0".format(self.log_name()),
                    "mac": self.mac,
                    "ips_attributes": [{
                        "address": "192.168.3.{}".format(self.log_num),
                        "netmask": "255.255.255.0",
                        "ip_type": "ipv4"
                    }],
                },
                {
                    "role": "experimental",
                    "name": "{}:if1".format(self.log_name()),
                    "mac": self.alt_mac
                },
            ],
            # xxx needs to be made much more accurate
            location_attributes = {
                'altitude' : 145,
                'latitude' : self.latitude(),
                'longitude' : self.longitude(),
                },
            name = self.log_name(),
            ram = "8 GB",
            ram_type = "DIMM Synchronous",
            urn = "urn:publicid:IDN+omf:r2lab+node+{}".format(self.log_name()),
        )

    def dnsmasq_conf(self):
        control="dhcp-host=net:control,{},{},192.168.3.{}\n".\
            format(self.mac, self.log_name('fit'), self.log_num)
        data="dhcp-host=net:data,{},{}-exp,192.168.2.{}\n".\
            format(self.alt_mac, self.log_name('data-'), self.log_num)
        return control+data


    def hosts_conf_sn(self, sn_ip, sn_name):
        # we cannot change the IP address of the CMC card, so this one is physical
        is_cmc = (sn_ip == self.subnets[0][0])
        num = self.phy_num if is_cmc else self.log_num
        hostnames = self.log_name(prefix=sn_name+'-')
        if sn_name == 'control':
            hostnames += " " + self.log_name()
        return "192.168.{sn_ip}.{num}\t{hostnames}\n".format(**locals())

    def hosts_conf(self):
        return "".join([self.hosts_conf_sn(i,n) for (i,n) in self.subnets])

    def nagios_host_cfg_sn(self, sn_ip, sn_name):
        log_name=self.log_name()
        sn_ip=sn_ip
        sn_name=sn_name
        # we cannot change the IP address of the CMC card, so this one is physical
        is_cmc = (sn_ip == self.subnets[0][0])
        num = self.phy_num if is_cmc else self.log_num

        ### NOTE: format uses { } already so for inserting a { or } we need to double them
        result = """define host {{
use fit-node
host_name {log_name}-{sn_name}
address 192.168.{sn_ip}.{num}
check_command my_ping
}}
""".format(**locals())

        if is_cmc:
            result += """ define service{{
use my-service
host_name {log_name}-{sn_name}
service_description  ON/OFF
check_command on_off
}}
""".format(**locals())

        return result

    def nagios_host_cfg(self):
        return "".join([self.nagios_host_cfg_sn(i,n) for (i,n) in self.subnets])

    def nagios_groups(self):
        "returns a 3-list with the hostnames for the 3 subnets"
        log_name=self.log_name()
        return [ "{log_name}-{sn_name}".format(log_name=log_name, sn_name=sn_name)
                 for i, sn_name in self.subnets ]
    
    def diana_db(self):
        ip = "138.96.119.{}".format(100+self.phy_num)
        hostname=self.phy_name()
        mac1=self.mac
        mac2=self.alt_mac
        return "{ip} h={hostname} {mac1} o=alt:{mac2}\n".format(**locals())

########################################
hosts_header="""# Do not edit this file directly
# it is generated by configure.py

127.0.0.1	localhost

# The following lines are desirable for IPv6 capable hosts
::1     localhost ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters

192.168.1.100   faraday1 faraday-reboot
192.168.2.100   faraday2 faraday-data
192.168.3.100   faraday3 faraday-control
192.168.4.100   faraday4
192.168.4.101   switch-reboot
192.168.4.102   switch-data
192.168.4.103   switch-control
192.168.4.104   switch-c007
192.168.4.36    wlab36

##########
"""

dnsmasq_header="""# Do not edit this file directly
# it is generated by configure.py

### the network switches are now configures statically
# we keep this for the record for their MAC address
#
# CONFIRMED to be the main data switch
#dhcp-host=f8:b1:56:33:50:ad,switch-data,192.168.3.102
# CONFIRMED control
#dhcp-host=f8:b1:56:42:51:32,switch-control,192.168.3.103
# CONFIRMED reboot
#dhcp-host=f8:b1:56:42:52:a5,switch-reboot,192.168.3.101
# switch in C007 type 5524
#dhcp-host=d0:67:e5:d6:ae:fe,switch-c007,192.168.3.104

##########
"""

class Nodes(OrderedDict):
    """
    a repository of known nodes, indexed by physical number
    """
    def __init__(self, map_filename, out_basename, prep_lab, verbose):
        OrderedDict.__init__(self)
        self.map_filename = map_filename
        self.out_basename = out_basename
        self.prep_lab = prep_lab
        self.verbose = verbose

    # format of a .map file is straightforward
    # (1) first column is the pysical number written on the box (sticker)
    # (2) second column is its main mac address
    # (3) last column is its logical location where it is deployed in faraday
    # 
    # in regular mode, we hide nodes that are declared in preplab
    # in prep_lab mode we expose all nodes, ignore column 3 and use column 1 instead
    def load(self):
        f = self.map_filename
        with open(f, 'r') as mapfile:
            for lno, line in enumerate(mapfile):
                # ignore comments
                if line.startswith('#'):
                    continue
                tokens = line.split()
                if len(tokens) != 3:
                    print("{}:{}: expecting 3 tokens - ignored".format(f, lno))
                    continue
                # get node number
                try:
                    phy_num = int(tokens[0])
                except:
                    print("{}:{}: cannot read first integer".format(f, lno))
                    continue
                # get logical number
                if tokens[2].startswith('prep'):
                    log_num = 0
                else:
                    try:
                        log_num = int(tokens[2])
                    except:
                        print("{}:{}: cannot read last integer".format(f, lno))
                        continue
                if self.prep_lab:
                    log_num = phy_num
                # discard nodes that are not on-site
                if log_num <= 0:
                    print ("{}:{} - undeployed physical node {} - ignored"
                           .format(f, lno, phy_num))
                    continue
                mac = tokens[1]
                match = mac_regexp.match(mac)
                if match:
                    prefix, last = match.group('prefix', 'last')
                    byte = int (last, base=16)
                    alt_last = hex(byte-1)[2:]
                    alt_mac = prefix+alt_last
                    self[phy_num] = Node(phy_num, log_num, mac, alt_mac)
                else:
                    print ("{}:{} physical node {} ignored - wrong MAC".format(f, lno))
                    if self.verbose: print(">>",line)
    
    def keep_just_one(self):
        for k in self.keys()[1:]:
            del self[k]
        self.out_basename += ".small"

    def write_json(self):
        out_filename = self.out_basename+".json"
        with open (out_filename, 'w') as jsonfile:
            json_models = [ node.json_model() for node in self.values() ]
            json.dump (json_models, jsonfile, indent=2, separators=(',', ': '), sort_keys=True)
        print ("(Over)wrote {out_filename} from {self.map_filename}".format(**locals()))

    def write_dnsmasq(self):
        out_filename = self.out_basename+".dnsmasq"
        with open (out_filename, 'w') as dnsmasqfile:
            dnsmasqfile.write(dnsmasq_header)
            for node in self.values():
                dnsmasqfile.write(node.dnsmasq_conf())
        print ("(Over)wrote {out_filename} from {self.map_filename}".format(**locals()))

    def write_hosts(self):
        out_filename = self.out_basename+".hosts"
        with open (out_filename, 'w') as hostsfile:
            hostsfile.write(hosts_header)
            for node in self.values():
                hostsfile.write(node.hosts_conf())
        print ("(Over)wrote {out_filename} from {self.map_filename}".format(**locals()))
    

    def write_nagios(self):
        out_filename = self.out_basename+"-nagios-nodes.cfg"
        with open(out_filename, 'w') as nagiosfile:
            for node in self.values():
                nagiosfile.write(node.nagios_host_cfg())
        print ("(Over)wrote {out_filename} from {self.map_filename}".format(**locals()))

    def write_nagios_hostgroups(self):
        out_filename = self.out_basename+"-nagios-groups.cfg"
        nodes_groups = zip(*[ node.nagios_groups() for node in self.values() ])
        with open(out_filename, 'w') as nagiosfile:
            for (i, sn_name), list_names in zip(Node.subnets, nodes_groups):
                sn_members = ",".join(list_names)
                hostgroup = """
define hostgroup {{
hostgroup_name .{i}
alias {sn_name}
members {sn_members}
}}
""".format(**locals())
                nagiosfile.write(hostgroup)
        print ("(Over)wrote {out_filename} from {self.map_filename}".format(**locals()))


    def write_diana_db(self):
        out_filename = self.out_basename+"-diana.db"
        with open(out_filename, 'w') as nagiosfile:
            for node in self.values():
                nagiosfile.write(node.diana_db())
        print ("(Over)wrote {out_filename} from {self.map_filename}".format(**locals()))
        
########################################        
def main():
    parser = ArgumentParser()
    parser.add_argument("-v", "--verbose", action='store_true', default=False)
    parser.add_argument("-o", "--output", default=None)
    parser.add_argument("-p", "--prep-lab", action='store_true', default=False,
                        help="In prep-lab mode, all nodes are exposed, regardless of the 'slot' column")
    parser.add_argument("-s", "--small", action='store_true', default=False,
                        help="force output of only one node")
    parser.add_argument("input", nargs='?', default='r2lab.map')
    args = parser.parse_args()

    if args.output:
        output = args.output
    elif not args.prep_lab:
        output =  args.input.replace(".map","")
    else:
        output =  args.input.replace(".map","-prep")

    nodes = Nodes(args.input, output, args.prep_lab, args.verbose)
    nodes.load()

    # this is a debugging trick so that we generate only one node,
    # given how loading the JSON file is slow
    if args.small:
        nodes.keep_just_one()

    nodes.write_json()
    nodes.write_dnsmasq()
    nodes.write_hosts()
    if not args.prep_lab:
        nodes.write_nagios()
        nodes.write_nagios_hostgroups()
        nodes.write_diana_db()

    return 0

if __name__ == '__main__':
    exit(main())
