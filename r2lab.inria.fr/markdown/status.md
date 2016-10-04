title: R2lab Status
tab: status
skip_header: yes

This page gives you live details on the individual nodes in the R2lab testbed.

---
## Overall status (livemap)

<a name="livemap"></a>
For accurate dimensions of the room, please see the [static blueprint
at the bottom of this page](#accurate-layout)

For more details about each node, please click in the node number/badge/icon.

<div class="row" id="all">
  <div class="col-lg-2"></div>
  <div class="col-lg-10">
    <div id="livemap_container"></div>
    <script type="text/javascript" src="/assets/r2lab/livemap.js"></script>
    <script>
    //livemap_show_rxtx_rates = true;
    </script>
    <style type="text/css"> @import url("/assets/r2lab/livemap.css"); </style>
  </div>
</div>


#### Legend

* A round shape with a O.S. icon (fedora or ubuntu) informs that the node is turned on, running the
  referenced O.S. and reachable through ssh.
* If only a number appears, this node is turned off.
* Smaller bullets indicate intermediate / temporary status
  * a small gray bullet means the node is turned ON but does not answer to ping
  (usually this means the node is being turned on or off)
  * a slightly larger and green-ish bullet means the node answers to ping but cannot be
  reached through ssh yet (usually this means an image is being
  loaded).
* Finally, if a node is hidden behind a large red circle, it means it
  is out of order, and altogether unavailable.

***

## Detailed status (livetable)

<a name="livetable"></a>

<br />

<div class="row" id="all">
  <div class="col-lg-12">
    <table class="table table-condensed" id='livetable_container'> </table>
    <script type="text/javascript" src="/assets/r2lab/livetable.js"></script>
    <script>
    //livetable_show_rxtx_rates = true;
    </script>
    <style type="text/css"> @import url("/assets/r2lab/livetable.css"); </style>
  </div>
</div>

#### Legend

* The ***availability*** column:
  tells you whether the node is usable or not. If not, this means you should not try to use that node for your experiment, as it may be physically powered off, or otherwise behave erratically.
* The ***on/off*** column:
  reports if the node is currently turned on or off.
* The ***ping*** column:
  says whether the node answers a single ping at the wired network interface or not.
* The ***Last O.S*** column:
  the nature of the O.S. that was **last seen** on that node (i.e. even if the node is currently off).
* The ***wlan...*** columns provide measured bandwidth in reception and transmission on the 2 radio interfaces. *This is only indicative* and inaccurate; experiments should probably measure this themselves if it is a crucial information. Also note that this feature does not work on images that use other names for the wireless devices.

Also please note that

 * Clicking anywhere in the header will focus on the nodes that are currently up; a second click returns to full mode.
 * Clicking a node badge will take it off the list

***

### Accurate layout

Below is the ground plan layout of the anechoic room which provides thirty-seven wireless nodes distributed in a **≈ 90m<sup>2</sup>** room.

The nodes are arranged in a grid with ≈1.0m (vertical) and ≈1.15m (horizontal) of distance between them, except for the nodes 12, 16, 17, 20 and 23, 24, 27 which are the nodes surrounding the two columns of the room.

<a name="accurate-layout">
<center>
	<img src="/assets/img/status.png" style="width:950px; height:592px;"/><br>
	<!-- <center> Fig. 1 - Resources status</center> -->
</center>
</a>

<br />

<!-- PARTIAL MODAL FOR NODES DETAILS - USED IN RUN OR STATUS -->
<!-- PARTIAL MODAL FOR NODES DETAILS - USED IN RUN OR STATUS -->
<script type='text/javascript' src='/assets/js/ug/ug-common-libraries.js'></script>
<script type='text/javascript' src='/assets/js/ug/ug-functions.js'></script>
<script type='text/javascript' src='/assets/js/ug/ug-slider.js'></script>
<script type='text/javascript' src='/assets/js/ug/ug-sliderassets.js'></script>
<script type='text/javascript' src='/assets/js/ug/ug-touchslider.js'></script>
<script type='text/javascript' src='/assets/js/ug/ug-zoomslider.js'></script>
<script type='text/javascript' src='/assets/js/ug/ug-video.js'></script>
<script type='text/javascript' src='/assets/js/ug/ug-gallery.js'></script>
<script type='text/javascript' src='/assets/js/ug/ug-carousel.js'></script>
<script type='text/javascript' src='/assets/js/ug/ug-api.js'></script>
<link rel='stylesheet' href='/assets/css/ug/unite-gallery.css' type='text/css' />
<script type='text/javascript' src='/assets/js/ug/ug-theme-slider.js'></script>
<link rel='stylesheet' href='/assets/css/ug/ug-theme-default.css' type='text/css' />
<script type="text/javascript" src="/assets/r2lab/omfrest.js"></script>
<script type="text/javascript" src="/assets/r2lab/info_nodes.js"></script>
<div class="modal fade" id="node_details" tabindex="-1" role="dialog" aria-labelledby="myModalSlice">
  <div class="modal-dialog modal-lg" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
	  <span aria-hidden="true">&times;</span>
	</button>
        <h4 class="modal-title" id="node_details_title">Technical Details</h4>
      </div>
      <div class="modal-body" id="node_details_content">
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
      </div>
    </div>
  </div>
</div>
