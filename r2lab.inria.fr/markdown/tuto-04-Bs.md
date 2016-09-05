title: NEPI - File Exchange
tab: tutorial
float_menu_template: r2lab/float-menu-tutorials.html
---

<script src="/assets/js/diff.js"></script>
<script src="/assets/r2lab/r2lab-diff.js"></script>
<style>@import url("/assets/r2lab/r2lab-diff.css")</style>

Below are a couple of experiments as a second level of learning
[NEPI](http://nepi.inria.fr/Install/WebHome) network tool and R2lab
simulation testbed.

The experiments were made with an increment level from **B1** to
**B2** to allow better subject understanding.

From one experiment to other, like git style, we highlight the
modifications, insert and delete actions by different colors to
improve the user experience learning. In most of the experiments cases
a picture explaining the scenario are presented to help the experiment
comprehension.

In addition to what we have seen in the previous experiments (A1-A4), we will now see two other features of NEPI.

* the `register_condition` is going to help us model dependencies
  between the various pieces of an experiment, for example in our
  scenario, to ensure that **fit01** sends traffic only when **fit02**
  is ready to receive it;

* and the `depends` tag of an application will help us deal with
  software dependencies, so that e.g. `netcat` gets installed before
  we can use it.

<br/>

<ul id="myTabs" class="nav nav-tabs" role="tablist">
  <li role="presentation" class="active">
    <a href="#B1" id="B1-tab" role="tab" data-toggle="tab" aria-controls="B1" aria-expanded="true">B1</a>
  </li>
  <li role="presentation" class="">
    <a href="#B2" role="tab" id="B2-tab" data-toggle="tab" aria-controls="B2" aria-expanded="false">B2</a>
  </li>
</ul>

<div id="contents" class="tab-content">

<!------------ B1  ------------>
<div role="tabpanel" class="tab-pane fade active in" id="B1" aria-labelledby="home-tab">
  <br/>
  The experiment below uses four nodes. From your computer you will
  create and deploy <strong>local</strong>, <strong>gateway</strong>,
  <strong>fit01</strong> and <strong>fit02</strong> nodes.
  <br/><br/>
  From <strong>local</strong> you will copy <code>file.txt</code> to
  R2lab <strong>gateway</strong> node, which in turn will copy the same
  file to <strong>fit02</strong> node. Both copies file will use
  <code>scp command</code>.
  <br/><br/>
  Once the file is present in <strong>fit02</strong> node, you will
  start <code>nc</code> (a.k.a. netcat) at <strong>fit01</strong> to
  listen in port 1234.  After <strong>fit01</strong> starts listening
  in 1234 port, <strong>fit02</strong> node will transmit the file
  also using <code>nc</code>.  The transmission from
  <strong>fit02</strong> to <strong>fit01</strong> use the wired
  <strong>control interface</strong>.

  Then, the terminal call should be:<br>
  <pre><code>$ python B1-send-file.py -s01 -r02 my_local_file.ext </code></pre>
  where, <code>-s</code> means the <b>sender</b> node, <code>-r</code> refers to the <b>receiver</b> node and <b>my_local_file</b> is the file you want
  transmit from sender node to receiver one.
  <br>
  Other options can be checked typing <b>-h</b>, or:<br>
  <pre><code>$ python B1-send-file.py -h </code></pre>

  <center>
    <img src="/assets/img/B1.png" alt="b1"><br/>
    Download the <a href="/code/B1-send-file.py" download target="_blank">B1 experiment</a> code
  </center>

<< codediff b1s B1-send-file.py >>
</div>

<!------------ B2 ------------>
<div role="tabpanel" class="tab-pane fade" id="B2" aria-labelledby="profile-tab">
  <br/>

  The experiment below are the same as the previous (B1), however here,
  to send the file from <strong>fit02</strong> to
  <strong>fit01</strong>, you will use the wireless interface instead of
  the wired one.

  <center>
    <img src="/assets/img/B2.png" alt="b2"><br/>
    Download the <a href="/code/B2-send-file.py" download target="_blank">B2 experiment</a> code
  </center>

<< codediff b2s B1-send-file.py B2-send-file.py >>
</div>

</div> <!-- end div contents -->
