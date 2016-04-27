# setup on `wlab49` a.k.a. `arduino`

* both hostnames are on the .pl.sophia.inria.fr domain
* setup based on ubuntu-16.04 desktop
* very basic install, plus `apt-get install arduino`
* user is tester with usual password, although it shows up as `R2lab arduino` or something of that kind
* otherwise the NITOS firmware is deployed in `/usr/share/arduino/nitos/` exactly like it was on etourdi
* except that of course it has been chwon'ed to `tester:tester` instead.
* also there is a backup of that area in `bemol:/root` that was actually used to perform migration
* ssh access from `root@bemol` is granted, mostly for propagating any new firmware versions

##### Tests
* had to remove the inclusion if `OneWire.h` that was not found and unused 
* otherwise turned out to work fine with fit39

# HowTO

* login on wlab39 as tester with usual password (or on etourdi as user etourdi)
* `Alt-F2` -> type `arduino`, click on the single app. that matches; this should run the Arduino IDE
* Click the icon that looks like a *Up arrow* (upper area, 4-th from the left), then Select 'Open...'
* double click on the 'nitos' subdir that you should see right away
* navigate to the location of interest; **Warning** you need to select the **.ino** file, not just the directory

---
* disconnect the USB cable from wlab49/etourdi - if applicable
* disconnect the node from any power supply
* physically open the box
* optionnally take a picture of how the CMC card is connected; 
* take out the 2 wires that get into the CMC card from the mother board (**remember the polarity**)
  * If you haven't : out of the 6 connectors in the CMC, these 2 wires use the **first** and **third** ones, starting from the bottom (so before you remove anything, you can see three bare connectors)
  * the one bottom-most is connected on the motherboard to the location closest to the front panel
* plug the 6-connectors red pin (with its USB cable attached) into the now-free 6-pin connector on the CMC; watch for the right direction (see NITOS's pictures); the chip should face the inside of the box, not towards the outside.

---
* in the arduino app, search section ** SERVER VARIABLES **
  * this should read, for exemple with node 27:

```
byte mac [] = {
   0x02, 0x00, 0x00, 0x00, 0x00, 0x27 };
byte ip[] = {
                      192, 168, 1, 27 };
```
* replace the 2 occurrences with your node number, on 2 digits (so e.g. `04` in both places is OK)
* still in the app, click the **Verify** button (it shows a check sign, it's the first from the left in the upper area); it should say `Done compiling`)
* at that point connect the other end of the USB cable in wlab49/etourdi
* if everything runs fine, the arduino application should say something like `Arduino ethernet on /dev/ttyUSB0 in the lower area`
* Click the **Upload** button (2nd from the left); after a few seconds it should show: `Done uploading`
* remove the USB cable
* **DO NOT FORGET:** replace the 2 wires
* reconnect power supply
* run `info` to check for the new version number (see below)
* screw the box lid over again

```
root@bemol ~ # info 38 | grep firmware
reboot38:firmware version: 3.1 INRIA, FRANCE
``` 

***
***

# setup on etourdi

`etourdi` is the box where Julien had installed the `arduino` IDE in the first place.

Here's what you need to know about that if you need to burn firmwares in our CMC's



## Historical note

### Now

When you use the arduino IDE, the default location when opening files is
```
/usr/share/arduino
```

So I have reorganized the whole thing so that

* the location is easier to find
* and one cannot get confused between several versions whose names begin the same (the arduino software is very rough in this respect)
* **WARNING** when making new software available, remember that **the whole area is to be owned by `etourdi:etourdi`**
* also the `.ino` filename ***must match*** the directory name; that's real odd, but yes...
* Latest version is **`withusrp_v_3_2_shield_1_2`**
  * version number 3.2 : the one that has `usrpon` and the like
  * shield number : all our CMC models are number 1.2 (see the `info` verb); there's also a version 2.1 that we can ignore
* **Local changes** in 3.2 are cosmetic and are about
  * INRIA France instead of INRIA FRANCE
  * the labels as printed by the 3 `usrp*` commands are now lowercase, and either `ok` for `usrpon` and `usrpoff`, and `usrpon` or `usrpoff` for `usrpstatus` (they were uppercase and uselessly verbose)
* Use the 'info' verb at the CMC to get the firmware version number. e.g. here we have the latest 3.2 uploaded on node 4

```
info root@bemol ~ # info 4
reboot04:firmware version: 3.2 INRIA, France
reboot04:hardware version: 1.2
reboot04:ip: 192.168.1.4
reboot04:mac: 02:00:00:00:00:04 
```

### Before

Until to Feb. 8th 2016

* everything was rooted here
 
    `/home/etourdi/Documents/Arduino/`

* at the time we used a single software, in

    `NITOS_CM_Card_Firmware_v2_1b_for_shield_v1_2_watchdog_no_XML`

* and inside this directory, a single file named

    `NITOS_CM_Card_Firmware_v2_1b_for_shield_v1_2_watchdog_no_XML.ino`


# Available commands

As per UTH guys; not all this is true or useful, hence the ~~barred commands~~

To control the nodes , we use the following commands :

* `curl 192.168.1.xx/on` : turns the node on(on)
* `curl 192.168.1.xx/off` :  turns the node off(off or closing)
* `curl 192.168.1.xx/reset` : resets the node(reseted)
* `curl 192.168.1.xx/info` : info from the CM
* `curl 192.168.1.xx/urspon` : turn on USRP
* `curl 192.168.1.xx/urspoff` : turn off USRP
* `curl 192.168.1.xx/urspstatus` : latest order sent to USRP (soft state)
* ~~`curl 192.168.1.xx/sensors`~~ : values from sensors
* ~~`curl 192.168.1.xx/temperature`~~ :  temperature's sensor value
* ~~`curl 192.168.1.xx/power`~~ :  power's sensor value
* ~~`curl 192.168.1.xx/light`~~ :  light's sensor value
* ~~`curl 192.168.1.xx/humidity`~~ :  humidity's sensor value


