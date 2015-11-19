import os

import configparser

# location, mandatory
locations = [
    ("/etc/imaging.conf", True),
    (os.path.expanduser("~/.imaging.conf"), False),
    ("./imaging.conf", False),
]

class ImagingConfig:

    def __init__(self):
        self.config = configparser.ConfigParser()
        for location, mandatory in locations:
            if os.path.exists(location):
                self.config.read(location)
            elif mandatory:
# for devel                
#                raise Exception("Missing mandatory config file {}".format(location))
                print("WARNING: Missing mandatory config file {}".format(location))

    def value(self, section, flag, hostname=None):
        if section not in self.config:
            raise KeyError("No such section {} in config".format(section))
        config_section = self.config[section]
        if hostname:
            return config_section.get("{flag}:{hostname}".format(**locals()), None) \
                or config_section[flag]
        else:
            return config_section[flag]
        
    # for now
    # the foreseeable tricky part is, this should be a coroutine..
    def available_frisbee_port(self):
        return self.value('networking', 'port')
    # maybe this one too
    def server_ip(self):
        return self.value('networking', 'server_ip')

the_config = ImagingConfig()
