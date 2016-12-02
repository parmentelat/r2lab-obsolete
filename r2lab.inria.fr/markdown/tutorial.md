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

All this contents is accessible through the 'TUTORIALS INDEX' dropdown that appears on all the tutorial pages on the upper right end of the navbar.

### Infrastructure

#### [Sign up for a OneLab account](tuto-100-registration.md)

  All information about how to register and schedule a node

#### [Shell tools](tuto-200-shell-tools.md) available in the R2lab gateway

  Discover how to do basic control of the nodes by logging in at the
  `faraday.inria.fr` gateway from a regular `ssh` session: how to
  check for control nodes status, leases, images, and phones even.
  
### Examples of experimentation scripts with `nepi-ng`

#### [`nepi-ng`: install](tuto-300-nepi-ng-install.md)

#### [`nepi-ng`: ping examples](tuto-400-ping.md) - a.k.a. the **A** series

  A couple examples to get started with the `nepi-ng` network tool

#### [`nepi-ng` : wireless](tuto-500-wireless.md) - a.k.a. the **B** series

  A few more pings to see how one can initialize and configure wireless links

#### [`nepi-ng` : file exchange](tuto-600-files.md) - a.k.a. the **C** series

A full loop doing file transfers: a random file is produced locally,
then pushed on one node, transferred to a second node using netcat
over the wired network, retrieved back on the local laptop where it is
compared with the original.

#### [`nepi-ng`: miscell](tuto-700-miscell.md) 

Additional resources here, most importantly

* guidelines on troubleshooting a `nepi-ng` script

* how to load images on the nodes in a nepi-ng script

* a more realistic script:
dealing with any number of nodes, and running pings between all couples of nodes.

### Other stuff

#### [R2lab and OpenAirInterface](tuto-800-oai.md)

  Some indications on the features present on R2lab to deploy experiments based on OpenAirInterface.

#### Video tutorials on YouTube

  * [End-to-End Experiment](tuto-900-youtube.md) : Running a wireless
    experiment end-to-end.

  * [OAI 5G experiment](tuto-900-youtube.md) : Setting up an
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


</div>

</div> <!-- end div contents -->
