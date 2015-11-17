import os

import configparser

locations = [
    "./imaging.conf",
    os.path.expanduser("~/.imaging.conf"),
    "/etc/imaging.conf",
    ]

def config_parser():
    config = configparser.ConfigParser()
    for location in locations:
        if os.path.exists(location):
            config.read(location)
    return config

Config = config_parser()
