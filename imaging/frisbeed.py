import asyncio

from logger import logger

class Frisbeed:
    def __init__(self, image):
        self.subprocess = None
        self.image = image
    
    @asyncio.coroutine
    def start(self):
        """
        Start a frisbeed instance
        returns a tuple multicast_address, port_number
        """
        from config import the_config
        server = the_config.value('frisbee', 'server')
        server_options = the_config.value('frisbee', 'server_options')
        # this one should probably be computed if no value is set in the config
        # or maybe also let admins define the local interface name (like 'control' or 'eth0')
        local_ip = the_config.local_control_ip()
        # in Mibps
        bandwidth = int(the_config.value('networking', 'bandwidth')) * 2**20
        # should use default.ndz if not provided
        command_common = [
            server, "-i", local_ip, "-W", str(bandwidth), self.image
            ]
        # add configured extra options
        command_common += server_options.split()

        nb_attempts = int(the_config.value('networking', 'pattern_size'))
        pat_ip   = the_config.value('networking', 'pattern_multicast')
        pat_port = the_config.value('networking', 'pattern_port')
        for i in range(1, nb_attempts+1):
            pat = str(i)
            multicast_group = pat_ip.replace('*', pat)
            multicast_port = str(eval(pat_port.replace('*', pat)))
            command = command_common + [
                "-m", multicast_group, "-p", multicast_port,
                ]
            self.subprocess = yield from asyncio.create_subprocess_exec(
                *command,
                stdout = asyncio.subprocess.PIPE,
                stderr = asyncio.subprocess.STDOUT
                )
            yield from asyncio.sleep(1)
            # after such a short time, frisbeed should not have returned yet
            # if is has, we try our luck on another couple (ip, port)
            command_line = " ".join(command)
            if self.subprocess.returncode is None:
                logger.info("started frisbeed: {}".format(command_line))
                return multicast_group, multicast_port
            else:
                logger.info("failed to start frisbeed with {}".format(command_line))


    @asyncio.coroutine
    def stop(self):
        self.subprocess.kill()
        self.subprocess = None
        logger.info("frisbeed stopped")
        pass
