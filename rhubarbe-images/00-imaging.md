* Entries listed latest first
* OAI-related details in a separate file `01-oai.md`
* List of known issues in `02-fixes.md`

# building 4.7 on Ubuntu-14.04

* first attempt to run [4.7.0/lowlatency kernel inside ubuntu-**16.04**](http://ubuntuhandbook.org/index.php/2016/07/install-linux-kernel-4-7-ubuntu-16-04/) ran without a glitch by just installing pre-packaged stuff
* but on **14.04** though the same recipe did dot work out

It took me a while to spot the issue:

* symptom was node not booting on that new kernel
* had to do with `/sys/kernel/uevent_helper`
* [this message is a good starting point](http://askubuntu.com/questions/809843/is-ubuntu-14-04-available-to-use-4-7-kernel-or-above)
* [kernel is ill-configured](http://tuxthink.blogspot.fr/2014/10/can-not-create-syskernelueventhelper.html)
* I gave a try at 4.7.2 as published on kernel.ubuntu.com, to no avail either

So evntually I just went for the yekkety / 16.10 vanilla kernel debs, which gave me a nice 4.8.0 with lowlatency that runs fine with both ubuntu-14 and ubuntu-16

# update - Oct. 2016

* in `infra/builds/`
* there is a script `build-image.py`
* that allows to build an image in an unattended manner
* and `all-images.sh` take advantage of that to list all the recipes that we use - some of them on a nightly basis eventually
* this also uses code actually in `infra/user/imaging.sh` 

# generic ubuntu stuff

## workflow

* downlaod the ISO for 64 bits `server` (as opposed to desktop which is much bigger)
* run `USB startup creator` (approx name) on a ubuntu (e.g. arduino) to create a bootable stick
* select a node that has the usual disk layout with 2 partitions on `ext4` (upload e.g. fedora21 or similar)
* boot off the USB stick ; while running the installer :
  * add openssh server
  * beware about **Using the current partition scheme** which can be missed completely - especially with 14.04, looks better with more recent installers
  * hostname `r2lab`; user `rl2ab`; password `r2lab` (will be cleaned up later on)
* log in as r2lab/r2lab


## `imaging-utils.sh`

`rhubarbe-images/imaging-utils.sh` is a script designed to **help** automate the various stages. 

**IMPORTANT NOTES**
* this script **only is a help** - make sure to read it before running it
* also bear in mind it will likely be subject to changes and evolutions

```
curl -O https://raw.githubusercontent.com/parmentelat/r2lab/master/rhubarbe-images/imaging-utils.sh
chmod +x imaging-utils.sh
# And then
./imaging-utils.sh help
```

# 2016/09/26 - fedora-24

* done on fit42 
* created a USB stick by just running 

```
dd if=/Users/parmentelat/Downloads/os-images/Fedora-Server-netinst-x86_64-24-1.2.iso of=/dev/rdisk2 bs=1m
```

* ~~**not working in text mode** in text mode; graphic mode looked unusable; however I could not use my partitioning in text mode~~
* eventually could use ***Install in basic graphics mode***, which is in the **Toubleshooting** submenu when running the fedora installer
* **Partitioning**
  * could not actually preserve the partitionin that I had `rhubarbe-load`-ed from `ubuntu-16`
  * redid something similar
  * make sure to select **ext4** as it defaults to **xfs**
* selected *Minimal install*
* defined usual root password
* --- rebooted
* `fdisk -l` - for checking partitions
* `dnf -y udpate` - not needed as I was using a net install, but it does help to update the internal db or cache of dnf
* `mkdir ~/.ssh ; chmod 700 ~/.ssh`
* open up root ssh access for `root@bemol`'s public key 
  * `# root@bemol scp ~/.ssh/id_rsa.pub root@fit42:.ssh/authorized_keys`
* **snapshot here** with `# rsave 42 -o fedora-24-v0-bemol-only`

## this needs more work:

* the following does not work at all and I can't figure out why
  * can't log into the node at all through ssh afterwards - it prompts for a passwd, that should be empty
  * have also tried to turn off selinux to no avail

``` 
./build.py $(plr faraday) fit01 fedora-24-v0-bemol-only fedora-24-v1-test clear-password.sh
```

* also, i have noticed that the following flaws with this image; they make everything slow and tedious:
  * ssh takes a long time (in the 1-2 minutes) before it accepts incomping connections
  * and more marginally, grub would need tweaking, we'd lose a good 5s stupidly waiting for grub input at boot-time

# 2016/04/25 - `ubuntu-14.04`

* done on fit38 (had to disconnect the USRP usb first)
* first time where `imaging-utils.sh` was actually used, although I improved it a lot afterwards, so please use with care


# 2016/04/22 - `ubuntu-16.04`

* done on fit41 (and actually I should not have because the damn thing has is super slow when downloading pxefrisbee and I have no idea why)
* created a USB stick from the `server` iso using USB Stick Creator on ubuntu
* started with uploading a previous ubuntu image to be sure about the partitioning and `ext4` business 
* otherwise the procedure was in line with what `imaging-utils.sh` has, except done mostly manually

# 2015/12/09: `ubuntu-12.04.5`

* for Naoufal's experiment; an old image is required
* done from scratch on `fit41`
* with the usual `ext4` layout
* standard install entirely; just added the OpenSsh service during
  installation; this also forced me to add me a `r2lab` account
* logged in from terminal (using r2lab account), did `sudo su -` to
set a passwd for root
* at that point I could enter through ssh from bemol

#
    apt-get update
    apt-get install -y emacs23-nox

* too bad, something is wrong here

#
    W: Failed to fetch bzip2:/var/lib/apt/lists/partial/us.archive.ubuntu.com_ubuntu_dists_precise_main_source_Sources  Hash Sum mismatch

* fixed the problem [as per this page](http://askubuntu.com/questions/41605/trouble-downloading-packages-list-due-to-a-hash-sum-mismatch-error)

#
    rm -rf /var/lib/apt/lists/*
    apt-get update

* could then install additional packages

#
	apt-get install -y emacs23-nox
    apt-get install -y rsync make git gcc
	apt-get install -y iw ethtool tcpdump wireshark bridge-utils
	
* edited `/etc/ssh/sshd_config` so that

#
    root@r2lab:/etc/ssh# grep -v '^#' /etc/ssh/sshd_config | egrep -i 'Root|Password|PAM'
    PermitRootLogin yes
    PermitEmptyPasswords yes
    PasswordAuthentication yes
    UsePAM no

* cleared passwd and extra user

#
    passwd --delete root
    userdel --remove r2lab

* hostname
  * found an occurrence of fit41in /etc/hosts for 127.0.0.1 - using `fit-image` instead
  * plus the usual:

#
    rm -f /etc/hostname

* netnames (control and data)- like for other ubuntus, see `rhubarbe-images/netnames-scratchpad.sh`



# 2015/11/09 : `fedora-23`

**Important note:** [do not use `fedup` that is deprecated; see this page instead](https://fedoraproject.org/wiki/DNF_system_upgrade)

* based on fit41
* re-loaded latest fedora22 image at that time
* ran `dnf update --refresh` 
* created a snapshot of that image using `omf6 save`. This should now become the reference image for fedora22 (named `fedora-22-updated-2015-11-09.ndz`)
* rebooted off that image again
* `dnf system-upgrade download --releasever=23`
* `dnf system-upgrade reboot`
* after some time the node comes back up; captured again as `fedora-23-system-upgrade.ndz` and of course related symlink

# 2015/11/09 : `ubuntu-15.10`

* based on fit42
* likewise, started with a global update & snapshot
* `apt-get update; apt-get upgrade`  
* created a snapshot `ubuntu-15.04-updated-2015-11-09.ndz` that here again should become the reference for ubuntu-15.04

* [Used instructions from this page](https://wiki.ubuntu.com/WilyWerewolf/ReleaseNotes#Upgrading_from_Ubuntu_15.04)
* which essentially amounted to `do-release-upgrade`

# 2015/10/13 `fedora-22`
* and about time...
* `fedora22` raw image done using `fedup` from the corresponding fedora21 image. **NOTE: this method is now deprecated**

#
    yum -y update
    yum -y install fedup
    shutdown -r now

* This results in a significantly larger image than the raw `f21` image;
* For `f23` I will probably redo an install from scratch
* PS: actually this was not done and it's maybe a pity; maybe f24 ?

# 2015/05/21 `ubuntu-15.04`

* remade on fit39 on may 21 2015
* first attempt essentially to check the new imagezip can handle ext4 partitions
* actually re-used partition scheme from fedora21 (24Gb swap, only 2 partitions so that new imagezip can run smoothly) 
* partition / with ext4
* mandatory user : ubuntu/ubuntu (should be deleted later)
* selected openssh server
* had no grub-related issue when rebooting (great !)
* use sudo su to enter root account

## `rough`

at this point, made a blank omf6 save and load on 40 -> everything is fine
`ubuntu15.04-ext4-v00-rough.ndz` 

* enable empty passwords in sshd_config

#
    root@fit41:/etc/ssh# grep -v '^#' /etc/ssh/sshd_config | egrep -i 'Root|Password|PAM'
    PermitRootLogin yes
    PermitEmptyPasswords yes
    PasswordAuthentication yes
    UsePAM no

* users

# 
    passwd --delete root
    userdel --remove ubuntu

* additional packages

# 
    apt-get install -y iw ethtool
    apt-get install -y rsync make git
    apt-get install emacs24-nox
    apt-get -y install gcc make tcpdump wireshark bridge-utils

* hostname
  * found an occurrence of fit39 in /etc/hosts for 127.0.0.1 - using fit-image instead

## `root+base` 

All looks fine; except for device names, as I found the MAC addresses from the initial node hardware where saved in `/etc/udev/rules.d/70-persistent-net.rules`; so unsurprisingly

* I had on `fit39` `p2p1`, `eth1`, `wlan0` and `wlan1`,
* while on `fit40` this was `p2p1`, `eth0`, `wlan2` and `wlan3`

See `r2lab/omf-images-6/netnames-scratchpad.sh` on how to deal with this, and have nice and clean names in `control` and `data`

## `netnames` 

had an attempt at an image that would have DHCP turned on for the data interface but that is a bad idea; root prompt gets all mashed up, too much overhead, trashed..

##  PS - June 22 2014 - v03-dataif
I am tweaking /etc/network/interfaces and /etc/network/interfaces.d/data so that the data interface can be turned on using a simple ‘ifup data’

## Possible improvements

* `apt-get python-pip python3-pip`
    
* see also Michelle’s proposal to fix hostname issue when enabling data interface; -- or -- fix this on the server side

# 2015/05/21 `fedora-21`

* done on fit38 on may 21 2015
* same partitioning as usual with ext4

```
#
Number  Start   End    Size    Type     File system     Flags
     1      1049kB  215GB  215GB   primary  ext4            boot
     2      215GB   240GB  25.3GB  primary  linux-swap(v1)
```

* added emacs-nox, cleared root password and enabled ssh access

## `rough`
* cleared hostname
* commented HWADDR from /etc/sysconfig/network-scripts/ifcfg-en*
* created udev rules (see `omf-images-6/netnames-scratchpad.sh`); here we need 2 sets of rules so the wireless device names match the ones in `wlan[01]`, which ubuntu has out of the box
* cleaned up `/etc/sysconfig/n*s` so that the new names `control` and `data` are relevant to network manager as well (`nmcli`); this in a nutshell comes down to 
  * renaming the ifcfg-* files
  * changing the definition of NAME in there
  * and adding a DEVICE= 
    so e.g.

#
    [root@fit38 ~]# cat /etc/sysconfig/network-scripts/ifcfg-control
    TYPE="Ethernet"
    BOOTPROTO="dhcp"
    DEFROUTE="yes"
    IPV4_FAILURE_FATAL="no"
    IPV6INIT="yes"
    IPV6_AUTOCONF="yes"
    IPV6_DEFROUTE="yes"
    IPV6_FAILURE_FATAL="no"
    NAME="control"
    DEVICE="control"
    UUID="c35aebc6-df07-4c59-a4b6-531f7a442e75"
    ONBOOT="yes"
    #HWADDR="00:03:1D:0E:24:79"
    PEERDNS="yes"
    PEERROUTES="yes"
    IPV6_PEERDNS="yes"
    IPV6_PEERROUTES="yes"
  * made an attempt at creating an ifcfg file for wlan0 so that this would show up in nmcli as well, but it did not work right away so I am giving up
* yum installed wireless-tools in the mix

## netnames
 * yum installed `wireless-tools ethtool rsync make git gcc tcpdump wireshark bridge-utils bind-utils`


# 2014/06/17 `ubuntu-14.10`

* redone on fit40
* so that we can rebuild latest gnuradio essentially
* used USB drive; expect error message; enter ‘Tab’ and then ‘expert’ 
* thanks to expert install, no nonsense *normal* user, just `root`
* based on ext4 + 2 simple partitions
* software selection
  * *universe + multiverse + backported*
  * disabled security updates (will handle that manually)
* install openSSH server
* some nuisance with GRUB and MBR; had to reboot in rescue mode (still with ubuntu pendrive) so that I could 
  * run `passwd --delete root`
  * enable empty passwords in `sshd_config`

# 
    root@fit41:/etc/ssh# grep -v '^#' /etc/ssh/sshd_config | egrep -i 'Root|Password|PAM'
    PermitRootLogin yes
    PermitEmptyPasswords yes
    PasswordAuthentication yes
    UsePAM no

* see also how `15.10` was done
  *  removed `hostname` in `/etc` and `/etc/hosts`
  *  installed additional packages

## PS: June 22 2014 - `v03-dataif`
* I am tweaking `/etc/network/interfaces` and `/etc/network/interfaces.d/data` so that the data interface can be turned on using a simple `ifup data`

# gnuradio, and older stuff

* [There is a separate google doc on how to create a gnu radio image.](https://docs.google.com/document/d/16Yg20OlwtKEnfGxDc3YEiHBk9DPDamrffAJzyqfmG6w/edit)

* [The present notes were initially stored in a google doc here](https://docs.google.com/document/d/10CEVjOk7v59v1w_6iZq-lr7x3-SlPyhkTI91TgeP39o/edit#). Most old entries could be forgotten so I have not migrated them over here for markdown.
