#!/usr/bin/env python3

import os.path

from asynciojobs import Engine, Job, Sequence

from apssh import SshNode, SshJob, SshJobScript
from apssh.formatters import ColonFormatter

def r2lab_hostname(x):
    """
    Return a hostname from a name like either
    1 (int), 1(str), 01, fit1 or fit01 ...
    """
    return "fit{:02d}".format(int(str(x).replace('fit','')))

def script(s):
    """
    all the scripts are located in the same place
    """
    return os.path.join(os.path.expanduser("~/git/r2lab/infra/user-env/"), s)

# include the same set of utility scripts
includes = [ script(x) for x in [ "r2labutils.sh", "nodes.sh", "oai-common.sh"] ]

def run(gateway, hss, epc, enb, do_load, verbose, debug):
    """
    expects e.g.
    * gateway : s.t like onelab.inria.oai.oai_build@faraday.inria.fr
    * hss : 23
    * epc : 16
    * enb : 19
    """
    
    gwuser, gwhost = gateway.split('@')
    gwnode = SshNode(hostname = gwhost, username = gwuser,
                     formatter = ColonFormatter(), debug=debug)

    hssname, epcname, enbname = [ r2lab_hostname(x) for x in (hss, epc, enb) ]
    
    hssnode, epcnode, enbnode = [
        SshNode(gateway = gwnode, hostname = hostname, username = 'root',
                formatter = ColonFormatter(), debug=debug)
        for hostname in (hssname, epcname, enbname)
    ]

    load_infra = SshJob(
        node = gwnode,
        commands = [
            [ "rhubarbe", "load", "-i", "u16-oai-gw", hssname, epcname ],
            [ "rhubarbe", "wait", "-t",  120, hssname, epcname ],
        ],
        label = "load and wait HSS and EPC nodes",
    )

    load_enb = SshJob(
        node = gwnode,
        commands = [
            [ "rhubarbe", "load", "-i", "u16-oai-enb", enbname ],
            [ "rhubarbe", "wait", "-t", 120, enbname ],
        ],
        label = "load and wait ENB",
    )

    loaded = [load_infra, load_enb]
    
#    macphone = SshNode(gateway = gwnode, hostname = 'macphone', username = 'tester',
#                       formatter = ColonFormatter(), debug = debug)
    stop_phone = SshJobScript(
        node = gwnode,
        command = [ script("faraday.sh"), "macphone", "r2lab/infra/user-env/macphone.sh", "phone-off" ],
        includes = includes,
        label = "Stopping phone",
        # stop it at the beginning of the scenario, so no required
    )

    run_hss = SshJobScript(
        node = hssnode,
        command = [ script("oai-gw.sh"), "run-hss", epc ],
        includes = includes,
        label = "run HSS",
        required = (loaded, stop_phone),
    )

    run_epc = SshJobScript(
        node = epcnode,
        command = [ script("oai-gw.sh"), "run-epc", hss ],
        includes = includes,
        label = "run EPC",
        required = (loaded, stop_phone),
    )

    run_enb = SshJobScript(
        node = enbnode,
        # run-enb expects the id of the epc as a parameter
        command = [ script("oai-enb.sh"), "run-enb", epc ],
        includes = includes,
        label = "run softmodem on ENB",
        required = (loaded, stop_phone),
    )

    # schedule the load phases only if required
    e = Engine(stop_phone, run_enb, run_epc, run_hss, verbose=verbose, debug=debug)
    if do_load:
        e.update(loaded)
    # remove requirements to the load phase if not added
    e.sanitize(verbose=False)
    
    print(40*'*', 'do_load=', do_load)
    e.list()

    if not e.orchestrate():
        print("KO")
        e.debrief()
    else:
        print("OK")

def main():

    default_slice = "onelab.inria.oai.oai_build@faraday.inria.fr"
    def_hss, def_epc, def_enb = 23, 16, 19
    

    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-l", "--load", dest='do_load', action='store_true', default=False,
                        help='load images as well')
    parser.add_argument("-v", "--verbose", action='store_true', default=False)
    parser.add_argument("-d", "--debug", action='store_true', default=False)
    parser.add_argument("-s", "--slice", default=default_slice,
                        help="defaults to {}".format(default_slice))

    parser.add_argument("--hss", default=def_hss, help="defaults to {}".format(def_hss))
    parser.add_argument("--epc", default=def_epc, help="defaults to {}".format(def_epc))
    parser.add_argument("--enb", default=def_enb, help="defaults to {}".format(def_enb))

    args = parser.parse_args()
    
    run(args.slice, hss = args.hss, epc = args.epc, enb = args.enb,
        do_load = args.do_load,
        verbose = args.verbose, debug = args.debug)

main()
