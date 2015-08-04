#!/usr/bin/env python3

import json
import sys
import os


def join_node_results():
    """
    help
    """
    path = '/'
    files = ['multiple_results.txt', 'alive_results.txt', 'reset_results.txt', 'load_results.txt']

    node_status = {}
    
    file = open("load_results.txt", "r")
    data = json.load(file)
    file.close()

    return data

def export_node_status():
    """
    help
    """

    join_node_results()

    nodes_status = join_node_results()

    with open('markdown/node_status.json', 'w') as output:
      json.dump(nodes_status, output)


def main():

    export_node_status()
   
if __name__ == '__main__':
    main()