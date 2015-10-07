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

from socketIO_client import SocketIO, LoggingNamespace

# globals
hostname = 'r2lab.inria.fr'
port = 443

# check if run as 'available.py' or 'unavailable.py'
import sys
available_value = 'ko' if 'un' in sys.argv[0] else 'ok'

# parse args
parser = ArgumentParser()
parser.add_argument("nodes", nargs='+', type=int)
args = parser.parse_args()

infos = [{'id': arg, 'available' : available_value} for arg in args.nodes]


socketio = SocketIO(hostname, port, LoggingNamespace)
print("Sending {infos} onto {hostname}:{port}".format(**locals()))
socketio.emit('r2lab-news', json.dumps(infos), None)




