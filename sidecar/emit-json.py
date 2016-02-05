#!/usr/bin/env python -i
from __future__ import print_function

import json
from socketIO_client import SocketIO, LoggingNamespace

def io_callback(*args, **kwds):
    print('on socketIO response', *args, **kwds)

hostname = 'r2lab.inria.fr'
port = 443

print("Run this script with python -i")
socketio = None

def i(hostname=hostname, port=port):
    global socketio
    socketio = SocketIO(hostname, port, LoggingNamespace)

i()
print("""---
soketio connected to {}:{}""".format(hostname, port))
print("""---
Run i('localhost', 443) e.g. to create another connection""")


def e(infos):
    # can work only one dict -> wrap it in a list
    if isinstance(infos, dict):
        infos = [infos]
    socketio.emit('chan:status', json.dumps(infos), io_callback)

print("Run e({'id':4, 'cmc_on_off': 'on'}) to send a message")

def a(id, info):
    info['id'] = id
    e(info)
    
print("Run a(4, {'cmc_on_off': 'off'}) to send a message about a specific node")

