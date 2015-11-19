import asyncio

import util
from monitor import Monitor
from frisbeed import Frisbeed

class ImageLoader:

    def __init__(self, cmcs, message_bus, image):
        self.cmcs = cmcs
        self.message_bus = message_bus
        self.image = image
        # xxx arm signal so we can clean up the nextboot area ...
        # as a matter of fact this should be done much earlier in the process...
        # signal(xxx, ...)
        self.monitor = Monitor(message_bus)

    @asyncio.coroutine
    def stage1(self):
        """
        redirect nextboot symlink to frisbee, and reset all nodes
        """

        @asyncio.coroutine
        def stage1_cmc(cmc):
            yield from asyncio.gather(cmc.manage_nextboot_symlink('frisbee'),
                                      cmc.ensure_reset())
            from config import the_config
            idle = the_config.value('nodes', 'idle_after_reset')
            yield from self.message_bus.put("idling for {}s".format(idle))
            yield from asyncio.sleep(idle)
            
        yield from asyncio.gather(*[stage1_cmc(cmc) for cmc in self.cmcs])

    @asyncio.coroutine
    def start_frisbeed(self):
        self.frisbeed = Frisbeed(self.image)
        ip_port = yield from self.frisbeed.start()
        return ip_port

    @asyncio.coroutine
    def stop_frisbeed(self):
        yield from self.frisbeed.stop()

    @asyncio.coroutine
    def stage2(self):
        """
        wait for all nodes to be telnet-friendly
        then run frisbee in all of them
        """
#        yield from asyncio.gather(self.start_frisbeed(),
#                                  *[cmc.stage2() for cmc in self.cmcs])
        ip, port = yield from self.start_frisbeed()
        yield from asyncio.gather(*[cmc.stage2(ip, port) for cmc in self.cmcs])

        print("stage2 half done")
        yield from self.stop_frisbeed()

    @asyncio.coroutine
    def nextboot_cleanup(self):
        """
        Remove nextboot symlinks for all nodes in this selection
        so next boot will be off the harddrive
        """
        yield from asyncio.gather(*[cmc.manage_nextboot_symlink('harddrive') for cmc in self.cmcs])

    @asyncio.coroutine
    def reset(self):
        """
        reset all nodes in this selection
        """
        print("NOT RESETTING!")
# TMP        yield from asyncio.gather(*[cmc.ensure_reset() for cmc in self.cmcs])

    @asyncio.coroutine
    def run(self):
        print("SKIPPING stage1")
# TMP       yield from self.stage1()
        yield from self.stage2()
        yield from asyncio.gather(self.nextboot_cleanup(),
                                  self.reset())
        yield from self.monitor.stop()

    def main(self):
        t1 = util.self_manage(self.run())
        t2 = util.self_manage(self.monitor.run())
        asyncio.get_event_loop().run_until_complete(asyncio.wait([t1, t2]))
