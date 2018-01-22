#!/usr/bin/env python3

v = {
    'verbose': True
}

from asynciojobs import Scheduler, Sequence
from apssh import SshNode, LocalNode, SshJob, Run, RunScript, Pull

faraday = SshNode(hostname='faraday.inria.fr', username='root', **v)
r2labapi = SshNode(hostname='r2labapi.inria.fr', username='root', **v)
localnode = LocalNode()

scheduler = Scheduler(**v)

dump = SshJob(
    node = faraday,
    scheduler = scheduler,
    commands = [
        Run("rm -rf DATA"),
        Run("mkdir DATA"),
        RunScript("dump-all.sh",
                  includes = ['migrate.py']),
        RunScript("extract-leases.py", "-j DATA/LEASES.json onecalvin"),
# I can't get this Pull thing to work as expected
#        Pull(remotepaths=["DATA"], localpath='.', recurse=True),
    ],
)

retrieve = SshJob(
    localnode,
    scheduler = scheduler,
    commands = [
        Run("rsync -av root@faraday.inria.fr:DATA/ DATA/")
    ]
)

gather = Sequence(dump, retrieve)

reset = SshJob(
    node = r2labapi,
    scheduler = scheduler,
    commands = [
        Run("psql -U pgsqluser template1 -c 'drop database planetlab5'"),
        Run("service plc restart"),
    ],
    )

rebuild = SshJob(
    node = localnode,
    scheduler = scheduler,
    required = (gather, reset),
    commands = [
        Run("python2", "-u", "migrate.py", "rebuild"),
    ],
)

ok = scheduler.orchestrate()
ok or scheduler.debrief()



