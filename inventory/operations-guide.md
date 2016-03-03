# Operations Guide

## BIOS Settings

The BIOS installed is Phoenix SecureCore, version LV-67N Ver: 1.2; procedure to upgrade the BIOS still in the old google drive, together with the manufacturer's doc BTW

### Magic keys

* Use these keys right after you listen to the first BEEP;
* when taken into account you'll hear a second BEEP to acknowledge
  * `<DEL>` to reach the BIOS menu
  * `<F5>` to reach the boot menu

### R2lab BIOS settings:

* RESET to factory defaults
* Configure time
* Main -> Boot Features
  * quick boot enabled
* Advanced-> HDD configuration
  * IDE mode
* Advanced->Network configuration
  * LAN OPROM Enabled
* Boot order : 
  1. the 2nd Lan interface (something like PCI LAN2)
  1. then hard drive (ssd in fact)

### Notes on IDE *vs* AHCI

The pxefrisbee image does not hold the required drivers to be able to write on AHCI

## How to remap nodes in R2lab

When a node is broken, you want to replace it with another spare node.
This requires root access on faraday and bemol, and can be achived like this:

* Of course perform the physical replacement
* Then to apply changes, do the following; 

```
$ cd r2lab/inventory
$ emacs r2lab.map
$ make remap
```

The syntax in `r2lab.map` should be self-explanatory, but in case it's not, make sure you only change the 'room-slot' column for each node, and that of course you mention one room slot only once.

***NOTE*** at this point there's a little more things to do manually so that the convenience tools on bemol (i.e. `all-nodes`) is aware of the change; see inventory/Makefile for details on how to handle that; hopefully will be improved in the future.


## How to check/troubleshoot a node

***This section is in the works***

Before you go down with a spare node under your arm, you may wish to check the following

* connect the spare node in the preplab
* run a couple of load-ubuntu / load-fedora in alternance, and check the expected version is indeed installed; that's what the nightly does in fact
  * beware to stay away from old ubuntu images that sometimes hang on prompting for whether or not an fsck is desired
* if this works as expected **your node is fine**

Otherwise

* make sure it correctly answers `reset` commands
  * that is to say, when the node is turned on and you send a reset, you hear the beep and the motherboard reloads its BIOS for rebooting
  * try again
* if not
  * need to determine if the BIOS settings are fine at least wrt Boor Order **need to be more explicit here**
  * if this might be the problem, check BIOS settings and try again
* if not
  * remove power plug from the node so as to clear its CMC card
  * ***not sure how long this is needed***
  * try again
* if still not
  * remove its battery for one minute
  * put it back
  * and reset BIOS settings as above
  * try again

***... to be reviewed / finalized / continued... ***
