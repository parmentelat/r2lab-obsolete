#!/usr/bin/env python3

import os, os.path
import stat
import tarfile
import shutil

from asynciojobs import Engine, Sequence

from apssh.formatters import ColonFormatter
from apssh.keys import load_agent_keys
from apssh.jobs.sshjobs import SshNode, SshJob, SshJobScript, SshJobPusher

#
# Usage:
# build.py gateway node script from-image to-image
#
class ImageBuilder:

    def __init__(self, gateway, node, from_image, to_image, scripts):
        """
        scripts is expected to be a list of strings
        each may contain spaces if arguments are passed
        """
        self.gateway = gateway
        self.node = node
        self.from_image = from_image
        self.to_image = to_image
        # normalize this one as a list of lists
        self.scripts = [ s.split() for s in scripts ]
        
    def user_host(self, input):
        try:
            username, hostname = input.split('@')
        except:
            username, hostname = "root", input
        return username, hostname

    def prepare_tar(self, dirname):
        """
        given the normalized list of scripts in self.scripts, this will
        * create a subdir named dirname
        * create 3 subdirs scripts/ args/ logs/
        * create symlinks named scripts/nnn-script -> script[0] starting at 001
        * create files named args/nnn-script -> the arguments to be passed to <script>
        * create a tarfile <dirname>.tar of subdir/ that can be transferred remotely 
        """
        try:
            os.mkdir(dirname)
        except:
            shutil.rmtree(dirname)
            os.mkdir(dirname)
            
        for subdir in "scripts", "args", "logs":
            os.mkdir(os.path.join(dirname, subdir))
        for i, script in enumerate(self.scripts, 1):
            localfile, *script_args = script
            os.chmod(localfile, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            basename = os.path.basename(localfile)
            numbered = "{:03d}-{}".format(i, basename)
            linkname = os.path.join(dirname, 'scripts', numbered)
            os.symlink(os.path.abspath(localfile), linkname)
            with open(os.path.join(dirname, 'args', numbered), 'w') as out:
                out.write(" ".join(script_args))
        tarname = "{}.tar".format(dirname)
        with tarfile.TarFile(tarname, 'w', dereference=True) as tar:
            tar.add(dirname)
        return tarname

    def run(self, verbose, debug, fast):

        print("Using node {} through gateway {}".format(self.node, self.gateway))
        print("In order to produce {} from {}".format(self.to_image, self.from_image))
        print("The following scripts will be run:")
        for i, script in enumerate(self.scripts):
            print("{:03d}:{}".format(i, " ".join(script)))
            
        if fast:
            print("WARNING: using fast mode - no image load or save")

        if verbose: print("Preparing tar of input shell scripts .. ", end="")
        tarfile = self.prepare_tar(self.to_image)
        if verbose: print("Done in {}".format(tarfile))

        keys = load_agent_keys()
        if verbose: print("We have found {} keys in the ssh agent".format(len(keys)))

        #################### the 2 nodes we need to talk to
        gateway_proxy = None
        username, hostname = self.user_host(self.gateway)
        gateway_proxy = SshNode(
            hostname = hostname,
            username = username,
            client_keys = keys,
            formatter = ColonFormatter(),
            debug = debug,
        )

        # really not sure it makes sense to use username other than root
        username, hostname = self.user_host(self.node)
        node_proxy = SshNode(
            gateway = gateway_proxy,
            hostname = hostname,
            username = username,
            client_keys = keys,
            formatter = ColonFormatter(),
            debug = debug,
        )

        #################### the little pieces
        sequence = Sequence(
            SshJob(
                node = gateway_proxy,
                commands = [
                    [ "rhubarbe", "load", "-i", self.from_image, self.node ] if not fast else None,
                    [ "rhubarbe", "wait", self.node ],
                ],
                label = "load and wait image {}".format(self.from_image),
            ),
            SshJob(
                node = node_proxy,
                commands = [
                    [ "rm", "-rf", "/etc/rhubarbe-history/{}".format(self.to_image) ],
                    [ "mkdir", "-p", "/etc/rhubarbe-history", ],
                    ],
                label = "clean up /etc/rhubarbe-history/{}".format(self.to_image),
            ),
            SshJobPusher(
                node = node_proxy,
                localpaths = tarfile,
                remotepath = "/etc/rhubarbe-history",
                label = "push scripts tarfile",
            ),
            SshJobScript(
                node = node_proxy,
                command = [ "./build-image.sh", self.from_image, self.to_image ],
                label = "run scripts",
            ),
        )

        # xxx some flag
        if not fast:
            sequence.append(
                Sequence(
                    SshJob(
                        node = gateway_proxy,
                        command = [ "rhubarbe", "save", "-o", self.to_image, self.node ],
                        label = "save image {}".format(self.to_image),
                    ),
                    SshJob(
                        node = gateway_proxy,
                        command = [ "rhubarbe", "images"],
                        label = "list current images",
                    ),
                )
            )

        e = Engine(sequence,
                   verbose = verbose,
                   debug = debug,
                   critical = True,
               )
        # sanitizing for the cases where some pieces are left out
        e.sanitize()

        if e.orchestrate():
            if verbose:
                e.debrief(sep = 40*'*' + ' debrief OK')
                e.list(40*'*' + ' list()')
            print("image {} OK".format(self.to_image))
            return True
        else:
            print("Something went wrong with image {}".format(self.to_image))
            if debug:
                e.debrief(40*'*' + ' debrief KO')
            return False

from argparse import ArgumentParser

def main():
    parser = ArgumentParser()
    parser.add_argument("-f", "--fast", action='store_true', default=False,
                        help="skip load and save, for when developping scripts")
    parser.add_argument("-v", "--verbose", action='store_true', default=False)
    parser.add_argument("-d", "--debug", action='store_true', default=False)
    parser.add_argument("gateway")
    parser.add_argument("node")
    parser.add_argument("from_image")
    parser.add_argument("to_image")
    parser.add_argument("scripts", nargs='+')
    args = parser.parse_args()

    try:
        node_id = int(args.node.replace('fit', ''))
        node = "fit{:02d}".format(node_id)
    except:
        print("cannot normalize {} - exiting".format(args.node))
        import traceback
        traceback.print_exc()
        exit(1)

    builder = ImageBuilder(args.gateway, node, args.from_image, args.to_image, args.scripts)
    run_code = builder.run(verbose=args.verbose, debug=args.debug, fast = args.fast)
    return 0 if run_code else 1

if __name__ == '__main__':
    exit(main())
        
