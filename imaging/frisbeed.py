import asyncio

class Frisbeed:
    def __init__(self, image):
        self.subprocess = None
        self.image = image
    
    @asyncio.coroutine
    def start(self):
        from config import the_config
        server = the_config.value('frisbee', 'server')
        # this one should probably be computed if no value is set in the config
        # or maybe also let admins define the local interface name (like 'control' or 'eth0')
        local_ip = the_config.server_ip()
        multicast_group = the_config.value('networking', 'multicast_group')
        port = the_config.available_frisbee_port()
        # in Mibps
        bandwidth = int(the_config.value('networking', 'bandwidth')) * 2**20
        # should use default.ndz if not provided
        local_command = [
            server, "-i", local_ip, "-m", multicast_group, "-p", str(port), "-W", str(bandwidth), self.image
            ]
        print("Starting frisbeed with {}".format(" ".join(local_command)))
        self.subprocess = yield from asyncio.create_subprocess_exec(
            *local_command,
            stdout = asyncio.subprocess.PIPE,
            stderr = asyncio.subprocess.STDOUT
            )
        # we don't wait for it yet, as this will come only when all the clients are done

    @asyncio.coroutine
    def stop(self):
        self.subprocess.kill()
        self.subprocess = None
        print("frisbeed stopped")
        pass
