title: R2lab Status
tab: status
skip_header: yes

This page gives you live details on the individual nodes in the R2lab testbed.

---
## Overall status (livemap)

<a name="livemap"></a>
For accurate dimensions of the room, please see the [static blueprint
at the bottom of this page](#accurate-layout).

<div id="livemap_container"></div>
<script type="text/javascript" src="/assets/r2lab/livemap.js"></script>
<script>livemap_show_rxtx_rates = true;</script>
<style type="text/css"> @import url("/assets/r2lab/livemap.css"); </style>

#### Legend

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

***

## Detailed status (livetable)

<a name="livetable"></a>

<br />

<table class="table table-condensed" id='livetable_container'> </table>
<script type="text/javascript" src="/assets/r2lab/livetable.js"></script>
<script>livetable_show_rxtx_rates = true;</script>
<style type="text/css"> @import url("/assets/r2lab/livetable.css"); </style>

#### Legend

* The <b>availability</b> column: 
  tells you whether the node is usable or not. If not, this means you should not try to use that node for your experiment, as it may be physically powered off, or otherwise behave erratically.
* The <b>on/off</b> column:
  reports if the node is currently turned on or off.
* The <b>ping</b> column: 
  does the node answers a single ping at the wired network interface.
* The <b>O.S</b> column:
  the nature of the O.S. that was **last seen** on that node (i.e. even if the node is currently off).

Also please note that 

 * Clicking anywhere in the header will focus on the nodes that are currently up; a second click returns to full mode.
 * Clicking a node badge will take it off the list

***

### Accurate layout

Below is the ground plan layout of the anechoic room which provides thirty-seven wireless nodes distributed in a **≈ 90m<sup>2</sup>** room.

The nodes are arranged in a grid with ≈1.0m (vertical) and ≈1.15m (horizontal) of distance between them, except for the nodes 12, 16, 17, 20 and 23, 24, 27 which are the nodes surrounding the two columns of the room.

<left>
	<img src="/assets/img/status.png" style="width:950px; height:592px;"/><br>
	<!-- <center> Fig. 1 - Resources status</center> -->
</left>

<br />

