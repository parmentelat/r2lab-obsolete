title: NEPI - Pings
tab: tutorial
float_menu_template: r2lab/float-menu-tutorials.html
---

<script src="/assets/js/diff.js"></script>
<script src="/assets/r2lab/r2lab-diff.js"></script>
<style>@import url("/assets/r2lab/r2lab-diff.css")</style>

Below are a couple of experiments to get started with the
[NEPI](http://nepi.inria.fr/Install/WebHome) experiment orchestration
tool, R2lab experimental testbed and <a href="http://openairinterface.eurecom.fr/openairinterface-software" target="_blank">Open Air interface</a>.

The experiments below are designed as a series of small incremental changes, so we can illustrate various
concepts one at a time.

To this end, from one experiment to the other, we highlight the
required changes in a git-like style: inserted and deleted lines are
shown with a different color, so readers can see what is new in this
tutorial.

<br/>

<ul id="myTabs" class="nav nav-tabs" role="tablist">
  <li role="presentation" class="active">
    <a href="#D1" id="D1-tab" role="tab" data-toggle="tab" aria-controls="D1" aria-expanded="true">D1</a>
  </li>
</ul>

<div id="contents" class="tab-content">
<!------------ D1 ------------>
<div role="tabpanel" class="tab-pane fade active in" id="D1" aria-labelledby="profile-tab">
  <br/>
  In this tutorial, we illustrate how to leverage OpenAirInterface in order to create a standalone 5G infrastructure inside R2Lab to deploy our ping test.
  In this experiment we repeat a simple ping between 2 nodes, however, with <b>Open Air Interface</b>.
  <br/><br/>
  The <b>Open Air Interface</b> provides truly open-source solutions for prototyping 5th Generation Mobile Networks
  and devices. You can check more details about <a href="http://openairinterface.eurecom.fr/openairinterface-software" target="_blank">Open Air Interface</a>.
  <br/><br/>
  For now, the nodes equipped with this interface are <code>11</code> and <code>23</code>. For this reason, in the code
  you will find these nodes already setup.

  <center>
    <!-- <img src="/assets/img/D1.png" alt="d1"> --> <br/>
    Download the <a href="/code/D1-ping-OAI.py" download target="_blank">D1 experiment</a> code
  </center>
<< codediff d1 D1-ping-OAI.py >>
</div>

</div> <!-- end div contents -->

<script src="/assets/r2lab/open_tab.js"></script>
