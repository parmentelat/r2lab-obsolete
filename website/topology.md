title: Topology
tab: topology
---

R2Lab testbed project offers a hight quality anechoic room for your experiments. Following are the details of the anechoic room.

### Layout

Below is the ground plan layout of the anechoic room which provide thirty-seven wireless nodes distributed in a **≈ 90m<sup>2</sup>** room.

The nodes are arranged in grid with ≈1.0m (vertical) and ≈1.15m (horizontal) of distance between them, except by the nodes 12, 16, 17, 20 and 23, 24, 27 which are the nodes surrounding the columns room.

<left>
	<img src="assets/img/status.png" style="width:950px; height:592px;"/><br>
	<!-- <center> Fig. 1 - Resources status</center> -->
</left>

<br>

### Livemap

Frequently a routine checks the availability of our nodes platform. In order to allow real time and multiple information concerning R2lab platform, our live map keep the users posted about the state of each node concerning technical infos, incidents and operational details.<br>
- The red/green round informs if the node responds or not a ping at the experiment interface.
- The round O.S. brand informs that the node is turned on and running the referenced O.S..
- The node is turned off when only the number is presented in the map.

<div id="livemap_container"></div>

<h3>Status</h3>

Complementary to the live map above, this status table present an alternative format the queries results.
- The <b>availability</b> column: 
	Reports that the node are controllable or not. In fail case the node could be physically powered off or in maintenance.
- The <b>on/off</b> column:
	Reports that the node is ready to be used or not.
- The <b>ping</b> column: 
	Reports that the node answers a single ping at the experiment interface.
- The <b>O.S</b> column:
	Reports that the node responds a ssh connection sending back the operational system release.
<br>

The table with these queries are presented below.

<hr />
<table class="table table-condensed livetable">
  <thead>
    <tr>
      <th></th>
      <th>Availability</th>
      <th>On/Off</th>
      <th>Ping</th>
      <th>O.S.</th>
    </tr>
  </thead>
  <!-- hook for livetable.js -->
  <tbody id="livetable_container">
  </tbody>
</table>


</html>
