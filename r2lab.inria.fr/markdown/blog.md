title: Latest news, infos and incidents...
tab: blog
---

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
