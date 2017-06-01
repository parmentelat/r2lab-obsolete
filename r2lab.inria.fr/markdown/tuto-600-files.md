title: nepi-ng - managing files
tab: tutorial
skip_header: True

<script src="https://cdnjs.cloudflare.com/ajax/libs/jsdiff/3.2.0/diff.min.js"></script>
<script src="/assets/r2lab/open-tab.js"></script>
<script src="/assets/r2lab/r2lab-diff.js"></script>
<style>@import url("/assets/r2lab/r2lab-diff.css")</style>

<ul class="nav nav-tabs">
  <li class="active"> <a href="#INTRO">INTRO</a> </li>
  <li> <a href="#C1">C1</a></li>
  <li> <a href="#C2">C2</a></li>
  <li> <a href="#C3">C3</a></li>
  <li> <a href="#C4">C4</a></li>
  <li> <a href="#C2bis">C2bis</a></li>
  <li> <a href="#WRAPUP">WRAPUP</a></li>

  << include r2lab/tutos-index.html >>
</ul>

<div id="contents" class="tab-content" markdown="1">

<!------------ INTRO ------------>
<div id="INTRO" class="tab-pane fade in active" markdown="1">

### Scenario

In this series, we will see how to transfer files between hosts, using
the `Push` and `Pull` commands in a `SshNode`.

<br/>
The version in C3 will perform the following:

* generate a random file locally, and transfer it using SFTP onto fit01
* transfer it from fit01 to fit02 over the data network using netcat
* finally retrieve it locally from fit02 using SFTP again,
  and compare the result to make sure the file is intact.

The progression from C1 to C3 matches these bullets : C1 just
performs the first bullet, and C2 performs the first two bullets.

In C4, we add to C3 the ability to load images before actually
starting the experiment.

The last scenario, labelled C2bis, is a variant around C2. It is not
crucial to see it when first reading this tutorial.  In this scenario,
we perform the exact same scenario as in C2, but we see a recipe to
start and stop a process in sync with the jobs in a scheduler.


### New features

We will meet the `LocalNode` object that will let use run local
commands just like on remote nodes.

We will also take this chance to see that a `SshJob` object can be
defined with **several commands**, which can be helpful to avoid the
need to create long strings of jobs.

We also introduce the `Sequence` object, that is a convenience tool
for creating, well obviously, sequences of jobs, without the hassle of
managing the `required` relationship for each job.

Finally throughtout this series, we will also illustrate another
possible way to manage the components of the scheduler: instead of
creating the scheduler at the end with all the jobs, we create the
scheduler at the very beginning and create the jobs **right into the
scheduler**. Of course the result is exactly the same, it's just
another programming style that is probably worth considering.

Let us start with [copying files over to the
node](javascript:open_tab('C1')) with the `Push` command object.

</div>

<!------------ C1 ------------>
<div id="C1" class="tab-pane fade" markdown="1">

### Objective

We start over from scratch here, and to begin with, we want to

* locally generate a random file,
* and push it over to node fit01

This is what the code below carries out; the things to outline in this code are

* we see for the first time **the `LocalNode` object**, that can be used
  almost exactly as a `SshNode` object - except that it is of course
  simpler to build;

* once the local file is created, we use **a `Push` instance** instead of
  the `Run` and its variants that we have seen so far, to actually
  copy local files on the remote node;

* also note that inside a single `SshJob` instance, it is possible to
  provide an (ordered) **list of commands** to run on that node, mixing
  commands and file transfers as needed; this is how we can both push
  the `RANDOM` file over to node1, and display its size and SHA1 sum,
  using a single instance of `SshJob`.

### The code

<< codeview C1 C1-files.py >>

### Sample output

    $ python3 C1-files.py
    faraday.inria.fr:Checking current reservation for inria_r2lab.tutorial OK
    LOCALNODE:-rw-r--r--  1 parmentelat  staff  1048576 Nov 30 21:32 RANDOM
    LOCALNODE:3f147d42ed40df83819de3ab2093de352a1c5c6b  RANDOM
    fit01:-rw-r--r-- 1 root root 1048576 Nov 30 21:32 RANDOM
    fit01:3f147d42ed40df83819de3ab2093de352a1c5c6b  RANDOM

### Next

In [the next section](javascript:open_tab('C2')) we will extend this
scenario, and push the RANDOM file on another node using the wired network.

</div>

<!------------ C2 ------------>
<div id="C2" class="tab-pane fade" markdown="1">

### Objective

We extend the C1 scenario and push the RANDOM file from fit01 to fit02 over the wired network.

So we reuse the `turn-on-data` commands, that we had seen in the B
series already, to enable the `data` interface.

### File transfer per se

In order to transfer the file from fit01 to fit02: of course we could
have used simple tools like plain `scp`. Our goal however here is more
to show how to orchestrate such transfers in an environment closer to
typical experimental conditions.

So in this first variant, we will use `netcat`;  we start with running
a server instance of netcat on the receiving end (in our case
`fit02`), then run a client netcat on the sender side (here `fit01`).

In terms of synchronization, note how we

* start the server side in background (with a `&`); the corresponding
  job hence returns immediately;

* which lets us start the client side
  almost immediately afterwards (well, we add a 1s delay to stay on
  the safe side)

* and luckily enough, the server-side server will terminate as soon as
  the client side netcat is done; so we essentially do not need to
  worry about stopping the server, it stops itself at the exact right
  time

* so once the sender client is done, we can proceed and display the
  received file on fit02.

The purpose of the C2bis script is to show how one can use shell
tricks to deal with less fortunate situations, where typically the
server side runs forever, but you need to stop it once some other job
is done.

### The `Sequence` object

Note the use of the `Sequence` object in variable `transfer_job`, that
almost entirely relieves us of managing the `required` relationships.

All the jobs inserted in the `Sequence` have their `required`
relationship set to the previous job in the list, by setting
`required` on the `Sequence` object we actually deal with the
`required` jobs for the first job in the sequence.

Finally, by setting `scheduler` on this `transfer_job` object, we
automatically attach all the jobs in the sequence to the global
scheduler.

### The code

<< codeview C2 C1-files.py C2-files.py >>

### Sample output

    $ python3 C2-files.py
    faraday.inria.fr:Checking current reservation for inria_r2lab.tutorial OK
    LOCALNODE:-rw-r--r--  1 parmentelat  staff  1024 Dec  2 12:13 RANDOM
    LOCALNODE:384500c5f756f72720c2fed631191dae7edaf0bd  RANDOM
    fit01:-rw-r--r-- 1 root root 1024 Dec  2 12:13 RANDOM
    fit01:384500c5f756f72720c2fed631191dae7edaf0bd  RANDOM
    fit01:turn-on-data: data network on interface data
    fit02:turn-on-data: data network on interface data
    fit02:data
    fit01:data
    fit01:SENDER DONE
    fit02:-rw-r--r-- 1 root root 1024 Dec  2 12:13 RANDOM
    fit02:384500c5f756f72720c2fed631191dae7edaf0bd  RANDOM

### Next

In [the next section](javascript:open_tab('C3')) we will see
how to retrieve back that same file in order to close the loop.

</div>

<!------------ C3 ------------>
<div id="C3" class="tab-pane fade" markdown="1">

### Objective

In this scenario, we extend again C2 to close the loop, and retrieve
our random file back on the local laptop.

### The `Pull` object

The only new thing here is the use of a `Pull` object, which like for
the `Push` object, can be ued in a list of commands to run on a given
node as part of a `SshJob`.

### The code

<< codeview C3 C2-files.py C3-files.py >>

### Sample output

    $ python3 C3-files.py
    faraday.inria.fr:Checking current reservation for inria_r2lab.tutorial OK
    LOCALNODE:-rw-r--r--  1 parmentelat  staff  1024 Dec  2 12:17 RANDOM
    LOCALNODE:ad8ccdea8fc4fefb3f5aa2d23920aae84cb23fb8  RANDOM
    fit01:-rw-r--r-- 1 root root 1024 Dec  2 12:17 RANDOM
    fit01:ad8ccdea8fc4fefb3f5aa2d23920aae84cb23fb8  RANDOM
    fit01:data
    fit02:data
    fit01:SENDER DONE
    fit02:-rw-r--r-- 1 root root 1024 Dec  2 12:17 RANDOM
    fit02:ad8ccdea8fc4fefb3f5aa2d23920aae84cb23fb8  RANDOM
    fit02:the Pull command runs on fit02
    LOCALNODE:-rw-r--r--  1 parmentelat  staff  1024 Dec  2 12:17 RANDOM.loopback
    LOCALNODE:RANDOM.loopback identical to RANDOM

### Next

In [the next scenario](javascript:open_tab('C4')) we will learn how to add to this script the ability to load images on our traget nodes before we actually run the experiment.

</div>

<!------------ C4 ------------>
<div id="C4" class="tab-pane fade" markdown="1">

### Objective

In this scenario, we further extend the C3 scenario, and add to it the
ability to load images on the two nodes involved before the C3
scenario actually triggers.

To this end, we add a new command line option to the script, that
users can use to request image loading.

Remember that the C3 scenario is about creating a local random file,
and have it circulate from your laptop to fit01, then fit02, and back
to your laptop.

### New `nepi-ng` features

There is not much new involved in this script, as far as `nepi-ng` is
concerned.  We just add the ability to simply create an additional
`SshJob` that runs on the `faraday` gateway, and that is in charge of:

* loading the image on our selected nodes
* waiting for these nodes to come back up
* and, in the mix, turn off all other nodes in the testbed.

What takes some care, depending on the context, is the definition of
the `required` relationship; of course the part of the experience that
actually needs the nodes to be up, has to mention this extra job as a
dependency. In our case we have defined an intermediate variable
`green_light_jobs` that contains a list of the jobs that the first
experimental job - `push_job` in this case - needs to wait for before
taking off.

### `rhubarbe` features used

For turning off unused nodes, we take advantage of the `rhubarbe`
selection mechanism, where you can say e.g.

    rhubarbe nodes -a ~1 ~2 ~4-12 ~15-28-2 ~30-100
    fit03 fit13 fit14 fit16 fit18 fit20 fit22 fit24 fit26 fit28 fit29

We have written the code so that you can reuse the same fragment,
just define the list of nodes in a `node_ids` variable.

### The code

<< codeview C4 C3-files.py C4-files.py >>

### Sample output

    $ python3 C4-files.py --load
    faraday.inria.fr:Checking current reservation for inria_r2lab.tutorial OK
    LOCALNODE:-rw-r--r--  1 parmentelat  staff  1024 Dec  3 16:31 RANDOM
    LOCALNODE:22aaa184304f7202dc2554839d5e6c09fe6757ba  RANDOM
    faraday.inria.fr:reboot21:ok
    faraday.inria.fr:reboot36:already off
    <..snip..>
    faraday.inria.fr:reboot23:already off
    faraday.inria.fr:reboot09:already off
    faraday.inria.fr:16:31:28 - +000s: Selection: fit01 fit02
    faraday.inria.fr:16:31:28 - +000s: Loading image /var/lib/rhubarbe-images/ubuntu.ndz
    faraday.inria.fr:16:31:28 - +000s: AUTH: checking for a valid lease
    faraday.inria.fr:16:31:28 - +000s: AUTH: access granted
    faraday.inria.fr:16:31:28 - +000s: fit01 reboot = Sending message 'reset' to CMC reboot01
    faraday.inria.fr:16:31:28 - +000s: fit02 reboot = Sending message 'reset' to CMC reboot02
    faraday.inria.fr:16:31:30 - +002s: fit01 reboot = idling for 15s
    faraday.inria.fr:16:31:30 - +002s: fit02 reboot = idling for 15s
    faraday.inria.fr:16:31:48 - +020s: started <frisbeed@234.5.6.3:10003 on ubuntu.ndz at 500 Mibps>
    faraday.inria.fr:16:31:48 - +020s: fit01 frisbee_status = trying to telnet..
    faraday.inria.fr:16:31:48 - +020s: fit02 frisbee_status = trying to telnet..
    faraday.inria.fr:16:31:50 - +022s: fit01 frisbee_status = timed out..
    <..snip..>
    faraday.inria.fr:16:32:10 - +042s: fit02 frisbee_status = trying to telnet..
    faraday.inria.fr:16:32:10 - +042s: fit02 frisbee_status = starting frisbee client
    faraday.inria.fr:16:32:25 - +057s: fit01 Uploading successful
    faraday.inria.fr:16:32:25 - +057s: fit01 reboot = Sending message 'reset' to CMC reboot01
    |###################################################|100% |33.98s|Time: 0:00:330s|ETA:  --:--:--
    faraday.inria.fr:16:32:34 - +066s: fit02 Uploading successful
    faraday.inria.fr:16:32:34 - +066s: fit02 reboot = Sending message 'reset' to CMC reboot02
    faraday.inria.fr:16:32:36 - +068s: stopped <frisbeed@234.5.6.3:10003 on ubuntu.ndz at 500 Mibps>
    faraday.inria.fr:<Node fit01>:ssh OK
    faraday.inria.fr:<Node fit02>:ssh OK
    fit01:-rw-r--r-- 1 root root 1024 Dec  3 16:33 RANDOM
    fit01:22aaa184304f7202dc2554839d5e6c09fe6757ba  RANDOM
    fit01:turn-on-data: data network on interface data
    fit02:turn-on-data: data network on interface data
    fit01:data
    fit02:data
    fit01:SENDER DONE
    fit02:-rw-r--r-- 1 root root 1024 Dec  3 16:33 RANDOM
    fit02:22aaa184304f7202dc2554839d5e6c09fe6757ba  RANDOM
    fit02:the Pull command runs on fit02
    LOCALNODE:-rw-r--r--  1 parmentelat  staff  1024 Dec  3 16:33 RANDOM.loopback
    LOCALNODE:RANDOM.loopback identical to RANDOM

### Next

If this is your first reading, we suggest you skip C2bis and [go
directly to WRAPUP](javascript:open_tab('WRAPUP')) for a conclusion on
this series.

</div>

<!------------ C2bis ------------>
<div id="C2bis" class="tab-pane fade" markdown="1">

### Objective

In this particular scenario, we are revisiting the C2 series.

Remember C2 is about transferring a file from node 1 to node 2 over
the data network, thanks to `netcat`. As we had seen at the time, it
is rather fortunate that `netcat` in server mode` returns as soon as
its (single) client terminates.

There are a lot of cases though, where things are not that simple, and
there is a need to manually terminate / cleanup dangling processes
that are no longer useful.

<br/>

Sometimes, it is only a matter of starting and stopping packaged
services like apache or similar, and in this case all need to do is to
call things like e.g. `systemctl start apache2` and `systemctl stop
apache2`.

<br/>

In the code below, you will see a technique that can be used to start
and stop, and even monitor, a custom process. This is in
`receiver_manager_script`, a small shell script that knows how to
start, stop, and even monitor, a single-process service.

### Graphical view

On any instance of `Scheduler` it is easy to get a graphical view of
the jobs and their dependencies, using the `export_as_dotfile` method,
in conjunction with any program that supports
[the `dot` format](https://en.wikipedia.org/wiki/DOT_(graph_description_language)).
The attached image was produced with `dot` that comes with the `graphviz`
package.

<img src="assets/img/C2bis-files.png" width="100%">

In this respect, note that:

* each job needs a specific label to be displayed in such a graph - as
  well as in `list()` and `debrief()` by the way

* the system does its best to provide a meaningful label, but

* you are always free to define your own label on a given job, like we
  did here with a few job instances.

### The code

<< codeview C2bis C2-files.py C2bis-files.py >>

### Sample output

    $ python3 C2bis-files.py
    faraday.inria.fr:Checking current reservation for inria_r2lab.tutorial OK
    LOCALNODE:-rw-r--r--  1 parmentelat  staff  1024 Dec  2 14:13 RANDOM
    LOCALNODE:950dd7f38a2691dd172cc09a00a3fe1da24cb413  RANDOM
    fit01:-rw-r--r-- 1 root root 1024 Dec  2 14:13 RANDOM
    fit02:no netcat process
    fit01:950dd7f38a2691dd172cc09a00a3fe1da24cb413  RANDOM
    fit02:no netcat process
    fit02:data
    fit01:data
    fit02:no netcat process
    fit02:no netcat process
    fit02:no netcat process
    fit02:Using id=02 and fitid=fit02 - from hostname
    fit02:STARTING CAPTURE into RANDOM
    fit02:netcat server running on data02:10000 in pid 28186
    fit02:  PID TTY      STAT   TIME COMMAND
    fit02:28186 ?        S      0:00 netcat -l data02 10000
    fit02:  PID TTY      STAT   TIME COMMAND
    fit02:28186 ?        S      0:00 netcat -l data02 10000
    fit02:  PID TTY      STAT   TIME COMMAND
    fit02:28186 ?        S      0:00 netcat -l data02 10000
    fit02:  PID TTY      STAT   TIME COMMAND
    fit02:28186 ?        S      0:00 netcat -l data02 10000
    fit02:no netcat process
    fit02:no netcat process
    fit01:SENDER DONE
    fit02:no netcat process
    fit02:no netcat process
    fit02:STARTING CAPTURE into
    fit02:Would kill process 28186
    fit02:no netcat process
    fit02:-rw-r--r-- 1 root root 1024 Dec  2 14:13 RANDOM
    fit02:no netcat process
    fit02:950dd7f38a2691dd172cc09a00a3fe1da24cb413  RANDOM
    fit02:no netcat process

### Next
We can now [conclude this section](javascript:open_tab('WRAPUP'))

</div>

<!------------ WRAPUP ------------>
<div id="WRAPUP" class="tab-pane fade" markdown="1">

In this C series , we have seen:

* how to use the `Push` and `Pull` commands to copy files back and
  forth on and from nodes;

* how to use the `LocalNode` to augment our scripts with commands run
  locally;

* how a single `SshJob` can trigger several commands, mixing `Run`,
  `RunString`, `Push` and `Pull` types of commands;

* how we can add an image loading feature in a `nepi-ng` script (in C4);

* how to implement (in C2bis) a rustic service management feature, for house cleaning purposes;

* and finally, still in C2bis, how to produce a graphical view of a
  `Scheduler` for documentation and/or troubleshooting.

</div>

</div> <!-- end div contents -->
