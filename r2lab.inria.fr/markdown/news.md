title: Latest news, infos and incidents...
tab: news
skip_news: yes
---

# Most recent first&nbsp;:

****
## 2016
****

### November 30 2016

* All tutorials now point at `nepi-ng` instead of deprecated `nepi`

### November 26 2016

* [R2lab Anechoic Chamber on WebTimeMedia.]http://www.webtimemedias.com/article/sophia-inaugure-ses-deux-chambres-sourdes-laboratoires-de-la-5g-20161104-58944

### November 9 2016

* [Inauguration ceremony - see detailed program here.](https://www.inria.fr/en/centre/sophia/calendar/r2lab-anechoic-chamber-a-heterogeneous-wireless-testbed)

* Slides available below:

  * [Keynote by Max Ott](../assets/files/2016-11-opening-keynote-max-ott.pdf)
  * [FIT Equipex, by Éric FLeury](../assets/files/2016-11-opening-fit-eric-fleury.pdf)
  * [FIT/CortexLab, by Tanguy Risset](../assets/files/2016-11-opening-cortexlab-tanguy-risset.pdf)
  * [FIT/R2lab, by Walid Dabbous](../assets/files/2016-11-opening-r2lab-walid-dabbous.pdf)
  * [OpenAirInterface, by Raymond Knopp](../assets/files/2016-11-opening-openairinterface-raymond-knopp.pdf)
  * [Demo on R2lab: setting up a 4G network in 3mn, by Thierry Parmentelat](../assets/files/2016-11-opening-r2lab-demo-thierry-parmentelat.pdf)


### November 4

* R2lab is [mentioned and described in this article in the WebTimeMedias newspaper (in French)](http://www.webtimemedias.com/article/sophia-inaugure-ses-deux-chambres-sourdes-laboratoires-de-la-5g-20161104-58944)

### October 24

* OpenAirInterface images for deploying infrastructures and eNodeB's are available under the names
  * `u14.319-oai-enb` for eNodeB's and scramblers and such
  * `u14.48-oai-gw` for infrastructure services like Home Subscriber Server (HSS) and Evolved Packet Core (EPC)

### October 15

* We have now 6 nodes equipped with USRP's

### October 1

* We now use [an automated tool](https://github.com/parmentelat/r2lab/blob/master/infra/builds/build-image.py) for building images [on a nightly basis](https://github.com/parmentelat/r2lab/blob/master/infra/builds/all-images.sh)

### September 15

* We have been working on a replacement for NEPI
* We have published 2 python libraries on pypi
  * [`asynciojobs`](https://github.com/parmentelat/asynciojobs)
  * [`apssh`](https://github.com/parmentelat/apssh), see also [this link](https://github.com/parmentelat/apssh/blob/master/README-jobs.md)
* We have [our first workable script](https://github.com/parmentelat/r2lab/blob/master/demos/jobs-angle-measure/angle-measure.py) that uses this combination of tools for running an experiment on R2lab
* You can compare with [the same experiment written with NEPI](https://github.com/parmentelat/r2lab/blob/master/demos/nepi-angle-measure/angle-measure.py)
* This new paradigm runs several times faster than the initial version.

### September 2

* upgrade of the physical server `faraday.inria.fr` to ubuntu-16.04-LTS
* upgrade of its web companion VM `r2lab.inria.fr` to fedora-24

* this means both hosts can take `systemd` and `python3.5` for granted
* in the mix, `omf_sfa` on `faraday` now runs on top of `ruby 2.3.1p112`

### August 30

* The R2lab team pays a visit to [our colleagues of FIT/CorteXlab at INSA Lyon](http://www.cortexlab.fr/)

### July 25

* Both faulty nodes 4 and 18 are shipped back to Greece for troubleshooting by the manufacturer

### July 13

* Node 18 is set aside and replaced with a spare node (no impact for users)
* All nodes deemed sustainably operational
* Nightly routine now is from 3a.m. until 4a.m.

### June 17

* New tutorial video! Setting up an OpenAirInterface-based 5G infrastructure, and a tour in the chamber using Skype on a commercial NEXUS phone.
* Check it out, [here](https://youtu.be/FpZo6uqTosQ)

### June 6

* Replacement of battery on nodes 7, 14, 18, 29 and 30 to deal with hang issues when restarting.

### March 17

* The 3d printed boxes are ready to ship

### Feb 28

* Start progressive rollout of a new layout for antennas
* Antennas to be aligned in a row, on a north-south line (relative to the livemap, not geographically)
* And spaces on a 3cm basis (although this seems a little too wide)

### Feb 25

* Start Progressive deployment of Intel 5300 cards.
  * Target is one Atheros and one Intel on each node

### Feb 20
* Ordered 3d-printed boxes to contain cards as they cannot be seated inside the box

### Feb 2 2016

* Reception of USRP-oriented extensions of the CMC cards
* Related firmware version is 3.2.
* Deployed on only a couple nodes for now

****
## 2015
****

### December 20, 2015

* Announcement of global availability; the testbed is now open to public use.

### November 30

* Deployment of [rhubarbe](https://github.com/parmentelat/rhubarbe) as a replacement of `omf6` for managing node images. New features include
  * written in [python 3 / asyncio](https://docs.python.org/3/library/asyncio.html) which results in a single threaded asynchroneous application
  * which makes it much more efficient than its ruby ancestor (can load all 37 nodes in parallel without a glitch)
  * and more reliable too (**always** exits if timeout expires for any reason)
  * includes a tool to wait for all nodes to be responsive (`rhubarbe wait`)
  * and to inspect current reservations (`rhubarbe leases`)
  * as well as a monitoring tool (this is what feeds the [livemap](status.md#livemap) and [livetable](status.md#livetable) views

* As a result, it is now possible for us to expose a single resource named `37nodes` to the onelab portal, thus materializing the fact that the whole testbed is actually reserved

### November 10

* availability of images based on fedora-23 and ubuntu-15.10

### November 9

* reverting `nitos_testbed_rc` to run gem 2.0.3 again (with our patches for
  using latest frisbee) ; 2.0.4 is not working properly for us, loading
  images is even less reliable than 2.0.3.

### November 6

* Announce availability to all FIT partners

### November 6

* Software upgrade
  * `omf_sfa`  now runs git hash `fd21d587` of Sept. 8 - prior to that, R2Lab was using
  `752868919` of Jul. 24
  * `nitos_testbed_rc` now runs gem 2.0.4

### September 22

* LabEx / Com4Innov meeting

### September 15
* R2lab Platform Live Map : we are working to finish a live map information of the R2Lab platform.

### September 5
* R2lab Platform Status : from today is possible follow the tech details of R2lab platform.

* We are monitoring some informations from the nodes in the anechoic chamber.
Have a look at [our status page](status.md#livemap) for details.

### July 9 2015
* FIT Meeting in Paris.
