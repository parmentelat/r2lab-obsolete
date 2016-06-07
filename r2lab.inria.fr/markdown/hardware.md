title: Hardware
tab: platform
---

**Thirty-seven** nodes are available in R2lab to provide a modern testbed infra structure. The nodes are distributed in a grid layout and are customizable, allowing great variety of experimentation scenarios.

<h2 class="text-center" style="color:green;" >
Full control and access to bare metal<br>
<span class="text-muted lead">The nodes are totally open and users can install any software stack they need</span><br>
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

  <div class="col-md-2"> </div>
  
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
    <i style="font-size:2em;" class="pull-left glyphicon glyphicon-signal" aria-hidden="true">&nbsp;</i>
  </span>
Our anechoic chamber is equipped with powerful nodes that can run high-level OS Linux. They can run many applications and advanced experimentations.

  <hr>

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

<hr>
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
  <div class="col-md-3">
    <br>
    <img src="/assets/img/icarus6i.png" width="300px">
    <center>Fig. 1 - Resource/Node Icarus</center>
    <br>
    <br>
    <img src="/assets/img/node_interface_2.jpg" width="300px">
    <center>Fig. 2 - Resource/Node Icarus</center>
  </div>
</div>

