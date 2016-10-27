#!/usr/bin/env python3

import random
import json
import time

from argparse import ArgumentParser
from socketIO_client import SocketIO, LoggingNamespace

# in seconds
default_cycle = 1
default_runs = 0
default_socket_io_url = "ws://localhost:443/"

node_ids = range(1, 38)
default_max_nodes_impacted = 10

######## helper to create float ranges
def drange(start, stop, step):
    result = []
    r = start
    while r < stop:
        result.append(r)
        r += step
    return result

wlan_rates_range = drange(0., 20. * 10**6, 6. * 10**5)

######## valid values for initializing
nodes_field_possible_values = {
    'available' : [ None, 'ko'] + 3*['ok'],
    'cmc_on_off' : [ 'fail' ] + 3 * [ 'on', 'off' ],
    'control_ping' : [ 'on', 'off' ],
    'control_ssh' : ['on', 'off'],
    'os_release' : [ 'fedora-21', 'ubuntu-15.04', 'other', ],
    'gnuradio_release' : ['3.7.10', '', None],
    'uname' : [ 'foo', '4.2.300-generic' ],
    'image_radical' : [ 'ubuntu-15.04', 'oai-scrambler', '', None ],
    'usrp_type' : 12 * [ None ] + [ 'b210', 'n210', 'usrp1', 'usrp2'],
    'usrp_on_off' : 3 * ['on'] + ['off'],
#    'wlan0_rx_rate' : wlan_rates_range,
#    'wlan0_tx_rate' : wlan_rates_range,
#    'wlan1_rx_rate' : wlan_rates_range,
#    'wlan1_tx_rate' : wlan_rates_range,
}

phones_field_possible_values = {
    'wifi_on_off' : [ 'on', 'off' ],
    'airplane_mode' : [ 'on', 'off'],
    }

####################    
def random_ids(max_nodes_impacted):
    how_many = random.randint(1, max_nodes_impacted)
    return [ random.choice(node_ids) for i in range(how_many)]

# heuristics to avoid too inconsistent data
def normalize_status(node_info):
    # None means do not mention this key at all
    none_keys = { k for k in node_info if node_info[k] is None }
    for k in none_keys:
        del node_info[k]
    # avoid producing too inconsistent data
    if 'control_ssh' in node_info and node_info['control_ssh'] != 'off':
        node_info.update({'cmc_on_off' : 'on',
                          'control_ping' : 'on',
                      })
    return node_info

def random_node_status(id, index=0):
    # for testing incomplete news on the livemap side
    # we expose one or the other or both
    # however the default always expose the full monty
    node_info = { 'id' : id }
    # fill node_info with all known keys
    node_info.update( { field : random.choice(values) 
                       for field, values in nodes_field_possible_values.items() })
    # make sure this is mostly consistent
    normalize_status(node_info)
    # index == 0 means we need a complete record
    # otherwise let's remove some
    items_to_remove = index % len(nodes_field_possible_values)
    keys_to_remove = random.sample(nodes_field_possible_values.keys(), items_to_remove)
    for field in keys_to_remove:
        if field in node_info:
            del node_info[field]
    return node_info

def random_phone_status(id):
    phone_info = { 'id' : id }
    # fill phone_info with all known keys
    phone_info.update( { field : random.choice(values) 
                       for field, values in phones_field_possible_values.items() })
    return phone_info

# too lazy to get this properly (need to turn off server auth)
leases_url = "https://faraday.inria.fr:12346/resources/leases";
leases_file = "LEASES"

def get_leases():
    try:
        with open(leases_file) as input:
            string = input.read()
            obj = json.loads(string)
            resources = obj['resource_response']['resources']
            return resources
    except:
        print("WARNING: unable to read leases file {} - not sending leases".format(leases_file))
        return []

def main():
    parser = ArgumentParser()
    parser.add_argument('-c', '--cycle', dest='cycle', default=default_cycle,
                        type=float,
                        help="Cycle duration in seconds (default={})".format(default_cycle))
    parser.add_argument('-r', '--runs', dest='runs', default=default_runs,
                        type=int,
                        help="How many runs (default={}; 0 means forever)".format(default_runs))
    parser.add_argument('-n', '--nodes', dest='max_nodes_impacted', default=default_max_nodes_impacted,
                        type=int,
                        help="Maximum number of nodes impacted by each cycle")
    parser.add_argument('-l', '--live', dest='live', action='store_true', default=False,
                        help="If set, only rx/tx data are animated")
    parser.add_argument('-p', '--phone-cycle', default=5, type=int,
                        help='send a random phone status every n cycles')
    parser.add_argument('-s', '--socket-io-url', action='store', default=default_socket_io_url,
                        help="""Sends status data to this ws URL using socketio - use something like {}""".format(default_socket_io_url))
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    args = parser.parse_args()

    cycle = args.cycle

    if args.live:
        to_remove = [ k for k in field_possible_values if 'rx' not in k and 'tx' not in k]
        for k in to_remove:
            del field_possible_values[k]

    if args.verbose:
        print("Using cycle {}s".format(cycle))

    from urllib.parse import urlparse
    try:
        hostname, port = urlparse(args.socket_io_url).netloc.split(':')
        port = int(port)
        if args.verbose:
            print("Sending to sidecar at {hostname} on {port}".format(**locals()))
    except:
        print("Could not parse websocket URL {}".format(args.socket_io_url))
        import traceback
        traceback.print_exc()
        exit(1)
        
    socketIO = SocketIO(hostname, port, LoggingNamespace)
    def io_callback(*args, **kwds): print('on socketIO response', *args, **kwds)

    counter = 0
    while True:
        news_infos = [ random_node_status(id, index)
                       for index, id in enumerate(random_ids(args.max_nodes_impacted)) ]
        if args.verbose:
            print("{} -- on {} nodes (id, len(fields)) : {}"
                  .format(counter, len(news_infos),
                          [ (info['id'], len(info)-1) for info in news_infos]))
            print(news_infos[0])
        socketIO.emit('info:nodes', json.dumps(news_infos), io_callback)

        # only one phone
        if counter % args.phone_cycle == 0:
            phone_infos = [ random_phone_status(id) for id in [1]]
            if args.verbose:
                print("phone: emitting {}".format(phone_infos[0]))
            socketIO.emit('info:phones', json.dumps(phone_infos), io_callback)

        leases = get_leases()
        if leases:
            socketIO.emit('info:leases', json.dumps(leases), io_callback)
        counter += 1
        if args.runs and counter >= args.runs:
            break
        time.sleep(cycle)

        
    # xxx should probably clean up the socket io client
    pass

if __name__ == '__main__':
    main()
