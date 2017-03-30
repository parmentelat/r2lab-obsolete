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

<div class="container" markdown="1">
  <div class="row">
    <div class="col-md-4">
      <span> <h3>The testbed is yours</h3> </span>
      <p>
	The testbed is reservable as a whole.
	Once they have booked the testbed, registered users can ssh into `faraday.inria.fr`,
	and from there control all the resources in the testbed.
	You are thus in full control of all the radio traffic in the chamber. 
        </p>
    </div>
    <div class="col-md-4">
      <span> <h3>The nodes are yours</h3> </span>
      <p>
        Also you can load your operating system of choice on any node.
	From that point you can ssh-access all nodes with administration privileges, and configure
	the available resources - nodes, USRPs and phones - to create a rich experimental environment.
       </p>
    </div>
    <div class="col-md-4">
      <span> <h3>Methodology</h3> </span>
      <p>
      Experimental scenarios can be created using standard tools. We also provide [tutorials, and python libraries](tutorial.md)
      that can optionnally help you efficiently orchestrate the complete experimental workflow, from deployment to data collection.
      </p>
    </div>
  </div>
</div>

<br>

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
      Some nodes are equipped with USRP devices from <a href="http://www.ettus.com" target="_blank">ETTUS</a> to run SDR-based experiments such as spectrum analyzer or 4G/5G OpenAirInterface scenarios. All these devices can be remotely-controlled through ust/uon/uoff utilities. 
      <br>
      Currently the following USRP devices are deployed:
      <ul>
        <li>Five <a href="http://www.ettus.com/product/details/UB210-KIT" target="_blank">USRP B210</a> on nodes 6, 11, 16, 19 and 23,
        </li>
        <li>One <a href="http://www.ettus.com/product/details/UN210-KIT" target="_blank">USRP N210</a> on node 12, 
        </li>
        <li>One old <a href="http://files.ettus.com/manual/page_usrp2.html" target="_blank">USRP 2</a> on node 13, and
        </li>
        <li>One old <a href="https://www.ettus.com/product/details/USRPPKG" target="_blank">USRP 1</a> on node 28.
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
      <h3>Commercial 4G Phone</h3>
      A Nexus 5 phone is available right inside the chamber:
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


<div class="container">
  <div class="row" markdown="1">
    <div class="col-md-12 new_pad">
      <h3>Nodes detailed information</h3>
      <!-- DyNAMIC TABLE CREATED BY CMD line in faraday-->
      <style type="text/css"> @import url("/assets/r2lab/table-nodes.css"); </style>
      <script type="text/javascript" src="/assets/r2lab/table-nodes.js"></script>
      <table id="comparative" class="table table-condensed dt_table">
        <thead><tr><th>&nbsp;</th></tr></thead>
        <tbody><tr><td>no info available yet</td></tr></tbody>
      </table>
    </div>
  </div>
</div>

<div class="modal fade" id="big_photo" tabindex="-1" role="dialog">
  <div class="modal-dialog modal-dialog-custom modal-lg" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
	      </button>
      <h6 class="modal-title" id="big_image_title">&nbsp;</h6>
      </div>
      <div class="modal-body" id="big_image_content">
      </div>
    </div>
  </div>
</div>

<div class="container">
  <div class="row" markdown="1">
    <div class="col-md-8 new_pad">
      <h3>Statistics on nodes health</h3>
      The testbed routinely runs a thorough raincheck procedure, to make sure that all is in order.
      <br>
      <a href="/stats.md">See the stats page for details</a>.
    </div>
  </div>
</div>


<script type="text/javascript" src="/assets/r2lab/xhttp-django.js"></script>
<!-- defines nodes_details_modal -->
<< include r2lab/nodes-details-modal.html >>
