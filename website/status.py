#!/usr/bin/env python3

import json
import sys
import os


def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dictionary
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def export_node_status():
    """
    help
    """

    path_read = ''
    path_save = 'markdown/'
    files = ['reset_results.txt', 'load_results.txt']

    for fl in files:
        file = open(path_read+fl, "r")
        data = file.read()
        file.close()

        file_name = fl.replace('.txt', '.json')
        with open(path_save+file_name, 'w') as output:
            json.dump(data, output)


def main():

    export_node_status()
   
if __name__ == '__main__':
    main()