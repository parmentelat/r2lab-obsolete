title: Tutorial : First steps
tab: tutorials
---

# Pre-requisite #

Obtain a slice account on R2LAB (faraday)
# Direct ssh access to the node

Example IP addresses of the target node

* CM card interface : 192.168.1.25
* Experiment interface : 192.168.2.25
* Control interface (OMF) : 192.168.3.25

**1 - Connect to your account in faraday**

    $ ssh my-account@faraday.inria.fr

**2 - Check access and IP address through the CM card**

    $ curl 192.168.1.25/status
    $ curl 192.168.1.25/info
**3 - Try to start and stop the node**

	$ curl 192.168.1.25/on[|off|reset]
**4 - Get the status of the node through OMF**

	$ omf6 stat -t fit25 

**5 - Start the node through OMF**

	$ omf6 tell -t fit25 -a on|off|reset

**6 - Ping the control interface to check that the node received its IP address**

	$ ping 192.168.3.25

**7 - Load the baseline image**

	$ omf6 load -t fit25 [-i baseline.ndz]
The node starts with the PXE image, gets an IP address, downloads the baseline image and restarts, as instructed in `.omf/etc/omf_script_conf.yaml`.   
This can be monitored through `/var/log/upstart/ntrc_frisbee.log`.  
The PXE image is located in `/tftpboot`.  
The baseline image `baseline.ndz` is located in `/var/lib/omf-images-6`.   

**8 - Access the node through ssh (as root)**

	$ ssh fit25

**9 - Save the modified image**

	$ omf6 save -n fit25

# Using short commands through ssh #

**1 - Connect to your account in faraday**

    $ ssh my-account@faraday.inria.fr
**2 - Select the nodes you want to use**
* All available nodes

        $ all-nodes
* A discontinuous set of nodes (e.g., fit15 and fit25)

        $ nodes 15 25
* A continuous set of nodes (e.g., fit30 to fit32)

        $ nodes 30-32
* All nodes currently turned on

        $ focus-nodes-on
* Add / remove a node from the existing list (e.g., fit20)

        $ n+ 20 [n- 20]
        
**3 - Get the status of the nodes**
* Are they turned on or off?

        $ st
Note : It is also possible to run this command directly without making a nodes selection (same for all upcoming commands)

        $ st 15 25
* Which nodes are turned on?
      
        $ show-nodes-on
* Do they answer to a ping command?

        $ wait
* What is their current Linux version?

        $ rel
        
**4 - Start / stop / reset the nodes** 
      
      $ on [off/reset]
      
**5 - Load an image in the selected nodes**    
* Ubuntu 14.10

        $ load-u1410
* Ubuntu 15.04

        $ load-u1504
* Fedora 21

        $ load-f21
* Ubuntu 14.10 with gnuradio installed

        $ load-gr-u1410
* Ubuntu 15.04 with gnuradio installed

        $ load-gr-u1504
* Another image

        $ load-image <myImage>
        
**6 - Run an ssh command on all selected nodes**

        $ map <mycommand>
        
**7 - Find other short commands**

        $ help

# Access with NEPI

Use one of the scripts below

* ![r2lab_testbed_bootstrap.py](./r2lab_testbed_bootstrap.py "r2lab_testbed_bootstrap.py")

This is a maintenance script used to bootstrap the nodes from
INRIA testbed (R2Lab) before running an experiment using Nitos nodes.   
This script loads an image into the nodes (image name can be changed at l. 84)
then resets the nodes, starts the wlan interface without configuring it.
   
Example of how to run this experiment (replace with your information):
   
    $ cd <path-to-nepi>/examples/linux [where the script has been copied]
    $ python r2lab_testbed_bootstrap.py -H <fitXX,fitZZ,..> -U <r2lab-node-username> -i <ssh-key> -g <r2lab-gateway> -u <r2lab-slicename>
    $ python r2lab_testbed_bootstrap.py -H fit12,fit18 -U root -i ~/.ssh -g faraday.inria.fr -u root

* ![r2lab_testbed_reset_eth.py](./r2lab_testbed_reset_eth.py "r2lab_testbed_reset_eth.py")

This is a maintenance script used to reset the nodes from
INRIA testbed (R2Lab) before running a OMF experiment using Nitos nodes.    
This script restarts the nodes, then starts the wlan interface without configuring it.

Example of how to run this experiment (replace with your information):
    
    $ cd <path-to-nepi>/examples/linux [where the script has been copied]
    $ python r2lab_testbed_reset_eth.py -H <fitXX,fitZZ,..> -U <r2lab-node-username> -i <ssh-key> -g <r2lab-gateway> -u <r2lab-slicename>
    $ python r2lab_testbed_reset_eth.py -H fit12,fit18 -U root -i ~/.ssh -g faraday.inria.fr  -u root

* ![r2lab_testbed_reset_wlan.py](./r2lab_testbed_reset_wlan.py "r2lab_testbed_reset_wlan.py")

This is a maintenance script used to prepare the nodes from INRIA 
testbed (R2Lab) before running an OMF experiment using Nitos nodes with WiFi.   
This script restarts the nodes, then starts and configures their 
WLAN interface (ad-hoc mode). IP address, ESSID and channel can be changed at line 118.

Example of how to run this experiment (replace with your information):
    
    $ cd <path-to-nepi>/examples/linux [where the script has been copied]
    $ python r2lab_testbed_reset_wlan.py -H <fitXX,fitZZ,..> -U <r2lab-node-username> -i <ssh-key> -g <r2lab-gateway> -u <r2lab-slicename>
    $ python r2lab_testbed_reset_wlan.py -H fit12,fit18 -U root -i ~/.ssh -g faraday.inria.fr  -u root
    
* ![r2lab_testbed_wlping.py](./r2lab_testbed_wlping.py "r2lab_testbed_wlping.py")

    Testbed : R2LAB   
    
        Node fitXX    
             0   
             |   
             0   
        Node fitYY   
   
    PING OVER WI-FI   
     - Experiment:  
       - t0 : Deployment and configuration   
       - t1 : Ping Start (3 packets sent over the air)  
       - t2 : Kill the application and retrieve traces  


Example of how to run this experiment (replace with your information):
    
    $ cd <path-to-nepi>/examples/linux [where the script has been copied]
    $ python r2lab_testbed_wlping.py -x <fitXX> -y <fitYY> -c <channel> -e <essid> -u <r2lab-slicename> -i <ssh-key> -g <r2lab-gateway> -U <r2lab-node-username>
    $ python r2lab_testbed_wlping.py -x fit12 -y fit18 -c 03 -e fitessai -u root -i ~/.ssh -g faraday.inria.fr -U root

# X11 Access (to be confirmed)   
 1 - Install `xterm`  on the target node (e.g., fit25)
 
    $ apt-get update
    $ apt-get install xterm   
 2 - Connect to faraday from your user host with the "-X" option

    $ ssh -X my-account@faraday.inria.fr
 3 - Hop to the Nitos node with the "-X" option

    $ ssh -X fit25
 4 - Launch `xterm` to obtain the graphic display of the node
 
    $ xterm
