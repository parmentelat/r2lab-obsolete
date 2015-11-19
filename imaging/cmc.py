#/usr/bin/env python3

import os.path

import asyncio
import aiohttp

from frisbee import FrisbeeConnection

class CMC:

    """
    This class allows to talk to a CMC using http, essentially
    for probing status and sending other commands
    Because it is designed to be used asynchroneously,
    methods return the object itself, with the result stored as an attribute
    i.e. self.get_status() return self with self.status set
    """
    def __init__(self, hostname, message_bus):
        self.hostname = hostname
        self.message_bus = message_bus
        self.status = None
        self.action = None
        self.mac = None

    def __repr__(self):
        return "<CMC {}>".format(self.hostname)

    def is_known(self):
        return self.control_mac_address() is not None

    def control_mac_address(self):
        from inventory import the_inventory
        return the_inventory.attached_hostname_info(self.hostname, 'control', 'mac')

    def control_ip_address(self):
        from inventory import the_inventory
        return the_inventory.attached_hostname_info(self.hostname, 'control', 'ip')

    def control_hostname(self):
        from inventory import the_inventory
        return the_inventory.attached_hostname_info(self.hostname, 'control', 'hostname')

    @asyncio.coroutine
    def get_status(self):
        """
        return value stored in self.status
        either 'on' or 'off', or None if something wrong is going on
        """
        url = "http://{}/status".format(self.hostname)
        try:
            client_response = yield from aiohttp.get(url)
        except Exception as e:
            self.status = None
            return self
        try:
            text = yield from client_response.text()
            self.status = text.strip()
            return self
        except Exception as e:
            self.status = None
            return self

    @asyncio.coroutine
    def get_status_verbose(self):
        yield from self.get_status()
        print("{}:{}".format(self.hostname, self.status))

    ####################
    # what status to expect after a message is sent
    expected_map = {
        'on' : 'on',
        'reset' : 'on',
        'off' : 'off'
    }
        
    @asyncio.coroutine
    def send_action(self, message="on", check = False, check_delay=1.):
        """
        Actually send action message like 'on', 'off' or 'reset'
        if check is True, waits for check_delay seconds before checking again that
        the status is what is expected, i.e.
        | message  | expected |
        |----------|----------|
        | on,reset | on       |
        | off      | off      |

        return value stored in self.action
        * if check is false
          * True if request can be sent and returns 'ok', or None if something goes wrong
        * otherwise:
          * True to indicate that the node is correctly in 'on' mode after checking
          * False to indicate that the node is 'off' after checking
          * None if something goes wrong
        """
        url = "http://{}/{}".format(self.hostname, message)
        try:
            client_response = yield from aiohttp.get(url)
        except Exception as e:
            self.action = None
            return self

        try:
            text = yield from client_response.text()
            ok = text.strip() == 'ok'
        except Exception as e:
            self.action = None
            return self
    
        if not check:
            self.action = ok
            return self
        else:
            yield from asyncio.sleep(check_delay)
            yield from self.get_status()
            self.action = self.status == self.expected_map[message]
            return self

    ####################
    message_to_reset_map = { 'on' : 'reset', 'off' : 'on' }

    @asyncio.coroutine
    def ensure_reset(self):
        if self.status is None:
            yield from self.get_status()
        if self.status not in self.message_to_reset_map:
            yield from self.message_bus.put("Cannot get status from CMC {}".format(self.hostname))
        message_to_send = self.message_to_reset_map[self.status]
        yield from self.message_bus.put("Sending message '{}' to CMC {}".format(message_to_send, self.hostname))
        yield from self.send_action(message_to_send, check=True)
        if not self.action:
            yield from self.message_bus.put("Failed to send message {} to CMC {}".format(message_to_send, self.hostname))


    ##########
    @asyncio.coroutine
    def manage_nextboot_symlink(self, action):
        """
        Messes with the symlink in /tftpboot/pxelinux.cfg/
        Depending on 'action'
        * 'cleanup' or 'harddrive' : clear the symlink corresponding to this CMC
        * 'frisbee' : define a symlink so that next boot will run the frisbee image
        see imaging.conf for configurable options
        """

        from config import the_config
        root = the_config.value('pxelinux', 'config_dir')
        frisbee = the_config.value('pxelinux', 'frisbee_image')
        
        # of the form 01-00-03-1d-0e-03-53
        mylink = "01-" + self.control_mac_address().replace(':', '-')
        source = os.path.join(root, mylink)
        dest = os.path.join(root, frisbee)

        if action in ('cleanup', 'harddrive'):
            if os.path.exists(source):
                os.remove(source)
        elif action in ('frisbee'):
            if os.path.exists(source):
                os.remove(source)
            os.symlink(frisbee, source)
        else:
            yield from self.message_bus.put("manage_nextboot_symlink : unknown action {}".format(action))

    ##########
    @asyncio.coroutine
    def wait_for_telnet(self):
        from inventory import the_inventory
        ip = self.control_ip_address()
        self.frisbee = FrisbeeConnection(ip, self.message_bus)
        yield from self.frisbee.wait()
        print("telnet on {} : ready = {}".format(ip, self.frisbee.is_ready()))
        
    @asyncio.coroutine
    def stage2(self, ip , port):
        yield from self.wait_for_telnet()
        yield from self.frisbee.run_client(ip, port)
