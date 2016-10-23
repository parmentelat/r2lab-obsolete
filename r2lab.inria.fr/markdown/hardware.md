title: Hardware
tab: platform
---
<div class="container">
  <div class="row">
    <div class="col-md-12">
      <p>
        <b>Thirty-seven</b> nodes are available in R2lab to provide a modern testbed infra structure.
        The nodes are distributed in a grid layout and are customizable, allowing great variety of experimentation scenarios.
        <h2 class="text-center" style="color:green;" >
          Full control and access to bare metal
          <br>
          <span class="text-muted lead">
            The nodes are totally open and users can install any software stack they need
          </span>
          <br>
        </h2>
      </p>
    </div>
  </div>
</div>

</hr>

<div class="container">
  <div class="row">
    <div class="col-md-4">
      <span>
        <h3>The node is yours</h3>
      </span>
      <p>
        This implies that you can run, reboot, load, and reload disparate
        operating system in each node. A full access to the node is handled by
        a remote access and a root user is available during your
        experimentation.
        </p>
    </div>
    <div class="col-md-4">
      <span>
        <h3>Node details</h3>
      </span>
      <p>
        Our anechoic chamber is equipped with powerful nodes that can run high-level OS Linux.
        They can run many applications and advanced experimentations.
      </p>
    </div>
    <div class="col-md-4">
      <span>
        <h3>Gateway connection</h3>
      </span>
      <p>
        R2lab offers a connection to the testbed infrastructure through a gateway access
        which allows the researchers to control each reserved node.
      </p>
    </div>
  </div>
</div>

<div class="container">
  <div class="row">
    <div class="col-md-12">
      <p>
        <h2 class="text-center" style="color:green;" >
          Comparative table
        </h2>
      </p>
    </div>
  </div>
</div>

<!-- DyNAMIC TABLE CREATED BY CMD line in faraday-->
<br>
<style type="text/css"> @import url("/assets/r2lab/detail_nodes.css"); </style>
<script type="text/javascript" src="/assets/r2lab/detail_nodes.js"></script>
<table id="comparative" class="table table-hover dt_table">
  <tr><td>no info yet</td></tr>
  <tr><td></td></tr>
<table>
<br>
<!-- Latest compiled and minified JavaScript -->
<div class="modal fade" id="big_photo" tabindex="-1" role="dialog" aria-labelledby="myModalSlice">
  <div class="modal-dialog modal-lg" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
	      </button>
      <h4 class="modal-title" id="big_image_title">Image</h4>
      </div>
      <div class="modal-body" id="big_image_content">
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
      </div>
    </div>
  </div>
</div>


<div class="container">
  <div class="row" markdown="1">
    <div class="col-md-8 new_pad">
      <h3>All nodes</h3>
      All 37 nodes are based on <a href="http://nitlab.inf.uth.gr/NITlab/" target="_blank">Nitos X50</a> and feature
      <ul>
        <li>State of the art motherboard
          <ul>
            <li>CPU Intel Core i7-2600 processor</li>
            <li>4Gb RAM</li>
            <li>240 Gb SSD</li>
          </ul>
        <li>2 Wireless Interfaces, dedicated to experimentation, 3 antennas each&nbsp;:
          <ul>
            <li>Atheros 802.11 93xx a/b/g/n</li>
            <li>and/or Intel 5300</li>
          </ul>
        </li>
        <li> 3 wired interfaces used for&nbsp;:
          <ul>
            <li>Remote power and reset management</li>
            <li>Control, used by the testbed management framework for providing access - 192.168.3.<b><font color="red">nn</font></b>, where <b><font color="red">nn</font></b> is the node number</li>
            <li>Data, dedicated to experimentation - 192.168.2.<b><font color="red">nn</font></b></li>
          </ul>
        </li>
      </ul>  
    </div>
    <div class="col-md-4">
      <br>
      <img src="/assets/img/node_interface_3.png" width="300px">
      <center>Fig. 1 - Icarus Nodes in the testbed</center>
    </div>
  </div>
</div>

<div class="container">
  <div class="row" markdown="1">
    <div class="col-md-8 new_pad">
      <h3>USRP nodes</h3>
      Some nodes are equipped with USRP extensions, for SDR-based experiments:
      <ul>
        <li>Based on  <a href="http://www.ettus.com/product/details/UN210-KIT" target="_blank">USRP N210</a>, or on <a href="http://www.ettus.com/product/details/UB210-KIT" target="_blank">USRP B210</a>,
        as well as some older USRP2 and USRP1, all models from <a href="http://www.ettus.com" target="_blank">ETTUS</a>
        </li>
        <li>Remote-controllable for reset-like operations
        </li>
        <li>Current deployment: 4 nodes - target: 10 nodes
        </li>
    </div>
    <div class="col-md-4">
      <br><br>
      <img src="/assets/img/icarus6i.png" width="300px">
      <center>Fig. 2 - Icarus node standalone</center>
    </div>
  </div>
</div>

<div class="container">
  <div class="row" markdown="1">
    <div class="col-md-8 new_pad">
      <h3>Nexus Phone</h3>
      A nexus phone is available right inside the chamber:
      <ul>
        <li>It is reachable through a Mac (that also sits in the room)
        that has its wireless card physically disabled, and that has a USB cable to the phone
        <li>The Mac can be reached from the gateway as <code>ssh tester@macphone</code> (or the <code>macphone</code> convenience shell shortcut)
        </li>
        <li>Once logged in the Mac you can use convenience helpers to manage the phone (type <code>help</code> for details), or use <code>adb</code> manually.
        </li>
        <li>The mac can also be managed using apple screen sharing tools (VNC-compliant), pointing directly at <code>faraday.inria.fr</code>
        </li>
      </ul>
    </div>
    <div class="col-md-4">
      <br><br>
      <img src="/assets/img/macphone.png" width="300px">
      <center>Fig. 3 - Commercial phone</center>
    </div>
  </div>
</div>

<hr>

<div class="container">
  <div class="row" markdown="1">
    <div class="col-md-12">
      <h3>Statistics on nodes health</h3>
      The testbed routinely runs a thorough raincheck procedure, to make
      sure that all is in order.  Historically, this was performed every
      night during the early stages; maturity is now such that we feel
      comfortable with running it only twice a week
      <a href="/book.md">see the booking page
      for details</a>.

      In any case, below is a summary of the issues found since Jan. 2016.

      <script type="text/javascript" src="/assets/r2lab/omfrest.js"></script>
      <script src="http://cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
      <script src="/assets/js/moment.min.js"></script>
      <script src="/assets/js/underscore-min.js"></script>
      <style type="text/css"> @import url("/assets/css/daterangepicker.css"); </style>
      <script src="/assets/js/daterangepicker.js"></script>
      <script type="text/javascript" src="/assets/r2lab/range-calendar.js"></script>
      <script src="/assets/js/chartlib/src/charts/Chart.Heat.js"></script>
      <script type="text/javascript" src="/assets/r2lab/charts.js"></script>
      <style type="text/css"> @import url("/assets/r2lab/charts.css"); </style>
      <script src="/assets/js/chartlib/dist/Chart.bundle.min.js"></script>
    </div>
  </div>
</div>

<div class="container">
  <div class="row">
    <div class="col-lg-12">
      <div style="width: 100%">
        <div id="line-chart-tooltip"></div>
        <canvas id="line" height="250" width="700"></canvas>
      </div>
    </div>
    <!-- <div class="col-lg-1"> -->
      <!-- <br><br>select a range date<br>
      <input type="text" id="range_calendar" class="form-control"> -->
    <!-- </div> -->
  </div>

  <div class="row">
    <div class="col-lg-12">
      <br><br>
      <p></p>
    </div>
  </div>    

  <div class="row">
    <div class="title_heat">
      presence of issues since the <b>beginning</b> of measurements
    </div>
    <div class="col-lg-1" style="width: 10px">
      <div class="side_title">
        <img src="/assets/img/mapylegend.png" class="">
      </div>
    </div>
    <div class="col-lg-10" style="width: 83.7%">
      <div class="heat_container" style="background-image: url(/assets/img/chamber.png); background-repeat: no-repeat;">
        <canvas id="heat" width="775" height="505"></canvas>
      </div>
    </div>
    <div class="legend complete_serie"></div><div class="legend2">&nbsp;all serie</div>
    <div class="col-lg-1" style="padding-left: 0px;">
      <div class="side_title"></div>
      <div class="heat_bar">
        high
        <span class="glyphicon glyphicon-plus" aria-hidden="true"></span>
      </div>
      <div class="">
        &nbsp;<img src="/assets/img/heatlevel.png" class="heatlevel">
      </div>
      <div class="heat_bar">
        less
        <span class="glyphicon glyphicon-minus" aria-hidden="true"></span>
      </div>
    </div>
  </div>

  <div class="row">
    <div class="col-lg-12">
      <br><br>
      <p></p>
    </div>
  </div>

  <div class="row">
    <div class="title_heat">
      presence of issues since the <b>beginning</b> of measurements by issue type in percent
    </div>
    <div class="col-lg-1" style="width: 10px">
      <div class="side_title">
        <img src="/assets/img/mapylegend.png" class="">
      </div>
    </div>
    <div class="col-lg-10" style="width: 83.7%">
      <div class="heat_container" id="doughnut_container" style="background-image: url(/assets/img/chamber.png); background-repeat: no-repeat;">
      </div>
    </div>
    <div class="legend complete_serie"></div><div class="legend2">&nbsp;all serie</div>
    <div class="col-lg-1" style="padding-right: 0px; padding-left: 0px; padding-top: 4px; width: 140px;">
      <div class="side_title"></div>
      <div class="legend_intern">LEGEND</div>
      <div class="legend start"></div><div class="legend2">issue in start</div>
      <div class="legend load"></div><div class="legend2">issue in load</div>
      <div class="legend zombie"></div><div class="legend2">issue in shut off</div>
      <div class="legend noissue"></div><div class="legend2">no issues</div>
    </div>
  </div>

</div>

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


<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>
