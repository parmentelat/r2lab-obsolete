import asyncio

from monitor import Monitor
from frisbeed import Frisbeed

class ImageLoader:

    def __init__(self, cmcs, message_bus, timeout, idle):
        """
        input argument is a list of CMC objects
        timeout is the amount of time reasonable for the slowest node to come back on telnet
        idle is the time after a reset during which there is no need to try the nodes
        """
        self.cmcs = cmcs
        self.message_bus = message_bus
        self.timeout = timeout
        self.idle = idle
        # xxx arm signal so we can clean up the nextboot area
        # signal(xxx, ...)
        self.monitor = Monitor(message_bus)

    @asyncio.coroutine
    def stage1(self):
        """
        redirect nextboot symlink to frisbee, and reset all nodes
        """

        # XXX not tested at all..
        @asyncio.coroutine
        def stage1_cmc(cmc):
            yield from asyncio.gather(cmc.manage_nextboot_symlink('frisbee'),
                                      cmc.ensure_reset())
            yield from self.message_bus.put("idling for {}s".format(self.idle))
            yield from asyncio.sleep(self.idle)
            
        yield from asyncio.gather(*[stage1_cmc(cmc) for cmc in self.cmcs])

    @asyncio.coroutine
    def start_frisbeed(self):
        self.frisbeed = Frisbeed()
        yield from self.frisbeed.start()

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
        yield from self.start_frisbeed()
        yield from asyncio.gather(*[cmc.stage2() for cmc in self.cmcs])

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
        t1 = asyncio.Task(self.run())
        t2 = asyncio.Task(self.monitor.run())
        asyncio.get_event_loop().run_until_complete(asyncio.wait([t1, t2]))
