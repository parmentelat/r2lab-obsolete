#!/usr/bin/env python3

import os, os.path
import stat
import tarfile
import shutil
import asyncio

from asynciojobs import Engine, Sequence, Job

from apssh.formatters import ColonFormatter
from apssh.keys import load_agent_keys
from apssh.jobs.sshjobs import SshNode, SshJob, SshJobScript, SshJobPusher, SshJobCollector

async def aprint(*args, **kwds):
    print(*args, **kwds)

#
# Usage:
# build.py gateway node script from-image to-image
#
class ImageBuilder:

    def __init__(self, gateway, node, from_image, to_image, scripts, includes, extra_logs, path):
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
        self.includes = includes
        self.extra_logs = [] if extra_logs is None else extra_logs
        # : separated list of paths to search - like $PATH
        # we add automatically so as to locate build-image.sh
        self.paths = path.split(":") + [ '.' ]
        
    def user_host(self, input):
        # callers can mention localhost as the gateway to avoid
        # the extra ssh leg
        if 'localhost' in input:
            return None, None
        try:
            username, hostname = input.split('@')
        except:
            username, hostname = "root", input
        return username, hostname

    def locate_script(self, script):
        result = None
        for path in self.paths:
            candidate = os.path.join(path, script)
            if os.path.exists(candidate):
                return candidate

    def locate_companion_shell(self):
        self.companion = self.locate_script("build-image.sh")
        if self.companion is None:
            print("Cannot locate build-image.sh in {}"
                  .format(self.paths))
            exit(1)

    def prepare_tar(self, dirname):
        """
        given the list of scripts and includes in self, this will
        * create a subdir named dirname
        * create 3 subdirs scripts/ args/ logs/
        * create symlinks named scripts/nnn-script -> script[0] starting at 001
        * create symlinks in scripts/ for all the includes 
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
            # search script in self.path
            localfile = self.locate_script(localfile)
            if not localfile:
                print("Cannot locate {} - exiting".format(script[0]))
                exit(1)
            os.chmod(localfile, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            basename = os.path.basename(localfile)
            numbered = "{:03d}-{}".format(i, basename)
            linkname = os.path.join(dirname, 'scripts', numbered)
            os.symlink(os.path.abspath(localfile), linkname)
            with open(os.path.join(dirname, 'args', numbered), 'w') as out:
                out.write(" ".join(script_args))
        for include in self.includes:
            include = self.locate_script(include)
            if not include:
                print("Cannot locate {} - exiting".format(script[0]))
                exit(1)
            basename = os.path.basename(include)
            linkname = os.path.join(dirname, 'scripts', basename)
            os.symlink(os.path.abspath(include), linkname)
        tarname = "{}.tar".format(dirname)
        with tarfile.TarFile(tarname, 'w', dereference=True) as tar:
            tar.add(dirname)
        return tarname

    def run(self, verbose, debug, no_load, no_save):
        """
        can skip the load or save phases
        """

        print("Using node {} through gateway {}".format(self.node, self.gateway))
        print("In order to produce {} from {}".format(self.to_image, self.from_image))
        print("The following scripts will be run:")
        for i, script in enumerate(self.scripts, 1):
            print("{:03d}:{}".format(i, " ".join(script)))
            
        items = []
        if no_load: items.append("skip load")
        if no_save: items.append("skip save")
        if items:
            print("WARNING: using fast-track mode {}"
                  .format(' & '.join(items)))

        self.locate_companion_shell()
        if verbose: print("Located companion in {}".format(self.companion))

        if verbose: print("Preparing tar of input shell scripts .. ", end="")
        tarfile = self.prepare_tar(self.to_image)
        if verbose: print("Done in {}".format(tarfile))

        keys = load_agent_keys()
        if verbose: print("We have found {} keys in the ssh agent".format(len(keys)))

        #################### the 2 nodes we need to talk to
        gateway_proxy = None
        gwuser, gwname = self.user_host(self.gateway)
        gateway_proxy = None if not gwuser else SshNode(
            hostname = gwname,
            username = gwuser,
            keys = keys,
            formatter = ColonFormatter(),
            debug = debug,
        )

        # really not sure it makes sense to use username other than root
        username, nodename = self.user_host(self.node)
        node_proxy = SshNode(
            gateway = gateway_proxy,
            hostname = nodename,
            username = username,
            keys = keys,
            formatter = ColonFormatter(),
            debug = debug,
        )

        banner = 20*'*'
        #################### the little pieces
        sequence = Sequence(
            Job(aprint(banner, "loading image {}".format(self.from_image)
                       if not no_load 
                       else "fast-track: skipping image load"
                   )),
            SshJob(
                node = gateway_proxy,
                commands = [
                    [ "rhubarbe", "load", "-i", self.from_image, nodename ] if not no_load else None,
                    [ "rhubarbe", "wait", "-v", "-t", "240", nodename ],
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
                command = [ self.companion, nodename, self.from_image, self.to_image ],
                label = "run scripts",
            ),
            SshJobCollector(
                node = node_proxy,
                remotepaths = "/etc/rhubarbe-history/{}/logs/".format(self.to_image),
                localpath = "{}/logs/".format(self.to_image),
                label = "retrieve logs",
                recurse = True,
            ),
        )

        # retrieve extr logs before saving
        for extra_log in self.extra_logs:
            sequence.append(
                SshJobCollector(
                    node = node_proxy,
                    remotepaths = extra_log,
                    localpath = "{}/logs/".format(self.to_image),
                    label = "retrieve extra log {}".format(extra_log),
                    recurse = True,
                )
            )

        # xxx some flag
        if no_save:
            sequence.append(
                Job(aprint(banner, "fast-track: skipping image save")))
        else:
            sequence.append(
                Sequence(
                    Job(aprint(banner, "saving image {} ..."
                               .format(self.to_image))),
                    # make sure we capture all the logs and all that
                    SshJob(
                        node = node_proxy,
                        commands = [
                            ["sync"],
                            ["sleep", "1"],
                            ["sync"],
                            ["sleep", "1"],
                        ],
                        label = 'sync',
                    ),
                    SshJob(
                        node = gateway_proxy,
                        command = [ "rhubarbe", "save", "-o", self.to_image, nodename ],
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
    usage = """
Create an R2lab image by loading 'from_image', running some scripts, and save into 'to_image'

All scripts are searched in 
* the path provided with -p
* the location of this command (esp. useful for spotting 'build-image.sh')
* .

Included scripts are useful if one of your own scripts sources another one.
Bear in mind that all scripts are first copied over on the target node in 
/etc/rhubarbe-history/to_image/scripts
together with their arguments and stuff
"""
    parser = ArgumentParser()
    parser.add_argument("-n", "--no-load-save", action='store_true', default=False,
                        help="skip load and save, for when developping scripts")
    parser.add_argument("-c", "--chain", action='store_true', default=False,
                        help="avoid loading given image, useful when chaining builds")
    parser.add_argument("-v", "--verbose", action='store_true', default=False)
    parser.add_argument("-d", "--debug", action='store_true', default=False)
    parser.add_argument("-i", "--includes", action='append', default=[])
    parser.add_argument("-l", "--logs", dest='extra_logs', action='append', default=[],
                        help="additional logs to be collected")
    parser.add_argument("-p", "--path", action='append', dest='paths', default=[],
                        help="colon-separated list of dirs to search")
    parser.add_argument("-s", "--silent", action='store_true', default=False,
                        help="redirect stdout and stder to <to_image>.log")
    parser.add_argument("gateway", help="no gateway if this contains 'localhost'")
    parser.add_argument("node", help="fit node to use - name or number")
    parser.add_argument("from_image", help="the image to start from")
    parser.add_argument("to_image", help="the image to create; use '==' to keep the same")
    parser.add_argument("scripts", nargs='+', help="each scripts is a space separated command")
    args = parser.parse_args()

    # find out where the command is stored so we can locate build-image.sh
    import sys
    command_dir = os.path.dirname(sys.argv[0])

    # keep the same image name over daily updates : use == in to_image
    to_image = args.from_image if '==' in args.to_image else args.to_image
    
    try:
        node_id = int(args.node.replace('fit', ''))
        node = "fit{:02d}".format(node_id)
    except:
        print("cannot normalize {} - exiting".format(args.node))
        import traceback
        traceback.print_exc()
        exit(1)

    # add the location of this command to the path
    path = ":".join(args.paths + [ command_dir ] )
        
    # default is of course to load and save
    no_load, no_save = False, False
    # -n means realy no load and no save
    if args.no_load_save:
        no_load, no_save = True, True
    if args.chain:
        no_load = True

    if args.silent:
        import sys
        sys.stdout = sys.stderr = open("{}.log".format(to_image), 'w')
    builder = ImageBuilder(gateway=args.gateway, node=node,
                           from_image=args.from_image, to_image=to_image,
                           scripts=args.scripts, includes=args.includes,
                           extra_logs=args.extra_logs, path=path)
    run_code = builder.run(verbose=args.verbose, debug=args.debug,
                           no_load=no_load, no_save=no_save)
    return 0 if run_code else 1

if __name__ == '__main__':
    exit(main())
