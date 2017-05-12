title: 5G offering
tab: tutorial
skip_header: True

<script src="/assets/r2lab/open-tab.js"></script>
<script src="/assets/js/diff.js"></script>
<script src="/assets/r2lab/r2lab-diff.js"></script>
<style>@import url("/assets/r2lab/r2lab-diff.css")</style>


<ul class="nav nav-tabs">
  <li class="active"> <a href="#INTRO">INTRO</a> </li>
  <li> <a href="#PHONE">PHONE</a></li>
  <li> <a href="#OAI-IMAGES">OAI IMAGES</a></li>
  <li> <a href="#WRAPUP">WRAPUP</a></li>

  << include r2lab/tutos-index.html >>
</ul>


<div id="contents" class="tab-content" markdown="1">

<!------------ INTRO ------------>
<div id="INTRO" class="tab-pane fade in active" markdown="1">

### The pieces

As of Nov. 2016, the following pieces are made available to R2lab users

* a commercial phone is deployed inside the room; it can be controlled through a dedicated MAC box, to which it is linked with a USB cable;
* we offer 2 ready-to-use images, tuned for the R2lab nodes, and with the OpenAiInterface software installed; they target, on the one hand, the infrastructure side of a LTE network, and on the other hand radio-oriented functions, like base stations and UEs.

These pieces are described in more detail in this section of the tutorial

</div>

<!------------ PHONE ------------>
<div id="PHONE" class="tab-pane fade" markdown="1">

### Phone setup

Here's the setup regarding the commercial phone

<img src="/assets/img/macphone.png"  width='500px'>

### From `faraday` to controlling MAC `macphone`
* controlling MAC is known from `faraday.inria.fr` as `macphone`
* however you need a private key to login; this is located in `/home/faraday/r2lab/inventory/macphone`
* so for convenience on `faraday` you can use the `macphone` alias that calls `ssh` with the right options

So for example to run the `macphone-status` command on the MAC, you can do this


    inria_r2lab.tutorial@faraday:~$ macphone phone-status && echo OK
    phone is turned ON
    OK

Or more simply if you just want to login into the MAC box, you can do this

    inria_r2lab.tutorial@faraday:~$ macphone
    Last login: Fri May 12 14:50:13 2017 from rhubarbe-switches
    macphone:~ tester$

### From `macphone`

Once on `macphone`, just like on faraday, there are some convenience tools available in this shell environment

    macphone:~ tester$ help
    #################### Native bash help
    <snip>
    #################### R2lab: tools for managing R2lab phone from macphone
    refresh 	retrieve latest git repo, and source it in this shell
    phone-start-app
    		start an app from its package name
    phone-wifi-on   turn on wifi (tested on nexus 5)
    phone-wifi-off  turn off wifi (tested on nexus 5)
    phone-on	    turn off airplane mode
    phone-off       turn off airplane mode - does not touch wifi settings
    phone-status    shows wheter airplane mode is on or off
    phone-reboot    reboot phone with abd reboot

You can also of course use `adb`, and thus eventually enter the phone itself

    macphone:~ tester$ adb devices
    List of devices attached
    062337da0051af9f	device
    
    macphone:~ tester$ adb shell
    shell@hammerhead:/ $

### VNC access

Another way to control the phone is through VNC, or equivalently the *Screen Sharing* application if your own computer is a MAC. This way you can obtain a video session in `macphone`, as illustrated below, and from that point you can run the *Vysor* application and see the phone screen, and interact with it as if it were in your hand.

<img src="/assets/img/screen-sharing.png" width='500px'>

For this you will need the following information:
* VNC endpoint : `faraday.inria.fr` on port 5900 - this port is forwarded to `macphone` on same port
* login credentials in `macphone` : `tester` / `tester++` 

### SIM card
* There is no reason why you would need this, but if only for the record:
* the phone's SIM card PIN is `1234`

</div>

<!------------ OAI-IMAGES ------------>
<div id="OAI-IMAGES" class="tab-pane fade" markdown="1">

### Images

The following images are available for uploading on R2lab:

* `oai-gw` comes with primarily `openair-cn` (from [this git repo](https://gitlab.eurecom.fr/oai/openair-cn.git))
* `oai-enb` comes with primarily `openairinterface5g` (from [this git repo](https://gitlab.eurecom.fr/oai/openairinterface5g.git))

Please note that the latter one only makes sense on nodes that have a
USRP attached. The former on the other hand can run on any node.

### Typical setup

For more details on how to run a 5G network inside the room, please
take a look in the R2lab git repo at [the OpenAirInterface
demo](https://github.com/parmentelat/r2lab/tree/public/demos/oai-skype)
and in particular [the source code](https://github.com/parmentelat/r2lab/blob/public/demos/oai-skype/oai-scenario.py) for
`oai-scenario.py`.

This script leverages these 2 images in order to create a setup where

* one (any) R2lab node is used to run a 5g HSS,
* one (any) R2lab node is used to run a 5g EPC and a 5g SPGW,
* one (USRP) node is used to run as a 5g Base Station,
* the commercial phone is used to connect to the 5G network;

Both images come with their own set of convenience shell functions,
and these are leveraged in `oai-scenario.py` in order to keep that
python script's size reasonable. Of course you do not have to use these convenience tools, you can use lower level tools to perform the configurations that you'd like.

For the sake of completeness, the convenience tools available on these 2 images are defined here:

* `nodes.sh` is what all regular nodes already have [(source code)](https://github.com/parmentelat/r2lab/blob/public/infra/user-env/nodes.sh) 
* `oai-common.sh` is relevant on both images [(source code)](https://github.com/parmentelat/r2lab/blob/public/infra/user-env/oai-common.sh) 
* `oai-gw.sh` is exposed in the `oai-gw` image [(source code)](https://github.com/parmentelat/r2lab/blob/public/infra/user-env/oai-enb.sh) 
* `oai-enb.sh` is exposed in the `oai-enb` image [(source code)](https://github.com/parmentelat/r2lab/blob/public/infra/user-env/oai-epc.sh) 

There is room for quite some improvement in these tools; if of interest, feel free to discuss this topic [on the users mailing list](mailto:fit-r2lab-users@inria.fr).

</div>

<!------------ WRAPUP ------------>
<div id="WRAPUP" class="tab-pane fade" markdown="1">

The software and hardware featured at R2lab allow to setup an experimental 5G network inside the anechoic chamber.

As of now, the simplest option is to use a commercial phone to act as the tip of the iceberg in this setup.

It is in principle doable to run a UE inside a R2lab as well, but we have no working implementation of that as of yet.

Again, feel free to discuss this topic [on the users mailing list](mailto:fit-r2lab-users@inria.fr).

</div>

</div> <!-- end div contents -->
