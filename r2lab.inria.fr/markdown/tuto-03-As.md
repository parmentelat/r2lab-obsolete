title: NEPI - Pings
tab: tutorial
---
<script type="text/javascript">loadMenu();</script>

Below are a couple of experiments to get started with
[NEPI](http://nepi.inria.fr/Install/WebHome) experiment orchestration
tool, and with R2lab simulation testbed.

This suite of experiments, labelled **A1** to **A4**, are designed as
a suite of small incremental changes, to allow better subject
understanding. Feel free to skip to the level that fits your
knowledge.

From one experiment to the other, we highlight the required changes in
a git-like style: inserted and deleted lines are shown with a
different color, so readers can see what is new in this tutorial. 

<br/>

<ul id="myTabs" class="nav nav-tabs" role="tablist">
  <li role="presentation" class="active">
    <a href="#A1" id="A1-tab" role="tab" data-toggle="tab" aria-controls="A1" aria-expanded="true">A1</a>
  </li>
  <li role="presentation" class="">
    <a href="#A2" role="tab" id="A2-tab" data-toggle="tab" aria-controls="A2" aria-expanded="false">A2</a>
  </li>
  <li role="presentation" class="">
    <a href="#A3" role="tab" id="A3-tab" data-toggle="tab" aria-controls="A3" aria-expanded="false">A3</a>
  </li>
  <li role="presentation" class="">
    <a href="#A4" role="tab" id="A4-tab" data-toggle="tab" aria-controls="A4" aria-expanded="false">A4</a>
  </li>
</ul>

<div id="contents" class="tab-content">
<!------------ A1 ------------>
<div role="tabpanel" class="tab-pane fade active in" id="A1" aria-labelledby="home-tab">
  <br/>
  In this experiment example, from your computer, you will create and deploy an application to connect to the R2lab
  <strong>gateway</strong> (faraday.inria.fr).
  <br/><br/>
  Once there, from the <strong>gateway</strong>, you will ping a <strong>google server</strong> and recover its answer.
<center>
  <img src="/assets/img/A1.png" alt="a1"> <br/>
  Download the <a href="/code/A1-ping.py" download target="_blank">A1 experiment</a> code
</center>
<pre data-src="prism.js" class="line-numbers"><code class="language-python">
<< codediff A1-ping.py >>
</code></pre>
</div>
<!------------ A2 ------------>
<div role="tabpanel" class="tab-pane fade" id="A2" aria-labelledby="profile-tab">
    <br/>
    In this experiment example, from your computer, you will create and deploy two application nodes. The first one to connect to the R2lab gateway (faraday.inria.fr) and, from there, reach the <strong>fit01</strong> node. 
    <br/><br/>
    Once connected at the R2lab gateway, you will ping the <strong>fit01</strong> node at its <strong>control interface</strong> (available as the <code>control</code> device under linux).
    At the end you will retrieve the answer of the experiment.
<center>
  <img src="/assets/img/A2.png" alt="a2"><br/>
  Download the <a href="/code/A2-ping.py" download target="_blank">A2 experiment</a> code
</center>
<pre data-src="prism.js" data-line-edit-line="10-13,20,22-30,47,51" data-line-inlcude-line="15-17,32-43" class="line-numbers">
<code class="language-python">
<< codediff A1-ping.py A2-ping.py>>
</code></pre>
</div>
<!------------ A3 ------------>
  <div role="tabpanel" class="tab-pane fade" id="A3" aria-labelledby="profile-tab">
    <br/>
    The experiment below uses two wireless nodes. From your computer you will create and deploy <strong>fit01</strong> and <strong>fit02</strong> nodes. You will configure in both nodes the wired <strong>experiment interface</strong> (available as <code>data</code> under linux) using DHCP.
    <br/><br/>
    Once configured the interface in both nodes, you will be able to ping the <strong>experiment interface</strong> at </strong>fit02</strong> from <strong>fit01</strong>.
<center>
   <img src="/assets/img/A3.png" alt="a3"><br/>
    Download the <a href="/code/A3-ping.py" download target="_blank">A3 experiment</a> code
</center>
<pre data-src="prism.js" data-line-remove-line="25-33"  data-line-edit-line="23,77-83,87" data-line-inlcude-line="19,20,48-59,61-67,69-75" class="line-numbers">
<code class="language-python">
<< codediff A2-ping.py A3-ping.py >>
</code></pre>
</div>


<!------------ A4 ------------>
<div role="tabpanel" class="tab-pane fade" id="A4" aria-labelledby="profile-tab">
  <br/>
    The experiment below uses two nodes and is an incremental change from previous experiment A3.
    From your computer you will create the same fit01 and fit02 nodes.
    This time however, you will configure an <em>ad-hoc</em> network between both nodes <strong>wireless interfaces</strong> (exposed in linux as <code>wlan0</code>).
    <br/><br/>
    Once the interfaces configured, you will ping fit01 and fit02 from one another using the <strong>wireless interface</strong>.
<center>
  <img src="/assets/img/A4.png" alt="a4"><br/>
  Download the <a href="/code/A4-ping.py" download target="_blank">A4 experiment</a> code
</center>
<pre data-src="prism.js" data-line-remove-line="62,79" data-line-edit-line="32,94,96,110,111" data-line-inlcude-line="22-29,63-71,80-88,102-108,114-116" class="line-numbers">
<code class="language-python">
<< codediff A3-ping.py A4-ping.py >>
</code></pre>
</div>

</div>

