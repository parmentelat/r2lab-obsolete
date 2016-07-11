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

The `pxefrisbee` image does not contain the required drivers to be able to write on AHCI; that's why we are left with only the option to run IDE for now.

## How to remap nodes in R2lab

When a node is broken, you want to replace it with another spare node.
This requires root access on faraday and bemol, and can be achived like this:

* Of course perform the physical replacement
* Then to apply changes, do the following on your laptop (this is where you need to have rights to run `ssh root@faraday` and `ssh root@bemol`)

```
cd r2lab/inventory
git pull
emacs r2lab.map
# just for extra safety
make clean 
make remap
# do not forget to commit the change into the repo, e.g.
git add r2lab.map
git commit -m "replaced node such-and-such with such-and-such"
git push
```

The syntax in `r2lab.map` should be self-explanatory, but in case it's not:

 * make sure you **only** change the 'room-slot' column for both nodes
 * and that of course you mention one room slot only once
 * the nodes not in the room should be marked as `preplab`

**NOTE**

You can safely ignore messages like

```
r2lab.map:4 - undeployed physical node 4 - ignored
```
### Example

So for example right now I have this

#
```
$ grep "04\t" r2lab.map
04	00:03:1d:0e:75:a9	preplab		20:c9:d0:36:5a:b3	7c:c3:a1:a8:0b:56
42	00:03:1d:0e:03:5b	04		7c:c3:a1:a8:26:9e	7c:c3:a1:a8:1c:2a
```

Which means that node physically numbered 42 is actually deployed on slot 4 in the room, while node physically numbered 4 is in the preplab.

### Some Details

At this point **almost** everything will work as expected, except this:

On faraday the list of all nodes is **always** `1-37`; this is by design, so that users don't need to know about possible replacements. So for example with node 42 deployed in slot 4 like above, we will have

#### In the room 

* the DHCP will offer IPs `192.138.3.4` (and same on .2) to node 42 for its `control` and `data` interfaces
* the `reboot` interface on node 42, however, still has the hard-wired `192.138.1.42` IP address. The rhubarbe tools will know about that and just do the right thing (as opposed to using curl directly, of course)

#### In the preplab

* in L102B, things are different, the only labelling that we will have is `04` written on the node, so we can talk to that node using `192.138.x.4` on all 3 subnets
* which means that in the user's point of view, the set of all nodes from bemol should be `4,38-41` and not `38-42` 

#### Epilogue

So to summarize, after `make remap` everything works fine in the faraday landscape. However for bemol, there is a need to tweak the list of all nodes, so that `rhubarbe -a` does the right thing.

`make remap` does the right thing (i.e. it changes )

For now, this is done on bemol in `/etc/rhubarbe/rhubarbe.conf`; and because the pip-install of rhubarbe is a little basic, it is best to reflect the change right into the `rhubarbe` git repo, so that a subsequent `pip install --upgrade` won't override the change.

It's no big deal if this is not done properly though, because the impact is so low.

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

# stupidest mistake so far

One day I ran a harmless rhubarbe command in `/etc/dnsmasq.d`. This had the result of creating a file named `/etc/dnsmasq.d/rhubarbe.log`. 

Next time dnsmasq tried to run, it complained about a syntax error in this file, refused to start; no DNS, ouch .. 

Took me 1 hour to figure that out. 