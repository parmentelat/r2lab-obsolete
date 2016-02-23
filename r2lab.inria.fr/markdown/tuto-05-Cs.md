title: NEPI - Load Images
tab: tutorial
float_menu_template: r2lab/float_menu-tutorials.html
---

Below we present an experiment which will conduct a load image using [NEPI](http://nepi.inria.fr/Install/WebHome) network tool at R2lab simulation testbed. 

You will be able load and control the most common Linux distros at R2lab testbed as root user. We provide the most recent Ubuntus and Fedoras for all users.

<br>

<ul id="myTabs" class="nav nav-tabs" role="tablist">
  <li role="presentation" class="active">
    <a href="#C1" id="C1-tab" role="tab" data-toggle="tab" aria-controls="C1" aria-expanded="true">C1</a>
  </li>
</ul>

<div id="contents" class="tab-content">

<div role="tabpanel" class="tab-pane fade active in" id="C1" aria-labelledby="home-tab">
  <br/>
  From your computer you will create and deploy <strong>gateway</strong> and <strong>fit01</strong> nodes. Once in R2lab <strong>gateway</strong> node you launch the code to load a fresh distro at <strong>fit01</strong> node. 
  <br><br>
  At the end, you will create also an application at the <strong>fit01</strong> node to check if the version corresponds as expected.

  <center>
    <img src="/assets/img/C1.png" alt="c1"><br>
    Download the <a href="/code/C1-load.py" download target="_blank">C1 experiment</a> code
  </center>
  

<pre data-src="prism.js"  data-line="" class="line-numbers"><code class="language-python">
<< codediff C1-load.py >>
</code></pre>
</div>
</div>

