title: Hardware
tab: platform
---

**Thirty-seven** nodes are available in R2lab to provide a modern testbed infra structure. The nodes are distributed in a grid layout and are customizable, allowing great variety of experimentation scenarios.

<h2 class="text-center" style="color:green;" >
  Full control and access to bare metal
  <br>
  <span class="text-muted lead">
    The nodes are totally open and users can install any software stack they need
  </span>
  <br>
</h2>

<hr class="featurette-divider">

<div class="row">
  <div class="col-md-4">
  	<span>
  		<h3>The node is yours</h3>
  	</span>
		This implies that you can run, reboot, load, and reload disparate operating system in each node. A full access to the node is handled by a remote access and a root user is available during your experimentation.
  </div>
  <div class="col-md-4">
    <span>
      <h3>Node details</h3>
    </span>
    Our anechoic chamber is equipped with powerful nodes that can run high-level OS Linux. They can run many applications and advanced experimentations.
  </div>
  <div class="col-md-4">
  	<span>
  		<h3>Gateway connection</h3>
  	</span>
		R2lab offers a connection to the testbed infrastructure through a gateway access which allows the researchers to control each reserved node.
  </div>
</div>

<hr>

<div class="row">
  <div class="col-md-8">
    <h3>All nodes</h3>
    All 37 nodes are based on [Nitos X50](http://nitlab.inf.uth.gr/NITlab/) and feature
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
            <li>Control, used by the testbed management framework for providing access - 192.168.3.<font color="red">**nn**</font>, where <font color="red">**nn**</font> is the node number</li>
            <li>Data, dedicated to experimentation - 192.168.2.<font color="red">**nn**</font></li>
          </ul>
        </li>
      </ul>  
  </div>
  <div class="col-md-4">
    <br>
    <img src="/assets/img/node_interface_3.png" width="300px">
    <center>Fig. 1 - Resource/Node Icarus</center>
  </div>
</div>

<div class="row">
  <div class="col-md-8">
    <h3>USRP nodes</h3>
    Some nodes are equipped with USRP extensions, for SDR-based experiments&nbsp;:
    <ul>
      <li>Based on [USRP N210](http://www.ettus.com/product/details/UN210-KIT),</li>
      <li>or on [USRP B210](http://www.ettus.com/product/details/UB210-KIT), featuring USRP2 and USRP1.</li>
      <li>both models from [ETTUS](http://www.ettus.com)</li>
      <li>also remote-controllable for reset-like operations</li>
      <li>Current deployment: 4 nodes - target: 10 nodes</li>
    </ul>
  </div>
  <div class="col-md-4">
    <br><br>
    <img src="/assets/img/icarus6i.png" width="300px">
    <center>Fig. 2 - Resource/Node Icarus</center>
  </div>
</div>

<div class="row">
  <div class="col-md-12">
    <h3>Historical of issues</h3>
      Summarized below are the results of our nightly monitoring routine which help us keep r2lab healthy. The graphs brings the number of issues found along the days from Jan/16.
  </div>
</div>


<script type="text/javascript" src="/assets/r2lab/omfrest.js"></script>
<script src="http://cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
<script src="/assets/js/moment.min.js"></script>
<script src="/assets/js/underscore-min.js"></script>
<style type="text/css"> @import url("/assets/css/daterangepicker.css"); </style>
<script src="/assets/js/daterangepicker.js"></script>
<script type="text/javascript" src="/assets/r2lab/range-calendar.js"></script>
<script src="/assets/r2lab/statistics-heat.js"></script>
<script type="text/javascript" src="/assets/r2lab/statistics.js"></script>
<script src="/assets/js/chartlib/dist/Chart.bundle.js"></script>
<script src="/assets/js/simpleheat.js"></script>
<style type="text/css"> @import url("/assets/r2lab/statistics.css"); </style>

<div class="container">
  <div class="row">
    <div class="col-lg-12">
      <div style="width: 100%">
        <canvas id="line" height="250" width="700"></canvas>
      </div>
    </div>
  </div>
  <div class="row">
    <div class="col-lg-12">
      <br><br>
      <p></p>
      <br><br>
    </div>
  </div>  
  <div class="row">
    <div class="col-lg-12">
      <div style="width: 100%">
        <canvas id="bar" height="250" width="700"></canvas>
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
      <br><br>
    </div>
  </div>  

  <div class="row">
    <div class="title_heat">
      presence of issues since the beginning of measurements
    </div>
    <div class="col-lg-11" style="width: 88%">
      <div class="heat_container" style="background-image: url(/assets/img/chamber.png); background-repeat: no-repeat;">
        <canvas id="heat" width="775" height="505"></canvas>
      </div>
    </div>
    <div class="col-lg-1">
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
      <br><br>
    </div>
  </div>  

  <div class="row">
    <div class="title_heat">
      presence of issues since the beginning of measurements by issue type
    </div>
    <div class="col-lg-11" style="width: 88%">
      <div class="heat_container" id="doughnut_container" style="background-image: url(/assets/img/chamber.png); background-repeat: no-repeat;">
      </div>
    </div>
    <div class="col-lg-1" style="padding-right: 0px; padding-top: 4px;">
      <div class="legend start"></div><div class="legend2">start</div>
      <div class="legend ssh"></div><div class="legend2">ssh</div>
      <div class="legend load"></div><div class="legend2">load</div>
      <div class="legend osos"></div><div class="legend2">o.s.</div>
      <div class="legend zombie"></div><div class="legend2">zombie</div>
    </div>
  </div>

</div>
