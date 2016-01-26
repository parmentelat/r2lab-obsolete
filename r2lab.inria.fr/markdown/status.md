title: R2lab Status
tab: status
---

R2lab testbed project offers a high quality anechoic room for your experiments. Following are the details of the anechoic room.


<div class="alert alert-danger" role="alert" markdown="1">
**Important note!**

R2lab platform is reset every night. A time slot from **3AM** until
**4AM** (GMT +1) is reserved to execute this routine.

Please, make sure all your experiments are saved before. You can check
[here](tuto-02-shell-tools.md#main) how to do it.
</div>

### Overall status (livemap)

Frequently a routine checks the availability of our nodes platform. In
order to allow real time and multiple information concerning the R2lab
platform, our live map keeps users posted about the state of each
node concerning technical infos, incidents and operational details:

* A round shape with a O.S. icon (fedora or ubuntu) informs that the node is turned on, running the
  referenced O.S. and reachable through ssh.
* If only a number appears, this node is turned off.
* Smaller bullets indicate intermediate / temporary status
  * a small gray bullet means the node is turned ON but does not answer to ping
  (usually this means the node is being turned on or off)
  * a slightly larger and green-ish bullet means the node answers to ping but cannot be
  reached through ssh yet (usually this means an image is being
  burned).
* Finally, if a node is hidden behind a large red circle, it means it
  is out of order, and altogether unavailable.

For accurate dimensions of the room, please see the [static blueprint
at the bottom of this page](#accurate-layout).

<div id="livemap_container"></div>
<script type="text/javascript" src="/plugins/livemap.js"></script>
<script>livemap_show_rxtx_rates = true;</script>
<style type="text/css"> @import url("/plugins/livemap.css"); </style>

***

### Detailed status (livetable)

Complementary to the live map above, this status table presents the same status information in an alternative format.

* The <b>availability</b> column: 
  tells you whether the node is usable or not. If not, this means you should not try to use that node for your experiment, as it may be physically powered off, or otherwise behave erratically.
* The <b>on/off</b> column:
  reports if the node is currently turned on or off.
* The <b>ping</b> column: 
  does the node answers a single ping at the wired network interface.
* The <b>O.S</b> column:
  the nature of the O.S. that was last seen on that node.

Also please note that 

 * Clicking anywhere in the header will focus on the nodes that are currently up; a second click returns to full mode.
 * Clicking a node badge will take it off the list

<br />

<table class="table table-condensed" id='livetable_container'> </table>
<script type="text/javascript" src="/plugins/livetable.js"></script>
<script>livetable_show_rxtx_rates = true;</script>
<style type="text/css"> @import url("/plugins/livetable.css"); </style>

<br />

***

### Accurate layout

Below is the ground plan layout of the anechoic room which provides thirty-seven wireless nodes distributed in a **≈ 90m<sup>2</sup>** room.

The nodes are arranged in a grid with ≈1.0m (vertical) and ≈1.15m (horizontal) of distance between them, except for the nodes 12, 16, 17, 20 and 23, 24, 27 which are the nodes surrounding the two columns of the room.

<left>
	<img src="/assets/img/status.png" style="width:950px; height:592px;"/><br>
	<!-- <center> Fig. 1 - Resources status</center> -->
</left>

<br />

