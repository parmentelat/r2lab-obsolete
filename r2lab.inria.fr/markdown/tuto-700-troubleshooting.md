title: nepi-ng - troubleshooting
tab: tutorial
skip_header: True

<script src="/assets/r2lab/open-tab.js"></script>
<script src="/assets/js/diff.js"></script>
<script src="/assets/r2lab/r2lab-diff.js"></script>
<style>@import url("/assets/r2lab/r2lab-diff.css")</style>

<ul class="nav nav-tabs">
  <li class="active"> <a href="#INTRO">INTRO</a> </li>
  <li> <a href="#COMMON MISTAKES">COMMON_MISTAKES</a></li>
  <li> <a href="#CODE UPDATE">CODE_UPDATE</a></li>
  <li> <a href="#VERBOSITY">VERBOSITY</a></li>
  << include r2lab/tutos-index.html >>
</ul>

<div id="contents" class="tab-content" markdown="1">

<!------------ INTRO ------------>
<div id="INTRO" class="tab-pane fade in active" markdown="1">

# Objectives

In this page we are going to see a few guidelines for troubleshooting
a `nepi-ng` script.

This tuto is organized in several parts

* Common mistakes : works as a simple checklist that should let you
  figure out the most common mistakes.

* Code updates : check to see if you're running the latest versions of the code

* Verbosity : how to enable more logging messages from your script

</div>

<!------------ COMMON_MISTAKES ------------>
<div id="COMMON_MISTAKES" class="tab-pane fade" markdown="1">

## Check for the obvious

Before you start diving in the code, it is **always** a good idea to
step back a little, and to check for the following common mistakes.

This is especially true when you start with `nepi-ng` and `R2lab, and
your scripts are not sophisiticated enough to do all these checks by
themselves.

Also these common sources of glitches occur frequently if you were
working on your scenario, and then your time went up, you are now just
back to the testbed.

### Do you have a valid reservation on the testbed ?

If your script does not check for that, it's a good idea to double check.

### Can you reach `faraday` via ssh ?

Try to enter the gateway with this simple command

    ssh your_slicename@faaday.inria.fr

If this does not work, then double check that your onelab private key
is known to your ssh agent - especially if you have recently logged out :

    ssh-add -l

### Are the nodes up ? Do they run the expected image ?

You can check all your nodes [directly in the `RUN`](run.md) page on the web
site, or with a session like this (when logged in `faraday`), assuming
that you need nodes 4, 6 and from 10 to 13 inclusive :


    $ rleases --check
    Checking current reservation for inria_r2lab.tutorial OK

    # select your nodes
    inria_r2lab.tutorial@faraday:~$ n 4 6 10-13
    export NODES="fit04 fit06 fit10 fit11 fit12 fit13"
    export NBNODES=6

    # check they are reachable through ssh - use the --timeout option if needed
    inria_r2lab.tutorial@faraday:~$ rwait
    <Node fit04>:ssh OK
    <Node fit06>:ssh OK
    <Node fit10>:ssh OK
    <Node fit11>:ssh OK
    <Node fit12>:ssh OK
    <Node fit13>:ssh OK

    # what image are they all running ?
    inria_r2lab.tutorial@faraday:~$ map rimage
    fit04:2016-11-29@00:12 - built-on fit03 - from-image fedora-23-v10-wireless-names - by inria_r2lab.tutorial
    fit10:2016-11-29@00:12 - built-on fit03 - from-image fedora-23-v10-wireless-names - by inria_r2lab.tutorial
    fit06:2016-11-29@00:12 - built-on fit03 - from-image fedora-23-v10-wireless-names - by inria_r2lab.tutorial
    fit13:2016-11-29@00:12 - built-on fit03 - from-image fedora-23-v10-wireless-names - by inria_r2lab.tutorial
    fit11:2016-11-29@00:12 - built-on fit03 - from-image fedora-23-v10-wireless-names - by inria_r2lab.tutorial
    fit12:2016-11-29@00:12 - built-on fit03 - from-image fedora-23-v10-wireless-names - by inria_r2lab.tutorial

</div>

<!------------ CODE_UPDATE ------------>
<div id="CODE_UPDATE" class="tab-pane fade" markdown="1">

The software involved in R2lab, either `nepi-ng` or the shell
utilities, are evolving quickly, especially during the current rollout
period.

So here's how you can check for possibly out-dated versions of either of these :

### `python3`

Please double check that you

* indeed run python-3.5 or higher
* and that you indeed use `python3` to run your script - it is so easy to
  forget the `3` in `python3 A1-ping.py` !

### `nepi-ng`

You can make sure that you run the latest version of `nepi-ng` by running

    [sudo] pip3 install --upgrade asynciojobs apssh

Alternatively, you can check the currently running versions by doing on your laptop

    $ python3 -c 'from asynciojobs import version; print(version.version)'
    $ python3 -c 'from apssh import version; print(version.version)'

and then compare them against the latest release numbers for these 2 libraries, that can be found :

* either by searching `https://pypi.python.org`,
* or in the respective documentation pages for
[`asynciojobs`](http://nepi-ng.inria.fr/asynciojobs/) and
[`apssh`](http://nepi-ng.inria.fr/apssh/).

### `shell tools`

The shell tools are used

* on `faraday` itself, but you can consider this is always up-to-date,
* as well as on the nodes themselves; and in this case, the version of
the R2lab convenience tools - like `turn-on-data` or other `r2lab-id`
or similar tools - that you use depends on **the date where your image
was created**.

This is why it is always a good idea to have your shell scripts,
whenever they source `/root/r2lab/infra/user-env/node.sh`, call
`git-pull-r2lab` which will update the whole repository `/root/r2lab`
from the latest version published on github.

</div>

<!------------ VERBOSITY ------------>
<div id="VERBOSITY" class="tab-pane fade" markdown="1">

OK, so you have tried everything else, you can't seem to find why your
script does not behave like you expected it to. Here's a brief
description of the various levels of verbosity that you can enable in
your script.

# `Scheduler.debrief()`

In all our examples so far, you have noticed that we always run a
scheduler like this :

    # run the scheduler
    ok = scheduler.orchestrate()
    # give details if it failed
    ok or scheduler.debrief()

This means that, if ever `orchestrate()` does not return `True`, we
run the `debrief()` method on that scheduler.

Keep in mind that `orchestrate` orchestration returns `False` only in
either of these 2 cases:

* one of the *critical* jobs inside the scheduler has raised an exception,
* and when you specify a timeout by calling e.g. `orchestrate(timeout=120)`,
if the total duration of `orchestrate` exceeds that timeout.

So if `orchestrate()` returns `False`, and you have not specified a
global timeout, it means you are in the first situation; and by
calling `debrief()` like we have done in all the tutorials, you will
see more details on the critical job that has caused the scheduler to
bail out.

# Structure of the scheduler

The programming style used to create a `Scheduler` instance and to add
jobs in it can sometimes lead to unexpected results. Typical mistakes
generally involve

* erroneous `required` relationsships,
* and jobs with wrong *criticality*.

You have several
means to check it for mistakes

### Checking contents

The `Scheduler.list()` method allows you to see an overview of your
`Scheduler` object, in terms of the jobs it contains, and their
`required` relationship. You can use it anytime, before or after you
orchestrate the scheduler, but if your script behaves oddly it might
be a good idea to check the scheduler before running it

     # just before you run orchestrate()
     shceduler.list()

You can even ask for more details

    scheduler.list(details=True)

`Sceduler.list()` uses some symbols in the hope to provide meaningful
information in a condensed way, you [can refer to this
page](http://nepi-ng.inria.fr/asynciojobs/README.html#inspecting-scheduler-and-results-scheduler-list)
to see the meaning of the different symbols, but in a nutshell:

* `⚠` : critical
* `★` : raised an exception
* `☉` : went through fine (no exception raised)
* `☓` : complete
* `↺` : running  
* `⚐` : idle     
* `∞` : forever  


### Graphical view

As we [have already seen in C2bis](tuto-600-files.md#C2bis), it is
rather easy to produce a *png* file that depicts the jobs in a
scheduler, together with their relationships.

    scheduler.export_as_dotfile("foo.dot")
    import os
    os.system("dot -Tpng -o foo.png foo.dot")

You will need to install `graphviz` so that you can use the `dot`
program in this fragment. Here's the example of output obtained in
[C2bis](tuto-600-files.md#C2bis)

<center><img src="assets/img/C2bis-files.png" height="150px"></center>

# Verbosity

You can also enable more verbosity in any of the following classes.

### `SshNode`

Setting `verbose=True` on an instance of `SshNode` results in messages
being printed about ssh connections and sessions being open and
closed. The scripts in the tutorial implement a `-v` option that does
just that, it is really useful especially for beginners.

If you do not set this, failures to create ssh connections go unnoticed.

Implementation note: this flag is in actuality passed to the
underlying *formatter* object.

### `SshJob`

Setting `verbose=True` on a `SshJob` instance results in all its
commands being run in verbose mode.

### `Run` and other commands

* `Run` : in verbose mode, shows the command that is run, and its return code once it's done
* `RunScript` and `RunScript` : in verbose mode, remote script is run using `bash -x`; expect a lot of output here
* `Push` and `Pull` : print actual arguments to the SFTP get and put

### `Scheduler`

Finally you can set `verbose=True` on a `Scheduler` object, which will
give you details of the jobs being started, and their are done.

</div>

</div> <!-- end div contents -->
