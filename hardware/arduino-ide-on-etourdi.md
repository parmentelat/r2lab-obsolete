# setup on etourdi

`etourdi` is the box where Julien had installed the `arduino` IDE in the first place.

Here's what you need to know about that if you need to burn firmwares in our CMC's

## Historical note

### Before

Up to Feb. 8th 2016
* everything was rooted here
 
    `/home/etourdi/Documents/Arduino/`

* at the time we used a single software, in

    `NITOS_CM_Card_Firmware_v2_1b_for_shield_v1_2_watchdog_no_XML`

* and inside this directory, a single file named

    `NITOS_CM_Card_Firmware_v2_1b_for_shield_v1_2_watchdog_no_XML.ino`

### Now

When you use the arduino IDE, the default location when opening files is
```
/usr/share/arduino`
```

So I have reorganized the whole thing so that
* the location is easier to find
* and one cannot get confused between several versions whose names begin the same (the arduino software is very rough in this respect)
* **WARNING** when making new software available, remember that **the whole area is to be owned by `etourdi:etourdi`**

So, here's what we have now

```
# pwd
/usr/share/arduino/nitos

# ls -ld
drwxr-xr-x 5 etourdi etourdi 4096 Feb  8 16:15 .

# find . -type f
./standalone_v2_1_shield_1_2/standalone_v2_1_shield_1_2.ino
./withusrp_v_3_1_shield_1_2/withusrp_v_3_1_shield_1_2.ino
./withusrp_v_3_1_shield_2_1/withusrp_v_3_1_shield_2_1.ino
./backup.tgz
```

# HowTO

* login on etourdi as user etourdi
* `Alt-F2` -> type `arduino`, click on the single app. that matches; this should run the Arduino IDE
* Click the icon that looks like a *Up arrow* (upper area, 4-th from the left), then Select 'Open...'
* double click on the 'nitos' subdir that you should see right away
* navigate to the location of interest; **Warning** you need to select the **.ino** file, not just the directory
---
* disconnect the USB cable from etourdi - if applicable
* disconnect the node from any power supply
* physically open the box
* optionnally take a picture of how the CMC card is connected
* take out the 2 wires that get into the CMC card from the mother board (**remember the polarity**)
  * If you haven't : out of the 6 connectors in the CMC, these 2 wires use the first and third ones, starting from the bottom (so before you remove anything, you can see three bare connectors)
  * the one bottom-most is connected to the location closest to the front panel
* plug the 6-connectors red pin (with its USB cable attached) into the now-free 6-pin connector on the CMC; watch for the right direction (see NITOS's pictures)

---
* in the arduino app, search section ** SERVER VARIABLES **
  * this should read, for exemple with node 27:

```
byte mac [] = {
   0x02, 0x00, 0x00, 0x00, 0x00, 0x27 };
byte ip[] = {
                      192, 168, 1, 27 };
```
* still in the app, click the `Verify` button (it shows a check sign, it's the first from the left in the upper area); it should say `Done compiling`)
* at that point connect the other end of the USB cable in etourdi
* if everything runs fine, the arduino application should say something like `Arduino ethernet on /dev/ttyUSB0 in the lower area
* Click the Upload button (2nd from the left); after a few seconds it show show: `Done uploading`
* remove the USB cable
* replace the 2 wires
* screw the box lid over again
* plug the node in; you're good to go
* optionnally check it with
```
root@bemol ~ # info 38 | grep firmware
reboot38:firmware version: 3.1 INRIA, FRANCE
``` 