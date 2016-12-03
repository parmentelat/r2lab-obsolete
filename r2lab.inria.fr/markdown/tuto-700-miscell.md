title: nepi-ng - miscellaneous
tab: tutorial
skip_header: True

<script src="/assets/r2lab/open-tab.js"></script>
<script src="/assets/js/diff.js"></script>
<script src="/assets/r2lab/r2lab-diff.js"></script>
<style>@import url("/assets/r2lab/r2lab-diff.css")</style>

<ul class="nav nav-tabs">
  <li class="active"> <a href="#INTRO">INTRO</a> </li>
  <li> <a href="#TROUBLESHOOTING">TROUBLESHOOTING</a></li>
  <li> <a href="#LOAD_IMAGES">LOAD IMAGES</a></li>
  <li> <a href="#MULTI_PING">MULTI_PING</a></li>

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

### Objective

### The code

<< codeview D1 D1-troubleshooting.py >>

### Sample output

### Next
[next tuto: load images](javascript:open_tab('LOAD_IMAGES'))

</div>

<!------------ LOAD_IMAGES ------------>
<div id="LOAD_IMAGES" class="tab-pane fade" markdown="1">

### Objective

In this scenario, we will slightly modify [the C3
scenario](tuto-600-files.md#C3), and add to it the ability to load
images on the two nodes involved before the C3 scenario actually
triggers.

To this end, we add a new command line option to the script, that
users can use to request image loading. 

Remember that the C3 scenario is about creating a local random file,
and have it circulate from your laptop to fit01, then fit02, and back
to your laptop.

### New `nepi-ng` features

There is not much new involved in this script, as far as `nepi-ng` is
concerned.  We just add the ability to simply create an additional
`SshJob` that runs on the `faraday` gateway, and that is in charge of:

* loading the image on our selected nodes
* waiting for these nodes to come back up
* and, in the mix, turn off all other nodes in the testbed.

What takes some care, depending on the context, is the definition of
the `required` relationship; of course the part of the experience that
actually needs the nodes to be up, has to mention this extra job as a
dependency. In our case we have defined an intermediate variable
`green_light_jobs` that contains a list of the jobs that the first
experimental job - `push_job` in this case - needs to wait for before
taking off.

### `rhubarbe` features used

For turning off unused nodes, we take advantage of the `rhubarbe`
selection mechanism, where you can say e.g.

    rhubarbe nodes -a ~1 ~2 ~4-12 ~15-28-2 ~30-100
    fit03 fit13 fit14 fit16 fit18 fit20 fit22 fit24 fit26 fit28 fit29

We have written the code so that you can reuse the same fragment,
just define the list of nodes in a `node_ids` variable.

### The code

<< codeview C4 C3-files.py C4-files.py >>

### Sample output

    $ python3 C4-files.py --load
    faraday.inria.fr:Checking current reservation for onelab.inria.r2lab.tutorial OK
    LOCALNODE:-rw-r--r--  1 parmentelat  staff  1024 Dec  3 16:31 RANDOM
    LOCALNODE:22aaa184304f7202dc2554839d5e6c09fe6757ba  RANDOM
    faraday.inria.fr:reboot21:ok
    faraday.inria.fr:reboot36:already off
    <..snip..>
    faraday.inria.fr:reboot23:already off
    faraday.inria.fr:reboot09:already off
    faraday.inria.fr:16:31:28 - +000s: Selection: fit01 fit02
    faraday.inria.fr:16:31:28 - +000s: Loading image /var/lib/rhubarbe-images/ubuntu.ndz
    faraday.inria.fr:16:31:28 - +000s: AUTH: checking for a valid lease
    faraday.inria.fr:16:31:28 - +000s: AUTH: access granted
    faraday.inria.fr:16:31:28 - +000s: fit01 reboot = Sending message 'reset' to CMC reboot01
    faraday.inria.fr:16:31:28 - +000s: fit02 reboot = Sending message 'reset' to CMC reboot02
    faraday.inria.fr:16:31:30 - +002s: fit01 reboot = idling for 15s
    faraday.inria.fr:16:31:30 - +002s: fit02 reboot = idling for 15s
    faraday.inria.fr:16:31:48 - +020s: started <frisbeed@234.5.6.3:10003 on ubuntu.ndz at 500 Mibps>
    faraday.inria.fr:16:31:48 - +020s: fit01 frisbee_status = trying to telnet..
    faraday.inria.fr:16:31:48 - +020s: fit02 frisbee_status = trying to telnet..
    faraday.inria.fr:16:31:50 - +022s: fit01 frisbee_status = timed out..
    <..snip..>
    faraday.inria.fr:16:32:10 - +042s: fit02 frisbee_status = trying to telnet..
    faraday.inria.fr:16:32:10 - +042s: fit02 frisbee_status = starting frisbee client
    faraday.inria.fr:16:32:25 - +057s: fit01 Uploading successful
    faraday.inria.fr:16:32:25 - +057s: fit01 reboot = Sending message 'reset' to CMC reboot01
    |###################################################|100% |33.98s|Time: 0:00:330s|ETA:  --:--:--
    faraday.inria.fr:16:32:34 - +066s: fit02 Uploading successful
    faraday.inria.fr:16:32:34 - +066s: fit02 reboot = Sending message 'reset' to CMC reboot02
    faraday.inria.fr:16:32:36 - +068s: stopped <frisbeed@234.5.6.3:10003 on ubuntu.ndz at 500 Mibps>
    faraday.inria.fr:<Node fit01>:ssh OK
    faraday.inria.fr:<Node fit02>:ssh OK
    fit01:-rw-r--r-- 1 root root 1024 Dec  3 16:33 RANDOM
    fit01:22aaa184304f7202dc2554839d5e6c09fe6757ba  RANDOM
    fit01:turn-on-data: data network on interface data
    fit02:turn-on-data: data network on interface data
    fit01:data
    fit02:data
    fit01:SENDER DONE
    fit02:-rw-r--r-- 1 root root 1024 Dec  3 16:33 RANDOM
    fit02:22aaa184304f7202dc2554839d5e6c09fe6757ba  RANDOM
    fit02:the Pull command runs on fit02
    LOCALNODE:-rw-r--r--  1 parmentelat  staff  1024 Dec  3 16:33 RANDOM.loopback
    LOCALNODE:RANDOM.loopback identical to RANDOM
    
### Next
[next tuto: multi-ping](javascript:open_tab('MULTI_PING'))

</div>

<!------------ MULTI_PING ------------>
<div id="MULTI_PING" class="tab-pane fade" markdown="1">

### Objective

### The code

<< codeview D3 D3-multi-ping.py >>

### Sample output

</div>

</div> <!-- end div contents -->
