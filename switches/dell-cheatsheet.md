# hostnames

From faraday's `/etc/hosts` through `ssh` (usual credentials)

* `ssh switch-data`  (62xx)
* `ssh switch-control` (55xx)
* `ssh switch-reboot` (55xx)
* `ssh switch-c007` (????)

# virtual terminal

As of Oct. 2016, I used the following setup

* host wlab49 - aka arduino under ubuntu
* together with the COM to USB adapter (in the chamber)
* `apt-get install -y minicom`
* need to turn off hardware flow-control (was hard to spot)
* run `minicom -s`, select `/dev/ttyUSB0` and speed `9600 8N1` as detailed below, saved as standard config
* it does not matter which USB port is used (see `dmesg -w` when plugging the adapter to make sure)
* all this is OK on wlab49 as of Oct. 28 2016, it's easy to redo on a fresh ubuntu install
* run `minicom`, you should be good


# Stacking & general

* look at the current config

#
    show running-config

* Baudrates
<table>
<tr><th>Type</th><th>Where</th><th>speed</th></tr>
<tr><td>Linksys SRW0248</td><td>bemol</td><td>38400 8N1</td></tr>
<tr><td>PowerConnect 62xx</td><td>faraday - data</td><td> 9600 8N1 </td></tr>
<tr><td>PowerConnect 55xx</td><td>faraday - others</td><td> 9600 8N1 </td></tr>
</table>

  * can be changed (on both types) using
 e.g. `speed 38400` but we don't want to do that


* Stacking
  * It feels like the 2 models we have cannot be stacked together in any case
  * We could still stack the 2 55xx boxes but what sense would that make ?
* Paging
  * the 55xx can use `terminal datadump` to turn off paging (i.e. displaying a `-more-` prompt); 
  * could not find the same on 62.xx

* ssh
  * all 4 switches run an ssh server; enter with user `root` and usual password
  * preparation for SSH	 server: not appearing in either config are the following 2 commands that I ran once to create keypairs attached to host identification of the switch itself. ssh server won't start - even after `ip ssh server` if any of both keys is missing


###
    crypto key generate rsa
    crypto key generate dsa
    
# Workflow
* All 4 config files are managed under git in the `switches/` subdir
* running `make push-dell` pushes this onto the tftp server on faraday
* then use one of these commands to fetch that config from the switch

###
    copy tftp://192.168.4.100/switch-data.conf startup-config
    copy tftp://192.168.4.100/switch-control.conf startup-config
    copy tftp://192.168.4.100/switch-reboot.conf startup-config
    copy tftp://192.168.4.100/switch-c007.conf startup-config
    
* and then 

###
    reload

# Data Switch - 6248

## config management

* For resetting to factory defaults, I found only one method for now, which is to reboot the box, and from the console you first hit a menu that lets you restore the factory defaults

* it could be that deleting the startup-config would do the trick as well but I have not tried that at this point.

* in order to save the running config for next reboot:
  * `copy running-config startup-config` (62xx)
  * `write memory`  (55xx)


## Addressing

* interfaces get addressed by strings like

```
interface ethernet 1/g44
```    

* or by range

```
interface range ethernet 1/g1-1/g37
```

* example, inspecting

```
switch-data#show interfaces status ethernet 1/g4
Port   Type                            Duplex  Speed    Neg  Link  Flow Control
                                                             State Status
-----  ------------------------------  ------  -------  ---- --------- ------------
1/g4   Gigabit - Level                 Full    1000     Auto Up        Active
    
Flow Control:Enabled
```

## Mirroring/monitoring   

```
monitor session 1 source interface 1/g<x>
monitor session 1 destination interface 1/g<z>
```
At that point the session is not active; you can check this with (`exit` config mode of course)

```
show monitor session 1
```    

Turn on

```
monitor session 1 mode
```    

Turn off

```
no monitor session 1 mode
```

## IGMP

```
ip igmp snooping
show bridge multicast address-table
```    

# Reboot and Control switches - 5548

## config management

* reset to factory defaults (do not save when prompted)

```
delete startup-config
reload
```

* save current config

```
write memory
```

## Addressing

* interfaces get addressed by strings like

```
interface gigabitethernet 1/0/4
```
    
* c007 : `te1/0/1` (to faraday) and `te1/0/2` (to switch-data)
* data : `1/xg3` (to swtich-data) 
* reboot : 
* control
    
* example, inspecting

```
switch-reboot# show interfaces status gigabitethernet 1/0/4
                                             Flow Link          Back   Mdix
Port     Type         Duplex  Speed Neg      ctrl State       Pressure Mode
-------- ------------ ------  ----- -------- ---- ----------- -------- -------
gi1/0/4  1G-Copper    Full    100   Enabled  On   Up          Disabled Off
```

## Mirroring/monitoring   

* not tried but I expect the same `monitoring` commands to work identically

## IGMP

```
ip igmp snooping
```
