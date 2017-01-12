# infra

* install SSL certificates
* tweak https config so that `fit-r2lab.inria.fr` points at `r2lab.inria.fr`
* set up **backups on r2labapi** including PLCAPI db

# web UI (Mario)

* iron out leases management
  * cf mail to Mario
* manage ssh keys

# nightly

* **delayed** infer presence and type of usrp devices - delayed, **done manually for now**
* On that subject, we **badly need** to get back to some **convergence** between `sidecar` and the `r2lab/nodes` thingy so as to 
  * remove data duplication
  * ease out publication path

# images

* **OpenAirInterface** 
  * rebuild enb images as per Rohit/OAI's instructions proper
  * try these again
* **Fedora25**
  * first attempt on fit42 has failed due to caveats in frisbee
  * would be nice to find a way to do installation on a disk that **we** partition; damn fedora install program won't let us at first sight.

# monitor

* **investigate potential reliability issues**
  * I suspect sometimes `probe` just hangs
  * also I've already seen monitorphones being down - it's not supposed to survive a broken ssh connection to `macphone` - (check this again, as it might be done already)
* ~~report usrpstatus (on or off)~~
* ~~either in monitor, or in a companion: check for the phone to be turned (on or off)~~
* ~~make sure the 'image_radical' data (from rhubarbe-image) is correctly detected (feels like names with a dot `.` get trimmed)~~

# miscell

* ~~**try to show past leases somehow**~~

# sidecar

* ~~provision for information about the phone (on or off)~~
* ~~provision for data about USRP (presence of devices, on or off in the CMC)~~

