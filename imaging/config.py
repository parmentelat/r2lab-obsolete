import os

import configparser
import guessip

# location, mandatory
locations = [
    ("/etc/imaging.conf", True),
    (os.path.expanduser("~/.imaging.conf"), False),
    ("./imaging.conf", False),
]

class ConfigException(Exception):
    pass

class ImagingConfig:

    def __init__(self):
        self.config = configparser.ConfigParser()
        for location, mandatory in locations:
            if os.path.exists(location):
                self.config.read(location)
            elif mandatory:
                raise ConfigException("Missing mandatory config file {}".format(location))

    def get_or_raise(self, dict, section, key):
        res = dict.get(key, None)
        if res is not None:
            return res
        else:
            raise ConfigException("imaging config: missing entry section={} key={}"
                                  .format(section, key))

    def value(self, section, flag, hostname=None):
        if section not in self.config:
            raise ConfigException("No such section {} in config".format(section))
        config_section = self.config[section]
        if hostname:
            return config_section.get("{flag}:{hostname}".format(**locals()), None) \
                or self.get_or_raise(config_section, section, flag)
        else:
            return self.get_or_raise(config_section, section, flag)
        
    # for now
    # the foreseeable tricky part is, this should be a coroutine..
    def available_frisbee_port(self):
        return self.value('networking', 'port')

    # maybe this one too
    def local_control_ip(self):
        # if specified in the config file, then use that
        if 'networking' in self.config and 'local_control_ip' in self.config['networking']:
            return self.config['networking']['local_control_ip']
        # but otherwise guess it
        from inventory import the_inventory
        from guessip import local_ip_on_same_network_as
        ip, prefixlen = local_ip_on_same_network_as(the_inventory.one_control_interface())
        return ip

the_config = ImagingConfig()
