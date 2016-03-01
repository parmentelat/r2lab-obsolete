title: NEPI - Pings
tab: tutorial
float_menu_template: r2lab/float-menu-tutorials.html
---

<script src="/assets/js/diff.js"></script>
<script src="/assets/r2lab/r2lab-diff.js"></script>
<style>@import url("/assets/r2lab/r2lab-diff.css")</style>

Below are a couple of experiments to get started with the
[NEPI](http://nepi.inria.fr/Install/WebHome) experiment orchestration
tool, and with the R2lab experimental testbed.

This suite of experiments, labelled **A1** to **A4**, are designed as
a series of small incremental changes, so we can illustrate various
concepts one at a time.

To this end, from one experiment to the other, we highlight the
required changes in a git-like style: inserted and deleted lines are
shown with a different color, so readers can see what is new in this
tutorial.

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
  In this experiment example, from your computer, you will run a simple command on the R2lab 
  <strong>gateway</strong> (faraday.inria.fr).
  <br/><br/>
  In this example, we will ping a <strong>google server</strong>
  and retrieve its answer.
  <br/><br/>
  Before you run this code, you might wish to check that you indeed have access to the gateway. Assuming your slice name is <code>onelab.inria.mario.tutorial</code>, you should be able to run the following command&nbsp;: <br/><br/>
  <pre><code>
  ssh -i ~/.ssh/onelab.private onelab.inria.mario.tutorial@faraday.inria.fr hostname
  </code></pre>
  <p>If this command fails, then you need to check again the steps described in the previous tutorials</p>

  <center>
    <img src="/assets/img/A1.png" alt="a1"> <br/>
    Download the <a href="/code/A1-ping.py" download target="_blank">A1 experiment</a> code
  </center>
<< codediff a1 A1-ping.py >>
</div>

<!------------ A2 ------------>
<div role="tabpanel" class="tab-pane fade" id="A2" aria-labelledby="profile-tab">
  <br/>
  This time we want to run some command from inside a node, and not from
  inside the gateway. Since there is no way to log into a node directly, we will need to
  define our node object a little differently.
  <br/><br/>
  In addition, you will need to make sure that the testbed is reserved for us at the moment;
  for ensuring complete reproducibility, the testbed is not sharable, and so you need to
  have a valid reservation before you run this experiment;
  see <a href="book.md">the reservation page</a> for seeing the current reservations and create your own.
  <br/><br/>
  Finally, we assume here that the node we use for our experiment is actually turned on.
  We have seen in the previous tutorial how to do this from a manual ssh command to the gateway,
  so we suggest you use this method for now.
  <br/><br/>
  In this example, the command that we run from the node is simply to
  ping the gateway (we could not ping the outside world from a node
  anymore as they do not have this connectivity).
  <center>
    <img src="/assets/img/A2.png" alt="a2"><br/>
    Download the <a href="/code/A2-ping.py" download target="_blank">A2 experiment</a> code
  </center>
<< codediff a2 A1-ping.py A2-ping.py >>
</div>

<!------------ A3 ------------>
<div role="tabpanel" class="tab-pane fade" id="A3" aria-labelledby="profile-tab">
  <br/>
  The experiment below now uses two wireless nodes. We will configure in both nodes the
  wired <strong>experiment interface</strong> (available as
  <code>data</code> under linux) using DHCP.
  <br/><br/>
  Once this is done, we will be able to ping
  the <strong>experiment interface</strong> at </strong>fit02</strong>
  from <strong>fit01</strong>.
  <center>
    <img src="/assets/img/A3.png" alt="a3"><br/>
    Download the <a href="/code/A3-ping.py" download target="_blank">A3 experiment</a> code
  </center>
<< codediff a3 A2-ping.py A3-ping.py >>
</div>

<!------------ A4 ------------>
<div role="tabpanel" class="tab-pane fade" id="A4" aria-labelledby="profile-tab">
  <br/>
  The experiment below is essentially similar to the previous one, but
  illustrates,  rather than using the wired network,
  how to configure and use an ad-hoc wireless network
  between the <strong>wireless interfaces</strong> on our two nodes,
  (exposed in linux as <code>wlan0</code>).

  <br/><br/>
  Once the interfaces are configured, we will ping fit01 and fit02 from one
  another using the <strong>wireless interface</strong>.
  <center>
    <img src="/assets/img/A4.png" alt="a4"><br/>
    Download the <a href="/code/A4-ping.py" download target="_blank">A4 experiment</a> code
  </center>
<< codediff a4 A3-ping.py A4-ping.py >>
</div>

</div> <!-- end div contents -->
