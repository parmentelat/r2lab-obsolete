title: nepi-ng - wireless
tab: tutorial
skip_header: True

<script src="/assets/r2lab/open-tab.js"></script>
<script src="/assets/js/diff.js"></script>
<script src="/assets/r2lab/r2lab-diff.js"></script>
<style>@import url("/assets/r2lab/r2lab-diff.css")</style>


<ul class="nav nav-tabs">
  <li class="active"> <a href="#INTRO">INTRO</a> </li>
  <li> <a href="#B1">B1</a></li>
  <li> <a href="#B2">B2</a></li>
  <li> <a href="#WRAPUP">WRAPUP</a></li>

  << include r2lab/tutos-index.html >>
</ul>


<div id="contents" class="tab-content" markdown="1">

<!------------ INTRO ------------>
<div id="INTRO" class="tab-pane fade in active" markdown="1">

### This page is under construction...

<br/>
<br/>
<br/>

### Prerequisites

For this series of experiments, we make the same assumptions as in the
previous series. In a nutshell, we expect you have a valid
reservation, and the 2 nodes `fit01`and `fit02` are properly loaded with
the default image, and turned on of course.

Please [visit this page](http://r2lab.inria.fr/tuto-400-ping.md#INTRO)
to review how to reach that point, if necessary.

### Objectives

In this series we will start playing with the wireless interfaces. Of
course a minimal background is assumed in terms of dealing with
wireless interfaces under linux; further information can be found at
the following locations :

* we recommend to see [this quick introduction to `iw`, that is
  instrumental in these
  tasks](https://wireless.wiki.kernel.org/en/users/documentation/iw)

* as well as [this helpful page on how to use `iw` if you were more
  familiar with `iwconfig` that is now considered
  obsolete](https://wireless.wiki.kernel.org/en/users/documentation/iw/replace-iwconfig) -
  much like `ip` has now replaced `ifconfig`.

### `nepi-ng`

Now as far as `nepi-ng` is concerned, in the previous series we have
seen ways to run remotely simple commands. In this section we will see
simple means to come up with more complex logic, simply by using shell
scripts that are pushed remotely under the hood before they are
triggered. This is what the `RunString` and `RunScript` classes are
about.


</div>

<!------------ B1 ------------>
<div id="B1" class="tab-pane fade" markdown="1">

### Objective

We are going to run the exact same experiment [as in the previous run
A5](tuto-400-ping.md#A5), that is to say a simple ping triggered on
`fit01` towards `fit02`, but this time on one of the wireless
interfaces.

What changes then, as compared with our previous experiment, is that
we cannot anymore simply run the predefined convenience command
`data-up`, and we are going to have to put a little more work in this
step.


### The code

<center>Download the <a href="/code/B1-wireless.py" download target="_blank">B1 experiment</a> code</center>

<< codeview B1 A5-ping.py B1-wireless.py >>

### Sample output

### Next
[](javascript:open_tab(''))

</div>

<!------------ B2 ------------>
<div id="B2" class="tab-pane fade" markdown="1">

### Objective

### The code

<center>Download the <a href="/code/B2-wireless.py" download target="_blank">B2 experiment</a> code</center>

<< codeview B2 B1-wireless.py B2-wireless.py >>

### Sample output

### Next
[](javascript:open_tab(''))

</div>

<!------------ WRAPUP ------------>
<div id="WRAPUP" class="tab-pane fade" markdown="1">

</div>

</div> <!-- end div contents -->
