title: Status
tab: status
---

R2Lab testbed project offers a high quality anechoic room for your experiments. Following are the details of the anechoic room.

### Overall status (livemap)

Frequently a routine checks the availability of our nodes platform. In
order to allow real time and multiple information concerning R2lab
platform, our live map keeps users posted about the state of each
node concerning technical infos, incidents and operational details:

* A round O.S. icon informs that the node is turned on, running the
  referenced O.S. and reachable through ssh.
* The node is turned off when only the number is presented in the map.
* Smaller bullets indicate intermediate / temporary status
  * a small gray bullet means the node is turned ON but does not answer ping
  (usually this means the node is turning on or off)
  * a slightly larger and green bullet means the nodes answers pings but cannot be
  reached through ssh yet (usually this means an image is being
  burned).
* Finally, if a node is hidden behind a large red circle, it means it
  is out of order, and altogether unavailable.

For accurate dimensions of the room, please see the [static blueprint
at the bottom of this page](#accurate-layout).

<div id="livemap_container"></div>
<script type="text/javascript" src="plugins/livemap.js"></script>
<script>livemap_show_rxtx_rates = true;</script>
<style type="text/css"> @import url("plugins/livemap.css"); </style>

***

### Detailed status (livetable)

Complementary to the live map above, this status table present an alternative format the queries results.
- The <b>availability</b> column: 
	Reports that the node are controllable or not. In fail case the node could be physically powered off or in maintenance.
- The <b>on/off</b> column:
	Reports that the node is ready to be used or not.
- The <b>ping</b> column: 
	Reports that the node answers a single ping at the experiment interface.
- The <b>O.S</b> column:
	Reports that O.S. that was last seen on that node.
<br />


<table class="table table-condensed" id='livetable_container'> </table>
<script type="text/javascript" src="plugins/livetable.js"></script>
<script>livetable_show_rxtx_rates = true;</script>
<style type="text/css"> @import url("plugins/livetable.css"); </style>

<br />

***

### Accurate layout

Below is the ground plan layout of the anechoic room which provides thirty-seven wireless nodes distributed in a **≈ 90m<sup>2</sup>** room.

The nodes are arranged in grid with ≈1.0m (vertical) and ≈1.15m (horizontal) of distance between them, except by the nodes 12, 16, 17, 20 and 23, 24, 27 which are the nodes surrounding the columns room.

<left>
	<img src="assets/img/status.png" style="width:950px; height:592px;"/><br>
	<!-- <center> Fig. 1 - Resources status</center> -->
</left>

<br />

