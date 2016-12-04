title: nepi-ng - troubleshooting
tab: tutorial
skip_header: True

<script src="/assets/r2lab/open-tab.js"></script>
<script src="/assets/js/diff.js"></script>
<script src="/assets/r2lab/r2lab-diff.js"></script>
<style>@import url("/assets/r2lab/r2lab-diff.css")</style>

<ul class="nav nav-tabs">
  <li class="active"> <a href="#INTRO">INTRO</a> </li>
  <li> <a href="#TROUBLESHOOTING">TROUBLESHOOTING</a></li>
  << include r2lab/tutos-index.html >>
</ul>

<div id="contents" class="tab-content" markdown="1">

<!------------ INTRO ------------>
<div id="INTRO" class="tab-pane fade in active" markdown="1">

### This page is under construction...

[](javascript:open_tab('TROUBLESHOOTING'))

</div>

<!------------ TROUBLESHOOTING ------------>
<div id="TROUBLESHOOTING" class="tab-pane fade" markdown="1">

# Objectives

In this page we are going to see a few guidelines for troubleshooting a `nepi-ng` script.

## Check for the obvious

Before you start diving in the code, it is **always** a good idea to
step back a little, and to check for the following common mistakes.

This is especially true when you start with `nepi-ng` and `R2lab, and
your scripts are not sophisiticated enough to do all this checks by
themselves.

Also these common sources of glitches occur frequently if you were
working on your scenario, and then your time went up, you are now just
back to the testbed.

### Do you have a valid reservation on the testbed ?

If your script does not check for that, it's a good idea to double check.

### Are the nodes up ?

### Do they have the expected image ?

You can check all your nodes with a session like this (when logged in `faraday`)

    # assuming we need nodes 4, 6, 8 and from 10 to 15 inclusive
    
    $ rleases --check
    Checking current reservation for onelab.inria.r2lab.tutorial OK
    
    onelab.inria.r2lab.tutorial@faraday:~$ n 4 6 8 10-15
    export NODES="fit04 fit06 fit08 fit10 fit11 fit12 fit13 fit14 fit15"
    export NBNODES=9
    
    onelab.inria.r2lab.tutorial@faraday:~$ rwait
    <Node fit04>:ssh OK
    <Node fit06>:ssh OK
    <Node fit08>:ssh OK
    <Node fit10>:ssh OK
    <Node fit11>:ssh OK
    <Node fit12>:ssh OK
    <Node fit13>:ssh OK
    <Node fit14>:ssh OK
    <Node fit15>:ssh OK

    onelab.inria.r2lab.tutorial@faraday:~$ map rimage
    fit10:2016-11-29@00:12 - built-on fit03 - from-image fedora-23-v10-wireless-names - by onelab.inria.r2lab.tutorial
    fit12:2016-11-29@00:12 - built-on fit03 - from-image fedora-23-v10-wireless-names - by onelab.inria.r2lab.tutorial
    fit15:2016-11-29@00:12 - built-on fit03 - from-image fedora-23-v10-wireless-names - by onelab.inria.r2lab.tutorial
    fit06:2016-11-29@00:12 - built-on fit03 - from-image fedora-23-v10-wireless-names - by onelab.inria.r2lab.tutorial
    fit11:2016-11-29@00:12 - built-on fit03 - from-image fedora-23-v10-wireless-names - by onelab.inria.r2lab.tutorial
    fit14:2016-11-29@00:12 - built-on fit03 - from-image fedora-23-v10-wireless-names - by onelab.inria.r2lab.tutorial
    fit04:2016-11-29@00:12 - built-on fit03 - from-image fedora-23-v10-wireless-names - by onelab.inria.r2lab.tutorial
    fit13:2016-11-29@00:12 - built-on fit03 - from-image fedora-23-v10-wireless-names - by onelab.inria.r2lab.tutorial
    fit08:2016-11-29@00:12 - built-on fit03 - from-image fedora-23-v10-wireless-names - by onelab.inria.r2lab.tutorial    	  

### `Scheduler.debrief()`

In all our examples so far, you have noticed that we run a scheduler like this :

    # run the scheduler
    ok = scheduler.orchestrate()
    # give details if it failed
    ok or scheduler.debrief()

This means that, if ever `orchestrate()` does not return `True`, we run the `debrief()` method on that scheduler.





### Verbosity

You can enable more verbosity in any of the following classes. 

### Next
xxx [next tuto: load images](javascript:open_tab('LOAD_IMAGES'))

</div>

</div> <!-- end div contents -->
