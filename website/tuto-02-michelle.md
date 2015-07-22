title: SSH access
tab: guides
---

###Pre-requisite #

[Obtain a slice account on R2LAB (faraday)](tuto-01-registration.html)


###Direct ssh access to the node

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

###Using short commands through ssh #

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
