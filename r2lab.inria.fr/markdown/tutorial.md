title: The R2lab Tutorials
subtitle: Let's get you started
tab: tutorial
skip_header: True

<script src="/assets/r2lab/open-tab.js"></script>
<script src="/assets/js/diff.js"></script>
<script src="/assets/r2lab/r2lab-diff.js"></script>
<style>@import url("/assets/r2lab/r2lab-diff.css")</style>


<ul class="nav nav-tabs">
  <li class="active"> <a href="#INTRO">INTRO</a> </li>
  <li> <a href="#CONTACT">CONTACT</a> </li>

  << include r2lab/tutos-index.html >>
</ul>

<div id="contents" class="tab-content" markdown="1">

<!------------ INTRO ------------>
<div id="INTRO" class="tab-pane fade in active" markdown="1">

All this contents is accessible through the **TUTORIALS INDEX** dropdown that appears on all the tutorial pages on the upper right end of the navbar.

### Infrastructure

#### [Sign up for a OneLab account](tuto-100-registration.md)

*  All information about how to register and schedule a node

#### [Shell tools](tuto-200-shell-tools.md) available in the R2lab gateway

*  Discover how to do basic control of the nodes by logging in at the
  `faraday.inria.fr` gateway from a regular `ssh` session :
* how to check for the nodes status, leases, images, and phones even.
  
### Examples of experimentation scripts with `nepi-ng`

#### [`nepi-ng`: install](tuto-300-nepi-ng-install.md)

* How to install `nepi-ng` on your laptop

#### [`nepi-ng`: the basics](tuto-400-ping.md) - a.k.a. the **A** series

* A couple examples to get started with the `nepi-ng` network tool:
* [A1](tuto-400-ping.md#A1) : simplest way to run a simple ping from `faraday.inria.fr` to `google.fr`
* [A2](tuto-400-ping.md#A2) : same functions, but can pass a slice name on the command line
* [A3](tuto-400-ping.md#A3) : run the ping from a node instead of from the gateway
* [A4](tuto-400-ping.md#A4) : check for a valid reservation
* [A5](tuto-400-ping.md#A5) : run ping between two nodes inside the chamber, on the wired network

#### [`nepi-ng` : wireless](tuto-500-wireless.md) - a.k.a. the **B** series

*  A few more pings to see how one can initialize and configure wireless links
* [B1](tuto-500-wireless.md#B1) : like A5, but on a wireless ad hoc network
* [B2](tuto-500-wireless.md#B2) : same scenario, simplified by using `r2lab-id` 
* [B3](tuto-500-wireless.md#B3) : same scenario, but extract all the shell code in a single external file
* [B4](tuto-500-wireless.md#B4) : add an infinite loop that prints out TICK every second

#### [`nepi-ng` : file exchange](tuto-600-files.md) - a.k.a. the **C** series; a full loop doing file transfers, i.e.:

* A set of examples that deal with file transfers, using SFTP to and from the nodes; and that show an example of file transfer between two nodes
* [C1](tuto-600-files.md#C1) : a random file is produced locally,
* [C2](tuto-600-files.md#C2) : then pushed on one node, transferred to a second node using netcat over the wired network,
* [C3](tuto-600-files.md#C3) : and retrieved back on the local laptop where it is compared with the original;
* [C4](tuto-600-files.md#C4) : this extended version knows how to load images on the nodes before running C3.
* [C2bis](tuto-600-files.md#C2bis) : a variant on C2, that deals with a service that is started and stopped in sync with another job

#### Guidelines for [troubleshooting a `nepi-ng` script](tuto-700-troubleshooting.md) 

* [COMMON_MISTAKES](tuto-700-troubleshooting.md#COMMON_MISTAKES) how to check for common mistakes
* [CODE_UPDATE](tuto-700-troubleshooting.md#CODE_UPDATE) how to check your software environment
* [VERBOSITY](tuto-700-troubleshooting.md#VERBOSITY) how to enable more verbosity

#### [`nepi-ng`: real scale examples](tuto-750-real-scale.md)

* [MULTI_PING](tuto-750-real-scale.md#MULTI_PING) : dealing with any
  number of nodes, run pings between all couples of nodes.

### Other stuff

#### [R2lab and OpenAirInterface](tuto-800-oai.md)

* Some indications on the features present on R2lab to deploy experiments based on OpenAirInterface.

#### [Video tutorials on YouTube](tuto-900-youtube.md)

  * [End-to-End Experiment](tuto-900-youtube.md#AOA) : Running a wireless
    experiment end-to-end.
  * [OAI 5G experiment](tuto-900-youtube.md#OAI) : Setting up an
    OpenAirInterface-based 5G infrastructure, and a tour in the
    chamber using Skype on a commercial NEXUS phone.

</div>

<!------------ CONTACT ------------>
<div id="CONTACT" class="tab-pane fade" markdown="1">

### Contacts

If you have any issue with this tutorial, or with using R2lab more
generally, please contact us at
[`fit-r2lab-users@inria.fr`](mailto:fit-r2lab-users@inria.fr)

You can subscribe to that `fit-r2lab-users` discussion list by sending
an email to `sympa@inria.fr` with `subscribe fit-r2lab-users` in the
body of the message.

You can do this by
[simply clicking this link](mailto:sympa@inria.fr?subject=subscribe fit-r2lab-users)


### Chat room

We use the `#r2lab` channel on freenode; also once you are logged into
the website, in the `RUN` page, you will find on top of the page a
button that will let you join this chat room in a single click.

</div>

</div> <!-- end div contents -->
