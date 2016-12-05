title: nepi-ng - wireless
tab: tutorial
skip_header: True

<script src="/assets/r2lab/open-tab.js"></script>
<script src="/assets/js/diff.js"></script>
<script src="/assets/r2lab/r2lab-diff.js"></script>
<style>@import url("/assets/r2lab/r2lab-diff.css")</style>


<ul class="nav nav-tabs">
  <li class="active"> <a href="#INTRO">INTRO</a> </li>
  <li> <a href="#B1">B1</a></li>
  <li> <a href="#B2">B2</a></li>
  <li> <a href="#B3">B3</a></li>
  <li> <a href="#B4">B4</a></li>
  <li> <a href="#WRAPUP">WRAPUP</a></li>

  << include r2lab/tutos-index.html >>
</ul>


<div id="contents" class="tab-content" markdown="1">

<!------------ INTRO ------------>
<div id="INTRO" class="tab-pane fade in active" markdown="1">

### Prerequisites

For this series of experiments, we make the same assumptions as in the
previous series. In a nutshell, we expect you have a valid
reservation, and the 2 nodes `fit01`and `fit02` are properly loaded with
the default image, and turned on of course.

Please [visit this page](http://r2lab.inria.fr/tuto-400-ping.md#INTRO)
to review how to reach that point, if necessary.

### Objectives

In this series we will start playing with the wireless interfaces. Of
course a minimal background is assumed in terms of dealing with
wireless interfaces under linux; further information can be found at
the following locations :

* we recommend to see [this quick introduction to `iw`, that is
  instrumental in these
  tasks](https://wireless.wiki.kernel.org/en/users/documentation/iw)

* as well as [this helpful page on how to use `iw` if you were more
  familiar with `iwconfig` that is now considered
  obsolete](https://wireless.wiki.kernel.org/en/users/documentation/iw/replace-iwconfig) -
  much like `ip` has now replaced `ifconfig`.

### `nepi-ng`

Now as far as `nepi-ng` is concerned, in the previous series we have
seen ways to run remotely simple commands. In this section we will see
simple means to come up with more complex logic, simply by using shell
scripts that are pushed remotely under the hood before they are
triggered. This is what the `RunString` and `RunScript` classes are
about. Let us [see them in action right away](javascript:open_tab('B1')).


</div>

<!------------ B1 ------------>
<div id="B1" class="tab-pane fade" markdown="1">

### Objective

We are going to run the exact same experiment [as in the previous run
A5](tuto-400-ping.md#A5), that is to say a simple ping triggered on
`fit01` towards `fit02`, but this time on one of the **wireless
interfaces**. 

What changes then, as compared with our previous experiment, is that
we cannot anymore simply run the predefined convenience command
`turn-on-data`, and we are going to have to put a little more work in this
step.

We are going to configure a small *ad hoc* network between both nodes,
using their Atheros WiFi card, and this is the purpose of the bash
shell script named `turn_on_wireless_script`; as you will see, this
script uses some hard-wired settings like the channel and SSID, but
you can easily tweak the code so as to make this a parameter.

### New features

The `B1 code` below exhibits the use of a new class, `RunString`,
which is a very convenient variation around the `Run` class.

Instead of remotely invoking a command that is supposed to be
available there already, like we have done so far when e.g. invoking
`ping` or even `turn-on-data`, `RunString` allows you to invoke a command
that we provide **as a python variable**.

This means that we can write our own shell snippet, in charge of
creating a small ad-hoc network, and embed this script right inside
our nepi-ng script; see the `turn_on_wireless_script` variable in the
code below.

See also how the `init_node_01` job now uses `RunString` to pass it
python variables as arguments. For example this is how
`turn_on_wireless_script` gets passed the right IP address for each node.

As you will see in the sample output below, it takes some time for the
IP connectivity to be established after the driver is configured.

### The code

<< codeview B1 A5-ping.py B1-wireless.py >>

### Sample output

    $ python3 B1-wireless.py
    faraday.inria.fr:Checking current reservation for onelab.your.slice.name OK
    fit02:turn-off-wireless: driver iwlwifi not used
    fit02:turn-off-wireless: shutting down device atheros
    fit01:turn-off-wireless: driver iwlwifi not used
    fit01:turn-off-wireless: shutting down device atheros
    fit02:turn-off-wireless: removing driver ath9k
    fit01:turn-off-wireless: removing driver ath9k
    fit02:loading module ath9k
    fit01:loading module ath9k
    fit02:configuring interface atheros
    fit01:configuring interface atheros
    fit01:PING 10.0.0.2 (10.0.0.2) from 10.0.0.1 atheros: 56(84) bytes of data.
    fit01:From 10.0.0.1 icmp_seq=1 Destination Host Unreachable
    fit01:From 10.0.0.1 icmp_seq=2 Destination Host Unreachable
    fit01:From 10.0.0.1 icmp_seq=3 Destination Host Unreachable
    fit01:From 10.0.0.1 icmp_seq=4 Destination Host Unreachable
    fit01:From 10.0.0.1 icmp_seq=5 Destination Host Unreachable
    fit01:From 10.0.0.1 icmp_seq=6 Destination Host Unreachable
    fit01:From 10.0.0.1 icmp_seq=7 Destination Host Unreachable
    fit01:From 10.0.0.1 icmp_seq=8 Destination Host Unreachable
    fit01:From 10.0.0.1 icmp_seq=9 Destination Host Unreachable
    fit01:64 bytes from 10.0.0.2: icmp_seq=10 ttl=64 time=4.71 ms
    fit01:64 bytes from 10.0.0.2: icmp_seq=11 ttl=64 time=2.32 ms
    fit01:64 bytes from 10.0.0.2: icmp_seq=12 ttl=64 time=2.33 ms
    fit01:64 bytes from 10.0.0.2: icmp_seq=13 ttl=64 time=2.35 ms
    fit01:64 bytes from 10.0.0.2: icmp_seq=14 ttl=64 time=2.31 ms
    fit01:64 bytes from 10.0.0.2: icmp_seq=15 ttl=64 time=2.31 ms
    fit01:64 bytes from 10.0.0.2: icmp_seq=16 ttl=64 time=2.35 ms
    fit01:64 bytes from 10.0.0.2: icmp_seq=17 ttl=64 time=1.77 ms
    fit01:64 bytes from 10.0.0.2: icmp_seq=18 ttl=64 time=1.45 ms
    fit01:64 bytes from 10.0.0.2: icmp_seq=19 ttl=64 time=1.42 ms
    fit01:64 bytes from 10.0.0.2: icmp_seq=20 ttl=64 time=1.43 ms
    fit01:
    fit01:--- 10.0.0.2 ping statistics ---
    fit01:20 packets transmitted, 11 received, +9 errors, 45% packet loss, time 19062ms
    fit01:rtt min/avg/max/mdev = 1.421/2.253/4.714/0.871 ms, pipe 3

### Next

Let us see some variants on that theme [in the next tab](javascript:open_tab('B2'))

</div>

<!------------ B2 ------------>
<div id="B2" class="tab-pane fade" markdown="1">

### Objective

In this new variant, we are going to illustrate a few convenient tricks:

* we add a new option to the script so that one can choose, right on
  the command line, whether we want to use the intel or the atheros
  WiFi card; this simply relies on the [standard `argparse`
  module](https://docs.python.org/3/library/argparse.html) that we
  have already used for other options, the only new thing being the
  use of the `choices` keyword, so that only the 2 supported driver
  names can be used;

* more interestingly, we can remove the `wireless_interface` variable
  from that script altogether, thanks to a shell utilily available on
  all nodes and named `wait-for-interface-on-driver`. This shell
  function returns the name of the network interface associated with a
  given driver name, so it is enough to load, say, module `ath9k` and
  let this function figure out that the actual interface name is
  `atheros`;

* in much the same way, we will remove the need to pass an IP address
  to the `turn_on_wireless_script`, by computing this address based on
  the node rank in r2lab, using another convenience tool named
  `r2lab-ip`; there actually are 2 similar functions available on each node

  * `r2lab-ip`: will return the number of the current node, under **1 or 2 digits**;
    for example on node 8, this returns `8`;
    this is suitable to build IP addresses;


  * `r2lab-id`: will return the number of the current node, but **always in 2 digits**;
    for example on node 8, this returns `08`;
    this is suitable to build hostnames; so for example you would do

# 

    my_data_hostname="data$(r2lab-id)"
    echo $my_data_hostname
    data08
    my_wireless_ip_address="10.0.0.$(r2lab-ip)"
    echo my_wireless_ip_address
    10.0.0.8

* finally, this new script displays the outputs of the ssh commands
  with a slightly different format, in that every line will now
  receive a timestamp in addition to the hostname. This is achieved
  through the use of the `TimeColonFormatter()` class; we create one
  instance of this class for each instance of `SshNode`.

So for example we would issue lines like

    14-37-28:fit01:turn-off-wireless: shutting down device intel

  instead of just

    fit01:turn-off-wireless: shutting down device intel

About that last point, note that other types of formatters are
  available, that will let you store output in a given directory, and
  in files named after each individual hostname. See [this
  page](http://nepi-ng.inria.fr/apssh/API.html#module-apssh.formatters)
  for more info on other available formatters.


### The code

<< codeview B2 B1-wireless.py B2-wireless.py >>

### Sample output

    $ python3 B2-wireless.py
    16-56-38:faraday.inria.fr:Checking current reservation for onelab.inria.r2lab.tutorial OK
    16-56-39:fit02:Using id=02 and fitid=fit02 - from hostname
    16-56-39:fit02:turn-off-wireless: driver iwlwifi not used
    16-56-39:fit01:Using id=01 and fitid=fit01 - from hostname
    16-56-39:fit02:turn-off-wireless: shutting down device atheros
    16-56-39:fit01:turn-off-wireless: driver iwlwifi not used
    16-56-39:fit01:turn-off-wireless: shutting down device atheros
    16-56-39:fit02:turn-off-wireless: removing driver ath9k
    16-56-39:fit01:turn-off-wireless: removing driver ath9k
    16-56-39:fit02:loading module ath9k
    16-56-39:fit01:loading module ath9k
    16-56-41:fit02:Using device atheros
    16-56-41:fit02:configuring interface atheros
    16-56-41:fit01:Using device atheros
    16-56-41:fit01:configuring interface atheros
    16-56-44:fit01:PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
    16-56-44:fit01:From 10.0.0.1 icmp_seq=1 Destination Host Unreachable
    16-56-44:fit01:From 10.0.0.1 icmp_seq=2 Destination Host Unreachable
    16-56-44:fit01:From 10.0.0.1 icmp_seq=3 Destination Host Unreachable
    16-56-47:fit01:From 10.0.0.1 icmp_seq=4 Destination Host Unreachable
    16-56-47:fit01:From 10.0.0.1 icmp_seq=5 Destination Host Unreachable
    16-56-47:fit01:From 10.0.0.1 icmp_seq=6 Destination Host Unreachable
    16-56-50:fit01:From 10.0.0.1 icmp_seq=7 Destination Host Unreachable
    16-56-50:fit01:From 10.0.0.1 icmp_seq=8 Destination Host Unreachable
    16-56-50:fit01:From 10.0.0.1 icmp_seq=9 Destination Host Unreachable
    16-56-50:fit01:64 bytes from 10.0.0.2: icmp_seq=10 ttl=64 time=4.45 ms
    16-56-51:fit01:64 bytes from 10.0.0.2: icmp_seq=11 ttl=64 time=2.12 ms
    16-56-53:fit01:64 bytes from 10.0.0.2: icmp_seq=12 ttl=64 time=2.12 ms
    16-56-53:fit01:64 bytes from 10.0.0.2: icmp_seq=13 ttl=64 time=2.13 ms
    16-56-54:fit01:64 bytes from 10.0.0.2: icmp_seq=14 ttl=64 time=2.10 ms
    16-56-55:fit01:64 bytes from 10.0.0.2: icmp_seq=15 ttl=64 time=2.44 ms
    16-56-56:fit01:64 bytes from 10.0.0.2: icmp_seq=16 ttl=64 time=2.13 ms
    16-56-57:fit01:64 bytes from 10.0.0.2: icmp_seq=17 ttl=64 time=1.49 ms
    16-56-58:fit01:64 bytes from 10.0.0.2: icmp_seq=18 ttl=64 time=1.59 ms
    16-56-59:fit01:64 bytes from 10.0.0.2: icmp_seq=19 ttl=64 time=1.48 ms
    16-57-00:fit01:64 bytes from 10.0.0.2: icmp_seq=20 ttl=64 time=1.56 ms
    16-57-00:fit01:
    16-57-00:fit01:--- 10.0.0.2 ping statistics ---
    16-57-00:fit01:20 packets transmitted, 11 received, +9 errors, 45% packet loss, time 19060ms
    16-57-00:fit01:rtt min/avg/max/mdev = 1.489/2.152/4.455/0.795 ms, pipe 3
    
### Next

In [the next variant](javascript:open_tab('B3')), we are going to see
how we can better esimate the time it takes for the ad hoc network to
actually come up.

</div>

<!------------ B3 ------------>
<div id="B3" class="tab-pane fade" markdown="1">

### Objective

In this variant, we will see how we can even design our experiment so
that all **the shell code** goes **in a single file**, working as a
companion for the python script that will only deal with overall
logic.

Our pretext for doing so is that we would like to better understand
the startup sequence observed in the previous runs B1 and B2. And for
doing that it is not good enough to just run `ping` like we did, but
instead we would need run something a little more elaborate - that
we'll write in shell.

As much as it is convenient to have the ability to insert shell script
right in the python code, when things become more complex, the shell
code tends to become in the way.

So, two features are at work in the following code

* Using `RunScript` instead of `RunString` as a way to define commands
  allows us to separate the shell script in a separate file.

* Also you can note at the end of the shell script, a very simple
  trick that lets you group any number of functions in a shell script,
  and call each individual function by just stating its name and arguments.

In other words, it means that if you write the following in a file named `myscript.sh`:

<code>
<pre>
<<include myscript.sh >>
</pre>
</code>

and then you invoke `myscript.sh foo 1 2 "3 4"` you will get this ouput

    $ myscript.sh foo 1 2 "3 4"
    in function foo
    foo arg:  1
    foo arg:  2
    foo arg:  3 4

### The code

Make sure you download both files in the same location before trying to run the python script.

<< codeview B3 B2-wireless.py B3-wireless.py >>

<< codeview B3SHELL B3-wireless.sh >>

### Sample output

    $ python3 B3-wireless.py
    14-08-35:faraday.inria.fr:Checking current reservation for onelab.inria.r2lab.tutorial OK
    14-08-36:fit02:turn-off-wireless: driver iwlwifi not used
    14-08-36:fit02:turn-off-wireless: shutting down device atheros
    14-08-36:fit01:turn-off-wireless: driver iwlwifi not used
    14-08-36:fit01:turn-off-wireless: shutting down device atheros
    14-08-36:fit01:turn-off-wireless: removing driver ath9k
    14-08-36:fit02:turn-off-wireless: removing driver ath9k
    14-08-36:fit01:loading module ath9k
    14-08-36:fit02:loading module ath9k
    14-08-38:fit01:Using device atheros
    14-08-38:fit01:configuring interface atheros
    14-08-38:fit02:Using device atheros
    14-08-38:fit02:configuring interface atheros
    14-08-40:fit01:10.0.0.2 not reachable
    14-08-41:fit01:10.0.0.2 not reachable
    14-08-42:fit01:10.0.0.2 not reachable
    14-08-43:fit01:10.0.0.2 not reachable
    14-08-44:fit01:10.0.0.2 not reachable
    14-08-45:fit01:10.0.0.2 not reachable
    14-08-46:fit01:10.0.0.2 not reachable
    14-08-47:fit01:10.0.0.2 not reachable
    14-08-47:fit01:fit01 -> 10.0.0.2: SUCCESS after 8s

### Next

Let us conclude this series with [an example that adds a
cyclic task](javascript:open_tab('B4')) to this scenario.

</div>

<!------------ B4 ------------>
<div id="B4" class="tab-pane fade" markdown="1">

### Objective

In this final example in the series, we will just for fun add an
infinite cyclic task in the scheduler. Here we will just write a TICK
mark every second, but this technique is most useful for consuming
events in a message queue, or any other similar approach.

The trick is just to use plain `Job` class from `asynciojobs`, which
expects a plain `asyncio` coroutine, that we implement as
`infinite_clock()`. We just need to define the asociated job
`clock_job` with `forever = True`, which tells the scheduler that this
job never ends, so it's no use waiting for it to complete.

### The code

<< codeview B4 B3-wireless.py B4-wireless.py >>

### Sample output

    $ python3 B4-wireless.py
    --- TICK - 14:09:21
    --- TICK - 14:09:22
    --- TICK - 14:09:23
    14-09-24:faraday.inria.fr:Checking current reservation for onelab.inria.r2lab.tutorial OK
    --- TICK - 14:09:24
    14-09-25:fit02:turn-off-wireless: driver iwlwifi not used
    14-09-25:fit02:turn-off-wireless: shutting down device atheros
    14-09-25:fit01:turn-off-wireless: driver iwlwifi not used
    14-09-25:fit01:turn-off-wireless: shutting down device atheros
    14-09-25:fit02:turn-off-wireless: removing driver ath9k
    14-09-25:fit01:turn-off-wireless: removing driver ath9k
    14-09-25:fit02:loading module ath9k
    --- TICK - 14:09:25
    14-09-26:fit01:loading module ath9k
    --- TICK - 14:09:26
    --- TICK - 14:09:28
    14-09-28:fit02:Using device atheros
    14-09-28:fit02:configuring interface atheros
    14-09-28:fit01:Using device atheros
    14-09-28:fit01:configuring interface atheros
    --- TICK - 14:09:29
    --- TICK - 14:09:30
    14-09-30:fit01:10.0.0.2 not reachable
    --- TICK - 14:09:31
    14-09-31:fit01:10.0.0.2 not reachable
    --- TICK - 14:09:32
    14-09-32:fit01:10.0.0.2 not reachable
    14-09-32:fit01:10.0.0.2 not reachable
    --- TICK - 14:09:33
    14-09-33:fit01:10.0.0.2 not reachable
    --- TICK - 14:09:34
    --- TICK - 14:09:35
    14-09-35:fit01:10.0.0.2 not reachable
    --- TICK - 14:09:36
    14-09-36:fit01:10.0.0.2 not reachable
    --- TICK - 14:09:37
    14-09-37:fit01:10.0.0.2 not reachable
    --- TICK - 14:09:38
    14-09-38:fit01:10.0.0.2 not reachable
    14-09-38:fit01:SUCCESS after 9s

</div>

<!------------ WRAPUP ------------>
<div id="WRAPUP" class="tab-pane fade" markdown="1">

We now know how to:

* have local scripts, written either as plain shell scripts (using
  `RunScript`) or embedded in python strings (using `RunString`),
  executed remotely

* obtain remote outputs using alternate formats, using
  e.g. `TimeColonFormatter`; see [this
  page](http://nepi-ng.inria.fr/apssh/API.html#module-apssh.formatters)
  for more info on other available formatters.

* run infinite jobs, that will get properly terminated when all the
  finite jobs in the scenario oare done.

In [the next series of tutorials](tuto-600-files.md), we will learn
more about transferring files back and forth.

</div>

</div> <!-- end div contents -->
