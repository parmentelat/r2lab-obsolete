title: Shell tools in the gateway
tab: tutorial
skip_header: True

<script src="/assets/r2lab/open-tab.js"></script>
<script src="/assets/js/diff.js"></script>
<script src="/assets/r2lab/r2lab-diff.js"></script>
<style>@import url("/assets/r2lab/r2lab-diff.css")</style>

<ul class="nav nav-tabs">
  <li class="active"> <a href="#LOGIN">LOG IN</a> </li>
  <li> <a href="#NODES">SELECT NODES</a></li>
  <li> <a href="#IMAGES">IMAGES</a></li>
  <li> <a href="#PHONES">PHONES</a></li>

  << include r2lab/tutos-index.html >>
</ul>

<div id="contents" class="tab-content" markdown="1">

<!------------ LOGIN ------------>
<div id="LOGIN" class="tab-pane fade in active" markdown="1">

### Logging in the gateway

Once you have [obtained a slice account on R2LAB
(faraday)](tuto-100-registration.md#main), you can reach the R2lab
gateway using ssh

    $ ssh -i onelab.private onelab.your.slice.name@faraday.inria.fr

---

### Listing commands

From your bash account on the gateway, you have a few very simple but
handy tools at your disposal for the early steps of your experiment,
like seeing the nodes status, turning them on or off, and loading
images.

    help

### Addressing

From the gateway, you can use the following hostnames to refer to nodes

* `fit08` : refers to the `control` wired interface on node 8; the
  control interface is configured in all our images to start up
  automatically at boot-time so the nodes can be reached.

* `data08` : refers to the `data` wired interface; this one is not
  automatically turned on, it is up to you to use it or not, you can
  use DHCP for that purpose.

* `reboot08` : refers to the ethernet interface of the CMC device on
  the node, that allows for remote management of the motherboard
  (i.e. turning nodes on and off)

Here's an example of how these names resolve. Beware that the IP
address of the reboot interface might occassionnally not be directly
to the node index, but this is seldom used by experiments.

    onelab.your.slice.name@faraday:~$ host fit08
    fit08 has address 192.168.3.8
    onelab.your.slice.name@faraday:~$ host data08
    data08 has address 192.168.2.8
    onelab.your.slice.name@faraday:~$ host reboot08
    reboot08 has address 192.168.1.8

### Checking leases

In case you're unsure about the current status of reservation, you can
list reserved timeslots - known as leases - with

    rleases

or check that you currently hold a reservation with

    rleases --check

This is a poorman's tool, as of course [the scheduler](/book.md) will
give you that same information in a much nicer way.

Note also that this is in fact equivalent to

    rhubarbe leases

[`rhubarbe`](https://github.com/parmentelat/rhubarbe) being the set of
tools that help us run the testbed. Indeed many of the convenience
functions starting with `r` in fact are aliases to a `rhubarbe`
subcommand.

In [the next tab](javascript:open_tab('NODES')) we will see how we can
focus on a specific set of nodes, and easily control them.<

</div>

<!------------ NODES ------------>
<div id="NODES" class="tab-pane fade" markdown="1">

### Monitor what you're doing

Be aware that you can have a global and live view of the testbed
status [right in the r2lab
website](http://r2lab.inria.fr/status.md). This link works for all
visitors, and if you are logged in you can [also see this
page](http://r2lab.inria.fr/run.md) that will also show you the state
of the reservation system.

### Selecting nodes

Most of the time, you will want to manage a selected subset of
nodes. There's a simple mechanism in place so you don't need to
specify your nodes for each and every command, by defining the
environment variable `NODES`. For this the `nodes` command is your
friend

To **select nodes**, use the `nodes` command. To select nodes 1 2 4 5 33 and 37 you could do this (`~` stands for negation)

    nodes 1-5 33,37 ~3

To select **all nodes**, you could do

    all-nodes

To **remove** all nodes between 3 and 35 from your selection; same with `nodes-add` for **adding nodes**

    nodes-sub 3-35

To see your selection, just run

    nodes

Finally the commands `nodes-save` and `nodes restore` let you name selections, and then reinstate them

    nodes-save run1
    ...
    nodes-restore run1

### Are these nodes on or off

    st

By default - i.e. **with no argument** - this command and most of the ones we will show here operate on **your nodes selection**, but you can always **specify another set of nodes** to operate on, regardless of the overall selection

So this will give you the status of nodes 1 2 and 3, no matter what you have selected

    st 1-3
    
### Managing nodes (turning them on or off, or rebooting)

To turn on your selected nodes selection just do

    on

Or again, if you want to turn on node 3 only, just do

    on 3

Turning them off is of course just

    off

You can trigger a reset (reboot) on a node - provided it is already on, with

    reset

To see the list of nodes that are ON

    show-nodes-on

You can select all the nodes currently ON with

    focus-nodes-on -a 

To see the linux version running in the nodes (this is less
sophisticated than what the [livetable](/status.md#livetable) would
provide)

    releases

</div>

<!------------ IMAGES ------------>
<div id="IMAGES" class="tab-pane fade" markdown="1">

### Loading images

The tool for loading images is called `rload`. It is in fact a shortcut for `rhubarbe load`, like most commands described here

    rhubarbe --help

See [the source code for `rhubarbe` for more details](https://github.com/parmentelat/rhubarbe).

Back to image loading, you will first want to know which images are available:

    rimages

Assuming you want to load the latest fedora image, you would just do

    rload -i fedora

that would act on all your selected nodes (or as always add a list of nodes to the command)

    rload -i fedora 1-10

image loading has a fancier mode that can come in handy for troubleshooting: the `--curses` mode - `-c` in short - gives you a live progressbar for each node. Note however that the curses mode is not suitable for scripting, as it will wait for a keystroke before exiting.

### Waiting for nodes

You can wait for all the selected nodes to be ssh-ready by running

    rwait

This command, like all the `rhubarbe`-related commands, has a default timeout, that you can change with (`-t` is the shortcut)

    rwait --timeout 30


### `ssh`-ing into nodes

Once you have loaded an image, you can enter all nodes by just doing

    ssh root@fit25

or just, if you're really lazy

    ss 25

You can run a command on all selected nodes with

    map ip addr show

this time of course, you cannot specify another set of nodes than the selection.

### Saving images

You have the ablility to save the image - this now of course applies only to **one node** at a time. To save node 25

    rsave 25 -o my-imge-name

This ends up in the common repository `/var/lib/rhubarbe-images`, under a name that holds the hostname and saving time. You can also provide an extra name to `rsave` with the `-o` option.

Images that may be of common interest usually needto be renamed; get in touch with the admins if you need to do this.

</div>

<!------------ PHONES ------------>
<div id="PHONES" class="tab-pane fade" markdown="1">

## Phones

We have (for now a single) commercial UE available right in the room. You can control it essentially through 2 ways

### `macphone`

The phone is physically connected through USB to a MAC (also in the room) named `macphone`;
 you can reach that MAC from faraday by doing

    macphone

From that point you can get a list of available commands, like always

    help

Among other things, you'll want to check for the folloing commands

    phone-status
    phone-off
    phone-on


### VNC

You can also use VNC to share `macphone`'s screen with the following info

    hostname : faraday.inria.fr
    port numnber : 5900
    macphone's user id : tester
    password : tester++


</div>

</div> <!-- end div contents -->
