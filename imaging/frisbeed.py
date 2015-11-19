import asyncio

class Frisbeed:
    def __init__(self):
        self.subprocess = None
    
    @asyncio.coroutine
    def start(self):
        # xxx config
        bin = "/usr/sbin/frisbeed"
        # this one should probably be computed if no value is set in the config
        # or maybe also let admins define the local interface name (like 'control' or 'eth0')
        local_ip = "192.168.3.200"
        multicast_group = "234.5.6.7"
        port = 10000
        bandwidth = 90000000
        # should use default.ndz if not provided
        image = "/var/lib/omf-images-6/ubuntu-14.10-ext4-v01-root+base.ndz"
        local_command = [
            bin, "-i", local_ip, "-m", multicast_group, "-p", str(port), "-W", str(bandwidth), image
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
