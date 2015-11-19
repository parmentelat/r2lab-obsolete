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
            # this is now synchoneous
            cmc.manage_nextboot_symlink('frisbee')
            yield from cmc.ensure_reset()
            from config import the_config
            idle = int(the_config.value('nodes', 'idle_after_reset'))
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
        # start_frisbeed will return the ip+port to use 
        ip, port = yield from self.start_frisbeed()
        yield from asyncio.gather(*[cmc.stage2(ip, port) for cmc in self.cmcs])
        # we can now kill the server
        yield from self.stop_frisbeed()

    @asyncio.coroutine
    def stage3(self):
        # just reset all nodes for now
        # waiting for the nodes to come back under ssh could be another image-wait feature
        yield from asyncio.gather(*[cmc.ensure_reset() for cmc in self.cmcs])

    # this is synchroneous
    def nextboot_cleanup(self):
        """
        Remove nextboot symlinks for all nodes in this selection
        so next boot will be off the harddrive
        """
        [cmc.manage_nextboot_symlink('harddrive') for cmc in self.cmcs]

    @asyncio.coroutine
    def run(self, skip_stage1, skip_stage2, skip_stage3):
        yield from (self.stage1() if not skip_stage1 else self.message_bus.put("Skipping stage1"))
        yield from (self.stage2() if not skip_stage2 else self.message_bus.put("Skipping stage2"))
        yield from (self.stage3() if not skip_stage3 else self.message_bus.put("Skipping stage3"))
        yield from self.monitor.stop()

    def main(self, skip_stage1=False, skip_stage2=False, skip_stage3=False):
        loop = asyncio.get_event_loop()
        t1 = util.self_manage(self.run(skip_stage1, skip_stage2, skip_stage3))
        t2 = util.self_manage(self.monitor.run())
        tasks = asyncio.gather(t1, t2)
        try:
            loop.run_until_complete(tasks)
        except KeyboardInterrupt as e:
            self.nextboot_cleanup()
            tasks.cancel()
            loop.run_forever()
            tasks.exception()
        finally:
            self.nextboot_cleanup()
            loop.close()
