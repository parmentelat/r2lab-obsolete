import asyncio

import util
from monitor import Monitor
from frisbeed import Frisbeed

class ImageLoader:

    def __init__(self, nodes, message_bus, image):
        self.nodes = nodes
        self.message_bus = message_bus
        self.image = image
        # xxx timeout should be configurable - if it works, that is
        self.monitor = Monitor(message_bus, 2000)

    @asyncio.coroutine
    def stage1(self):
        """
        redirect nextboot symlink to frisbee, and reset all nodes
        """

        @asyncio.coroutine
        def stage1_node(node):
            # this is now synchoneous
            node.manage_nextboot_symlink('frisbee')
            yield from node.ensure_reset()
            from config import the_config
            idle = int(the_config.value('nodes', 'idle_after_reset'))
            yield from node.feedback('reboot', "idling for {}s".format(idle))
            yield from asyncio.sleep(idle)
            
        yield from asyncio.gather(*[stage1_node(node) for node in self.nodes])

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
        yield from asyncio.gather(*[node.stage2(ip, port) for node in self.nodes])
        # we can now kill the server
        yield from self.stop_frisbeed()

    @asyncio.coroutine
    def stage3(self):
        # just reset all nodes for now
        # waiting for the nodes to come back under ssh could be another image-wait feature
        yield from asyncio.gather(*[node.ensure_reset() for node in self.nodes])

    # this is synchroneous
    def nextboot_cleanup(self):
        """
        Remove nextboot symlinks for all nodes in this selection
        so next boot will be off the harddrive
        """
        [node.manage_nextboot_symlink('harddrive') for node in self.nodes]

    @asyncio.coroutine
    def run(self, skip_stage1, skip_stage2, skip_stage3):
        yield from (self.stage1() if not skip_stage1 else self.message_bus.put("Skipping stage1"))
        yield from (self.stage2() if not skip_stage2 else self.message_bus.put("Skipping stage2"))
        yield from (self.stage3() if not skip_stage3 else self.message_bus.put("Skipping stage3"))
        yield from self.monitor.stop()

    # from http://stackoverflow.com/questions/30765606/whats-the-correct-way-to-clean-up-after-an-interrupted-event-loop
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
