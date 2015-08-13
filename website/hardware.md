title: Hardware
tab: platform
---

**Thirty-seven** nodes are available in R2Lab to provide a modern testbed infra structure. The nodes are distributed in grid layout and are customizable which allow great variety of tests and simulations.

<h2 class="text-center" style="color:green;" >
full control and granted access<br>
<span class="text-muted lead">The nodes are totally open and a full granted user access is provided</span><br>
</h2>

<hr class="featurette-divider">

<div class="row">
  <div class="col-md-5"> 
  	<span>
  		<h3>The node is yours</h3>
  		<i style="font-size:2em;" class="pull-left glyphicon glyphicon-check" aria-hidden="true"></i>
 		</span>

		&nbsp; This implies that you can run, reboot, load, and reload disparate operating system in each node. A full access to the node is handled by a remote access and a root user is available during your experimentation.
  </div>

  <div class="col-md-2">
  </div>
  
  <div class="col-md-5">
  	<span>
  		<h3>Gateway connection</h3>
  		<i style="font-size:2em;" class="pull-left glyphicon glyphicon-cog" aria-hidden="true"></i>
 		</span>

		&nbsp; R2Lab offers a connection to the testbed infrastructure trough a gateway access which allow the researchers control each reserved node.
  </div>
</div>

<div class="row">
  <div class="col-md-3">
    <br>
    <img src="assets/img/icarus.png">
    <center>Fig. 1 - Resource/Node Icarus</center>
    <br>
    <br>
    <br>
    <img src="assets/img/node_back.jpg">
    <center>Fig. 2 - Resource back wired details</center>
  </div>
  
  <div class="col-md-7"> 
  <span>
    <h3>Node details</h3>
    <i style="font-size:2em;" class="pull-left glyphicon glyphicon-signal" aria-hidden="true"></i>
  </span>
  &nbsp; Our anechoic chamber is equipped with powerful nodes which allows to run high-level OS Linux. It &nbsp; enables to run many applications and advanced simulations.

  The resources/nodes also contains **six USRP devices** distributed in a such way to cover as much area as possible of the wireless testbed. The device details are listed below.
  <br>
  <br>
  **The [Nitos](http://nitlab.inf.uth.gr/NITlab/) X50 nodes are:**
  <p>
  **CPU** Intel Core i7-2600 processor; 8M **Cache**, at 3.40GHz; **RAM** kingston 4GB HYPERX BLU DDR3; **Wireless Interfaces** Atheros 802.11 a/b/g and Atheros  802.11 a/b/g/n (MIMO).
  </p>
  **Our USRP X10 device are:**
  <p>
  **USRP** Xilinx Spartan 3A-DSP 3400; **FPGA** 100 MS/s duas ADC, 400 MS/s duas DAC; **Gigabit Ethernet** connectivity.
  </p>
  
  <p>
  The resources/nodes keep **three wired interfaces** (fig 2, <font color="green">green</font>, <font color="red">red</font> and <font color="blue">blue</font> cables) which are designed and implements the main following components as well.
  </p>
  **CM card**:<br>
  A small web server run in a Chassis Manager Card (CM card) to control and monitor the nodes. The CM card answer HTTP requests to expose on/off actions, status and others like: 
  <br>
  <br>
  - Remote on/off and reset of a NITOS node<br>
  - Monitoring of the node's status (on or off)<br>
  - Remote reset of the CM Card<br>
  - Auto-reset safeguards, in case of a hang<br>
  - Monitoring of the Power Supply Unit voltage integrity<br>
  <!-- - External environmental conditions monitoring (temperature, humidity, light intensity)<br>
  - Internal node temperature monitoring<br> -->
  <br> 
  The CM card interface is available at: 192.168.**1**.<font color="red">**xx**</font>, where <font color="red">**xx**</font> are the resource/node number.
  <br>
  <br>

  **Experiment interface**:<br>
  The experiment interface allow the access to the resource/node and is available at: 192.168.**2**.<font color="green">**xx**</font>.
  
  <br>
  <br>
  **Control interface(OMF)**:<br>
  OMF is a Testbed Control, Measurement and Management Framework. Was developed for wireless testbed platforms and had being extended to support features and facilities for testbed's control, measurement, and management.
  The CI OMF interface is available at: 192.168.**3**.<font color="blue">**xx**</font>.
  
  <br>
  <br>

  </div>
</div>