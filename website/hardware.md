title: Hardware
tab: platform
---

**Thirty-seven** nodes are available in R2lab to provide a modern testbed infra structure. The nodes are distributed in a grid layout and are customizable, allowing great variety of experimentation scenarios.

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

		&nbsp; R2lab offers a connection to the testbed infrastructure through a gateway access which allows the researchers to control each reserved node.
  </div>
</div>
<br>
<div class="row" markdown="1">
  <div class="col-md-7"> 
  <span>
    <h3>Node details</h3>
    <i style="font-size:2em;" class="pull-left glyphicon glyphicon-signal" aria-hidden="true"></i>
  </span>
  &nbsp; Our anechoic chamber is equipped with powerful nodes which allows to run high-level OS Linux. It &nbsp; enables to run many applications and advanced experimentations.

  Part of the nodes will be connected to **USRP** software radio devices. Details of the devices are provided below.
  <br>
  <br>
  **The [Nitos](http://nitlab.inf.uth.gr/NITlab/) X50 nodes are:**
  <p>
  **2 Wireless Interfaces** Atheros 802.11 a/b/g and Atheros  802.11 a/b/g/n (MIMO);  **CPU** Intel Core i7-2600 processor; 
  **RAM** kingston 4GB HYPERX BLU DDR3; 8M **Cache**, at 3.40GHz.
  </p>
  **Future USRP nodes:**
  <p>
  [**USRP** N210](http://www.ettus.com/product/details/UN210-KIT), [**USRP** B210](http://www.ettus.com/product/details/UB210-KIT), **USRP**2 and **USRP**1.
  </p>
  
  <p>
  The [Nitos](http://nitlab.inf.uth.gr/NITlab/) nodes embed **three wired interfaces**, which are used for:
  </p>
  **CM card**:<br>
  A small web server run in a Chassis Manager Card (CM card) to control and monitor the nodes. The CM card answer HTTP requests to expose on/off actions, status and others like: 
  <br>
  - Remote on/off and reset of a NITOS node<br>
  - Monitoring of the node's status (on or off)<br>
  - Remote reset of the CM Card<br>
  - Auto-reset safeguards, in case of a hang<br>
  - Monitoring of the Power Supply Unit voltage integrity<br>
  <!-- - External environmental conditions monitoring (temperature, humidity, light intensity)<br>
  - Internal node temperature monitoring<br> -->
  <br> 
  The CM card interface is available at: 192.168.**1**.<font color="red">**xx**</font>, where <font color="red">**xx**</font> are the node number.
  <br>
  <br>

  **Experiment interface**:<br>
  The experiment interface offers wired connectivity between nodes and
  to the infrastructure; this is entirely dedicated to experimenters -
  and is not turned on by default, but can easily be enabled from the
  node using DHCP, in which case it becomes available at: 192.168.**2**.<font color="green">**xx**</font>. This interface will not be available in case the Nitos node is attached to a **USRP**2 or **N210** device.
  
  <br>
  <br>
  **Control interface( OMF)**:<br>
  OMF is a Testbed Control, Measurement and Management Framework. It was developed for wireless testbed platforms and had being extended to support features and facilities for testbed's control, measurement, and management.
  The CI OMF interface is available at: 192.168.**3**.<font color="blue">**xx**</font>.
  
  <br>
  <br>

  </div>
  <div class="col-md-3">
    <br>
    <img src="/assets/img/icarus6i.png" width="300px">
    <center>Fig. 1 - Resource/Node Icarus</center>
    <br>
    <br>
    <br>
    <img src="/assets/img/node_interface_2.jpg" width="300px">
    <center>Fig. 2 - Resource/Node Icarus</center>
  </div>
</div>
