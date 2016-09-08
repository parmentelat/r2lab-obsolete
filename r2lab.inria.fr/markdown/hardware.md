title: Hardware
tab: platform
---

**Thirty-seven** nodes are available in R2lab to provide a modern testbed infra structure.
The nodes are distributed in a grid layout and are customizable, allowing great variety of experimentation scenarios.

<h2 class="text-center" style="color:green;" >
  Full control and access to bare metal
  <br>
  <span class="text-muted lead">
    The nodes are totally open and users can install any software stack they need
  </span>
  <br>
</h2>

*****

<div class="row">
  <div class="col-md-4">
    <span>
      <h3>The node is yours</h3>
    </span>
    This implies that you can run, reboot, load, and reload disparate
    operating system in each node. A full access to the node is handled by
    a remote access and a root user is available during your
    experimentation.
  </div>
  <div class="col-md-4">
    <span>
      <h3>Node details</h3>
    </span>
    Our anechoic chamber is equipped with powerful nodes that can run high-level OS Linux.
    They can run many applications and advanced experimentations.
  </div>
  <div class="col-md-4">
    <span>
      <h3>Gateway connection</h3>
    </span>
    R2lab offers a connection to the testbed infrastructure through a gateway access
    which allows the researchers to control each reserved node.
  </div>
</div>

*****

<div class="row" markdown="1">
  <div class="col-md-8">
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

<div class="row" markdown="1">
  <div class="col-md-8">
### USRP nodes

Some nodes are equipped with USRP extensions, for SDR-based experiments&nbsp;:

* Based on  [USRP N210](http://www.ettus.com/product/details/UN210-KIT),
  or on [USRP B210](http://www.ettus.com/product/details/UB210-KIT),
  as well as some older USRP2 and USRP1, all models from [ETTUS](http://www.ettus.com)
* Remote-controllable for reset-like operations
* Current deployment: 4 nodes - target: 10 nodes
  </div>
  <div class="col-md-4">
    <br><br>
    <img src="/assets/img/icarus6i.png" width="300px">
    <center>Fig. 2 - Icarus node standalone</center>
  </div>
</div>

<div class="row" markdown="1">
  <div class="col-md-8">

### Nexus Phone

A nexus phone is available right inside the chamber.

* It is reachable through a Mac (that also sits in the room)
  that has its wireless card physically disabled, and that has a USB cable to the phone
* The Mac can be reached from the gateway as `ssh tester@macphone` (or the `macphone` convenience shell shortcut)
* Once logged in the Mac you can use convenience helpers to manage the phone (type `help` for details), or use `adb` manually.
* The mac can also be managed using apple screen sharing tools (VNC-compliant), pointing directly at `faraday.inria.fr`
  </div>
  <div class="col-md-4">
    <br><br>
    <img src="/assets/img/macphone.png" width="300px">
    <center>Fig. 3 - Commercial phone</center>
  </div>
</div>

****

### Statistics on nodes health</h3>

The testbed routinely runs a thorough raincheck procedure, to make
sure that all is in order.  Historically, this was performed every
night during the early stages; maturity is now such that we feel
comfortable with running it only twice a week ([see the booking page
for details](/book.md)).

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
