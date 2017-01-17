#!/usr/bin/env python3

"""
This script emits messages to the sidecar server on faraday
to instruct it that some nodes are available or not
(use available.py or unavailable.py) 
"""

# xxx todo1 - if needed we could add options too to chose between available and unavailable
# xxx todo2 - more importantly we could consider talking to the OMF inventory on faraday
#             to maintain the same status over there


from argparse import ArgumentParser
import json
import traceback

from socketIO_client import SocketIO, LoggingNamespace

# globals
def_hostname = 'r2lab.inria.fr'
def_port = 999

glob_supported = {
    'node' : {
        '__range__': range(1, 38),
        'available' : ("on", "off"),
        'usrp_type' : ("b210", "n210", "usrp1", "usrp2"),
        },
    'phone' : {
        '__range__' : range(1, 2),
        'airplane_mode' : ("on", "off"),
        }
    }

def channel_name(type, prefix):
    return "{}:{}s".format(prefix, type)

def set_in_obj(socketio, type, channel, id, attribute, value):
    if id not in glob_supported[type]['__range__']:
        print("id {} out of range for type {}"
              .format(id, type))
        return
    if attribute not in glob_supported[type]:
        print("unknown attribute {} on type {}"
              .format(attribute, type))
        return
    if value not in glob_supported[type][attribute]:
        print("unknown value {} on attribute {}"
              .format(value, attribute))
        return
    infos = [{'id': id, attribute: value}]
    print("Sending {infos} on channel {channel}".format(**locals()))
    socketio.emit(channel, json.dumps(infos), None)
    

def main():
    parser = ArgumentParser()
    parser.add_argument("-t", "--type", choices=glob_supported.keys(), default="node",
                        help="Select one type of object to act on")
    parser.add_argument("set_triples", nargs='+',
                        metavar='node:attribute=value',
                        help="set value=attribute on given obj. id - additive")
    args = parser.parse_args()

    print("Opening socketio connection to {}:{}"
          .format(def_hostname, def_port))
    socketio = SocketIO(def_hostname, def_port, LoggingNamespace)

    channel = channel_name(args.type, "info")
    for set_triple in args.set_triples:
        try:
            id, rest = set_triple.split(':')
            id = int(id)
            attribute, value = rest.split('=')
            set_in_obj(socketio, args.type, channel, id, attribute, value)
        except Exception as e:
            traceback.print_exc()
            exit(1)
    
main()

