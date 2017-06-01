title: Video Tutorials on YouTube
tab: tutorial
skip_header: True

<script src="https://cdnjs.cloudflare.com/ajax/libs/jsdiff/3.2.0/diff.min.js"></script>
<script src="/assets/r2lab/open-tab.js"></script>
<script src="/assets/r2lab/r2lab-diff.js"></script>
<style>@import url("/assets/r2lab/r2lab-diff.css")</style>


<ul class="nav nav-tabs">
  <li class="active"> <a href="#AOA">Angle of Arrival</a> </li>
  <li> <a href="#OAI">OpenAirInterface</a></li>
  <li> <a href="#OAI-NG">OpenAirInterface (2)</a></li>

  << include r2lab/tutos-index.html >>
</ul>


<div id="contents" class="tab-content" markdown="1">

<!------------ AOA ------------>
<div id="AOA" class="tab-pane fade in active" markdown="1">


### Measuring WiFi angle of arrival

In this video, we give an end-to-end overview of how to conduct a realistic experiment. In this case, the scientific objectives are to compare the results of several methods for estimating the angle of arrival of a WiFi signal, on a receiver that has 3 aligned antennas, distant from one another by about half the wavelength.

This video emphasizes the usage of NEPI as a tool for designing the experiment logic. Check it out here&nbsp;:

<object width="854" height="480"
data="https://www.youtube.com/embed/vDPLQNsZaVY">
</object>

</div>

<!------------ OAI ------------>
<div id="OAI" class="tab-pane fade" markdown="1">

### Visiting the chamber using skype on top of a local 5G infrastructure based on OpenAirInterface

In this video, we illustrate how to leverage OpenAirInterface in order to

* create a standalone 5G infrastructure inside R2Lab,
* and deploy a base station on one of the nodes.

Based on this, we establish a skype session between a regular laptop and a commercial Nexus phone, right inside the chamber, and take this chance to give a physical tour of the chamber.

Later on, we use yet another node as a scrambling device to terminate the call.

<object width="854" height="480"
data="https://www.youtube.com/embed/FpZo6uqTosQ">
</object>

</div>

<!------------ OAI-NG ------------>
<div id="OAI-NG" class="tab-pane fade" markdown="1">

### Set up a 5G network in 5 minutes

The purpose is vry similar to the previous one; here again we leverage OpenAirInterface in order to

* create a standalone 5G infrastructure inside R2Lab,
* deploy a base station on one of the nodes,
* connect the dedicated phone inside the chamber,
* measure bandwidth to the outside Internet with speedtest.net,
* and visualize downlink and uplink spectrum.

<object width="854" height="480"
data="https://www.youtube.com/embed/N1nl_PqWlKw">
</object>

</div>

</div> <!-- end div contents -->
