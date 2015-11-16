#/usr/bin/env python3

import asyncio
import aiohttp

class CMC:
    """
    This class allows to talk to a CMC using http, essentially
    for probing status and sending other commands
    Because it is designed to be used asynchroneously,
    methods return the object itself, with the result stored as an attribute
    i.e. self.get_status() return self with self.status set
    """
    def __init__(self, hostname):
        self.hostname = hostname
        self.status = None
        self.action = None

    @asyncio.coroutine
    def get_status(self):
        """
        return value stored in self.status
        either 'on' or 'off', or None if something wrong is going on
        """
        url = "http://{}/status".format(self.hostname)
        try:
            client_response = yield from aiohttp.get(url)
#        except aiohttp.errors.ClientOSError as e:
        except Exception as e:
            #print("status - exception (1b) : {}".format(e))
            self.status = None
            return self
        try:
            text = yield from client_response.text()
            self.status = text.strip()
            return self
        except Exception as e:
            #print("status - exception (2) : {}".format(e))
            self.status = None
            return self

    @asyncio.coroutine
    def get_status_verbose(self):
        yield from self.get_status()
        print("{}:{}".format(self.hostname, self.status))

    ####################
    expected_map = { 'on' : 'on',
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
            print("Cannot get status from CMC {}".format(self.hostname))
        message_to_send = self.message_to_reset_map[self.status]
        print("Sending message '{}' to CMC {}".format(message_to_send, self.hostname))
        yield from self.send_action(message_to_send, check=True)
        if not self.action:
            print("Failed to send message {} to CMC {}".format(message_to_send, self.hostname))
