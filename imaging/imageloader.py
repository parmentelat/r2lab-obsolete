import asyncio
try:
    from asyncio import ensure_future
except:
    from asyncio import async as ensure_future

class ImageLoader:

    def __init__(self, cmcs, timeout, idle):
        """
        input argument is a list of CMC objects
        timeout is the amount of time reasonable for the slowest node to come back on telnet
        idle is the time after a reset during which there is no need to try the nodes
        """
        self.cmcs = cmcs
        self.timeout = timeout
        self.idle = idle
        # xxx arm signal so we can clean up the nextboot area
        # signal(xxx, ...)

    # this is not a co routine
    def stage1(self):
        """
        reset, and wait for everyone to be back on telnet
        """

        # XXX not tested at all..
        @asyncio.coroutine
        def stage1_cmc(cmc):
            yield from cmc.manage_nextboot_symlink('frisbee')
            yield from cmc.ensure_reset()
            yield from asyncio.sleep(self.idle)
            yield from cmc.wait_for_telnet()
            
        loop = asyncio.get_event_loop()
        tasks = [ensure_future(stage1_cmc(cmc)) for cmc in self.cmcs]
        loop.run_until_complete(asyncio.wait(tasks, timeout=self.timeout))
        loop.stop()

    def stage2(self):
        print("stage2 NYI")

    def cleanup(self):
        """
        Remove nextboot symlinks for all nodes in this selection
        """
        loop = asyncio.get_event_loop()
        tasks = [ ensure_future(cmc.manage_nextboot_symlink('reset')) for cmc in self.cmcs ]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.stop()

    def reset(self):
        """
        reset all nodes in this selection
        """
        loop = asyncio.get_event_loop()
        tasks = [ ensure_future(cmc.ensure_reset()) for cmc in self.cmcs ]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.stop()

    def epilogue(self):
        asyncio.get_event_loop().close()
