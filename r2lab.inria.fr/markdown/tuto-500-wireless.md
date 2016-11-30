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
  <li> <a href="#B5">B5</a></li>
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

* finally, this new script displays the outputs of the ssh
  commands with a slightly different format, in that every line will
  now receive a timestamp in addition to the hostname. So for example we would issue lines like

    14-37-28:fit01:turn-off-wireless: shutting down device intel

  instead of just

    fit01:turn-off-wireless: shutting down device intel

This is achieved through the use of the `TimeColonFormatter()` class; we create one instance of this class for each instance of `SshNode`


### The code

<< codeview B2 B1-wireless.py B2-wireless.py >>

### Sample output

### Next
[](javascript:open_tab(''))

</div>

<!------------ B3 ------------>
<div id="B3" class="tab-pane fade" markdown="1">

### Objective

### The code

<< codeview B3 B2-wireless.py B3-wireless.py >>

### Sample output

### Next
[](javascript:open_tab(''))

</div>

<!------------ B4 ------------>
<div id="B4" class="tab-pane fade" markdown="1">

### Objective

### The code

<< codeview B4 B3-wireless.py B4-wireless.py >>

### Sample output

### Next
[](javascript:open_tab(''))

</div>

<!------------ B5 ------------>
<div id="B5" class="tab-pane fade" markdown="1">

### Objective

### The code

<< codeview B5 B4-wireless.py B5-wireless.py >>

### Sample output

### Next
[](javascript:open_tab(''))

</div>

<!------------ WRAPUP ------------>
<div id="WRAPUP" class="tab-pane fade" markdown="1">

</div>

</div> <!-- end div contents -->
