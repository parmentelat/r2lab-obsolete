title: nepi-ng - in real scale
tab: tutorial
skip_header: True

<script src="/assets/r2lab/open-tab.js"></script>
<script src="/assets/js/diff.js"></script>
<script src="/assets/r2lab/r2lab-diff.js"></script>
<style>@import url("/assets/r2lab/r2lab-diff.css")</style>

<ul class="nav nav-tabs">
  <li class="active"> <a href="#INTRO">INTRO</a> </li>
  <li> <a href="#MULTI_PING">MULTI_PING</a></li>

  << include r2lab/tutos-index.html >>
</ul>

<div id="contents" class="tab-content" markdown="1">

<!------------ INTRO ------------>
<div id="INTRO" class="tab-pane fade in active" markdown="1">

We have grouped in this page a few more elaborate examples:

* a `multi-ping` example that in particular deals with a variable
  number of nodes, and runs ping beween each couple of nodes.

* more examples are expected in the future...

</div>

<!------------ MULTI_PING ------------>
<div id="MULTI_PING" class="tab-pane fade" markdown="1">

### Objective

This script is an extension of the B series, but the number of nodes
involved is now a parameter in the experiment (the `--max` option that
defaults to 5).

We will thus use the `m` first nodes in the system, and
* initialize the wireless ad-hoc network, on all those node, like we had done in the `B` series,
* and then run as many pings as there are couples of nodes - that is to say `m*(m-1)/2`  pings
* the results of these are then retrieved locally in files names `PING-i-j`

All the pings are essentially running at the same time here.  This is
why, as you will realize if you try to run the script yourself, the
script can cope with something around 8 nodes.

With a higher number of nodes, there is a too great need of open
connections at the same time; the script stops to behave as
expected, and a subtler variant is needed for this situation.

### The code

<< codeview MULTI_PING multi-ping.py >>

### Sample output

</div>

</div> <!-- end div contents -->
