import asyncio

from monitor import Monitor

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
            yield from cmc.manage_nextboot_symlink('frisbee')
            yield from cmc.ensure_reset()
            yield from self.message_bus.put("idling for {}s".format(self.idle))
            yield from asyncio.sleep(self.idle)
            
        yield from asyncio.gather(*[stage1_cmc(cmc) for cmc in self.cmcs])

    @asyncio.coroutine
    def stage2(self):
        """
        wait for all nodes to be telnet-friendly
        then run frisbee in all of them
        """
        @asyncio.coroutine
        def stage2_cmc(cmc):
            yield from cmc.wait_for_telnet()
        
        yield from asyncio.gather(*[stage2_cmc(cmc) for cmc in self.cmcs])

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
