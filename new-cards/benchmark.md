# the second wifi adapter

This document gathers a few notes on my experiments on the 3 options we have for substituting the initial Atheros card in mini-PCI slot 1

# Nodes used

1. `fit39` : with Intel 5300 in Mini-PCI slot 1
2. `fit41` : with Atheros AR9590 in Mini-PCI slot 1
3. `fit42` : with same card as before (Atheros AR5XBX112) connected in main (not mini) PCI through an adapter 

All nodes deployed in the prep-lab / bemol setup

# Preference a priori

At first glance, and unless we establish that there is a real scientific value in the diversity, our preferences are

1. fit42/same Atheros plainPCI
2. fit39/Intel miniPCI
3. fit41/other Atheros miniPCI

Because the other Atheros was reported by UTH as exhibiting some glitches similar to the ones we've had during the painful initial deployment stage, even if much more occasionnally

# Hard-drive performance test

Running a simple 2-phases tests that
* writes 150 Gb of zeroes (note that as of these tests all 3 nodes are set to run their hdd in IDE mode)
* reads them again and computes its MD5

## fit39/Intel miniPCI

    root@fit39:/var/tmp# time dd if=/dev/zero of=./zeroes bs=256M count=600
    600+0 records in
    600+0 records out
    161061273600 bytes (161 GB) copied, 388.34 s, 415 MB/s
    
    real	6m28.353s
    user	0m0.009s
    sys	2m16.511s
    
    root@fit39:/var/tmp# time md5sum zeroes

interrupted, would not return after more than 30'
at that point dmesg reports tons of errors related to `ata1`, like e.g.

    [ 3683.699948] ata1.00: status: { DRDY }
    [ 3683.700556] ata1.00: hard resetting link
    [ 3684.420109] ata1.01: hard resetting link
    [ 3685.447232] ata1.01: failed to resume link (SControl 0)
    [ 3685.603148] ata1.00: SATA link up 1.5 Gbps (SStatus 113 SControl 310)
    [ 3685.603160] ata1.01: SATA link down (SStatus 4 SControl 0)
    [ 3685.636046] ata1.00: configured for UDMA/33
    [ 3685.636051] ata1.00: device reported invalid CHS sector 0
    [ 3685.636057] ata1: EH complete
    [ 3717.667842] ata1: lost interrupt (Status 0x50)
    [ 3717.667860] ata1.00: exception Emask 0x50 SAct 0x0 SErr 0x48d0802 action 0xe frozen
    [ 3717.668548] ata1.00: SError: { RecovComm HostInt PHYRdyChg CommWake 10B8B LinkSeq DevExch }
    [ 3717.669227] ata1.00: failed command: READ DMA EXT
    [ 3717.669832] ata1.00: cmd 25/00:00:80:b3:a0/00:02:02:00:00/e0 tag 0 dma 262144 in
    [ 3717.669832]          res 40/00:01:00:00:00/00:00:00:00:00/e0 Emask 0x54 (ATA bus error)    
    
    
## fit41/other Atheros miniPCI

    root@fit41:/var/tmp# time dd if=/dev/zero of=./zeroes bs=256M count=600
    600+0 records in
    600+0 records out
    161061273600 bytes (161 GB) copied, 592.351 s, 272 MB/s

    real	9m52.359s
    user	0m0.000s
    sys	2m17.132s
    
    root@fit41:/var/tmp# time md5sum zeroes
    
interrupted, would not return after more than 30'
at that point dmesg reports tons of errors related to `ata1`, like e.g.

    [ 3577.793932] ata1.00: status: { DRDY }
    [ 3577.794542] ata1.00: hard resetting link
    [ 3578.514069] ata1.01: hard resetting link
    [ 3579.541200] ata1.01: failed to resume link (SControl 0)
    [ 3579.697114] ata1.00: SATA link up 1.5 Gbps (SStatus 113 SControl 310)
    [ 3579.697124] ata1.01: SATA link down (SStatus 4 SControl 0)
    [ 3579.753979] ata1.00: configured for UDMA/33
    [ 3579.753984] ata1.00: device reported invalid CHS sector 0
    [ 3579.753990] ata1: EH complete
    [ 3711.668899] ata1: lost interrupt (Status 0x50)
    [ 3711.668919] ata1.00: exception Emask 0x50 SAct 0x0 SErr 0x58d0802 action 0xe frozen
    [ 3711.669608] ata1.00: SError: { RecovComm HostInt PHYRdyChg CommWake 10B8B LinkSeq TrStaTrns DevExch }
    [ 3711.670283] ata1.00: failed command: READ DMA EXT
    [ 3711.670893] ata1.00: cmd 25/00:00:80:87:50/00:02:12:00:00/e0 tag 0 dma 262144 in
    [ 3711.670893]          res 40/00:01:00:00:00/00:00:00:00:00/e0 Emask 0x54 (ATA bus error)

## fit42/same Atheros plainPCI

    root@fit42:/var/tmp# time dd if=/dev/zero of=./zeroes bs=256M count=600
    600+0 records in
    600+0 records out
    161061273600 bytes (161 GB) copied, 356.088 s, 452 MB/s
    
    real	5m56.098s
    user	0m0.000s
    sys	2m14.835s

    root@fit42:/var/tmp# time md5sum zeroes
    f353f9cff0c9f4f24835cb74f9fc0ec7  zeroes
    
    real	6m39.906s
    user	4m22.712s
    sys	0m31.046s    
    
## hard-drive Conclusion
 
As far as disk performance is concerned, our preferred option is confirmed to be fit42/same Atheros

# Wifi tests

## Notes on the wifi drivers

The baseline image available on bemol as of the tests was

    root@bemol:~# ls -l /var/lib/omf-images-6/baseline.ndz
    -rw-r--r-- 1 root root 537919488 Feb  5 12:51 /var/lib/omf-images-6/baseline.ndz
    root@bemol:~# md5sum /var/lib/omf-images-6/baseline.ndz
    c65f5631c79d34be8c7bc595c6baa003  /var/lib/omf-images-6/baseline.ndz
    
This image comes with the 2 Atheros drivers blacklisted - but not the Intel driver. 

In order to make my personal arrangements permament I did the following on all three nodes

    # sed -i -e 's,blacklist ath9k,#blacklist ath9k,' /etc/modprobe.d/blacklist-compat.conf

which I advise we should do in our official reference image

With this in place I can see 2 wireless interfaces on each node

## which is which

In all three nodes it looks like

* the 'constant' Atheros interface, the one we have in miniPCI slot 2, is known as `wlan0`
* the 'new' wifi interface, the one that differs from one node to the other, is knowns as `wlan1`, as we can see below

###
    root@fit39:/var/tmp# lspci | grep Wi
    03:00.0 Network controller: Qualcomm Atheros AR93xx Wireless Network Adapter (rev 01)
    04:00.0 Network controller: Intel Corporation Ultimate N WiFi Link 5300
    root@fit39:/var/tmp# ls -l /sys/class/net/wlan*
    lrwxrwxrwx 1 root root 0 Mar 10 23:19 /sys/class/net/wlan0 -> ../../devices/pci0000:00/0000:00:1c.5/0000:03:00.0/net/wlan0
    lrwxrwxrwx 1 root root 0 Mar 10 23:19 /sys/class/net/wlan1 -> ../../devices/pci0000:00/0000:00:1c.6/0000:04:00.0/net/wlan1
    
    root@fit41:/var/tmp# lspci | grep Wi
    03:00.0 Network controller: Qualcomm Atheros AR93xx Wireless Network Adapter (rev 01)
    04:00.0 Network controller: Qualcomm Atheros AR9580 Wireless Network Adapter (rev 01)
    root@fit41:/var/tmp# ls -l /sys/class/net/wlan*
    lrwxrwxrwx 1 root root 0 Mar 11 15:13 /sys/class/net/wlan0 -> ../../devices/pci0000:00/0000:00:1c.5/0000:03:00.0/net/wlan0
    lrwxrwxrwx 1 root root 0 Mar 11 15:13 /sys/class/net/wlan1 -> ../../devices/pci0000:00/0000:00:1c.6/0000:04:00.0/net/wlan1
    
    root@fit42:/var/tmp# lspci | grep Wi
    01:00.0 Network controller: Qualcomm Atheros AR93xx Wireless Network Adapter (rev 01)
    04:00.0 Network controller: Qualcomm Atheros AR93xx Wireless Network Adapter (rev 01)
    root@fit42:/var/tmp# ls -l /sys/class/net/wlan*
    lrwxrwxrwx 1 root root 0 Mar 11 15:15 /sys/class/net/wlan0 -> ../../devices/pci0000:00/0000:00:01.0/0000:01:00.0/net/wlan0
    lrwxrwxrwx 1 root root 0 Mar 11 15:15 /sys/class/net/wlan1 -> ../../devices/pci0000:00/0000:00:1c.5/0000:04:00.0/net/wlan1

## setup

We create 2 ad-hoc networks, one for all the `wlan0` interfaces, using essid `wlan0`, and same for `wlan1`

### wifi
Each node has
* both its interfaces up
* configured in ad-hoc mode on ssid 'wlan0' or 'wlan1' 
* uses txpower 3dBm

that is to say

    root@fit39:/var/tmp# iwconfig wlan0; iwconfig wlan1
    wlan0     IEEE 802.11abgn  ESSID:"wlan0"
              Mode:Ad-Hoc  Frequency:2.412 GHz  Cell: 0A:8F:66:EA:50:D7
              Tx-Power=3 dBm
              Retry  long limit:7   RTS thr:off   Fragment thr:off
              Encryption key:off
              Power Management:off
    
    wlan1     IEEE 802.11abgn  ESSID:"wlan1"
              Mode:Ad-Hoc  Frequency:2.462 GHz  Cell: C2:CF:4D:A1:DB:DB
              Tx-Power=3 dBm
              Retry  long limit:7   RTS thr:off   Fragment thr:off
              Encryption key:off
              Power Management:off
              
### IP
    root@fit39:/var/tmp# for if in wlan0 wlan1; do ip address show $if | egrep 'wlan|inet ' ; done
    4: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
        inet 172.16.0.39/24 scope global wlan0
    5: wlan1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
        inet 172.16.1.39/24 scope global wlan1              

### services

* we run a total of 6 netcat services, one per wifi interfaces, all on port 1000

## tests in each data plane

* each of the 3 nodes sends a 256kb file over to one neighbour in a round-robin fashion
* we measure something around 3s for that transfer, no matter which plane nor direction

#
    root@fit39:/var/tmp# for net in 0 1; do for dest in $j $k; do  echo ========== sending from $i to $dest; date; cat 256kb | netcat     172.16.$net.$dest 1000 ; date; done; done
    ========== sending from 39 to 41
    Wed Mar 11 02:58:04 EET 2015
    Wed Mar 11 02:58:07 EET 2015
    ========== sending from 39 to 42
    Wed Mar 11 02:58:07 EET 2015
    Wed Mar 11 02:58:10 EET 2015
    ========== sending from 39 to 41
    Wed Mar 11 02:58:10 EET 2015
    Wed Mar 11 02:58:13 EET 2015
    ========== sending from 39 to 42
    Wed Mar 11 02:58:13 EET 2015
    Wed Mar 11 02:58:16 EET 2015
    
    root@fit41:/var/tmp# for net in 0 1; do for dest in $j $k; do  echo ========== sending from $i to $dest; date; cat 256kb | netcat     172.16.$net.$dest 1000 ; date; done; done
    ========== sending from 41 to 42
    Wed Mar 11 18:52:28 EET 2015
    Wed Mar 11 18:52:31 EET 2015
    ========== sending from 41 to 39
    Wed Mar 11 18:52:31 EET 2015
    Wed Mar 11 18:52:34 EET 2015
    ========== sending from 41 to 42
    Wed Mar 11 18:52:34 EET 2015
    Wed Mar 11 18:52:37 EET 2015
    ========== sending from 41 to 39
    Wed Mar 11 18:52:37 EET 2015
    Wed Mar 11 18:52:40 EET 2015
    
    root@fit42:/var/tmp# for net in 0 1; do for dest in $j $k; do  echo ========== sending from $i to $dest; date; cat 256kb | netcat     172.16.$net.$dest 1000 ; date; done; done
    ========== sending from 42 to 39
    Wed Mar 11 18:55:00 EET 2015
    Wed Mar 11 18:55:03 EET 2015
    ========== sending from 42 to 41
    Wed Mar 11 18:55:03 EET 2015
    Wed Mar 11 18:55:06 EET 2015
    ========== sending from 42 to 39
    Wed Mar 11 18:55:06 EET 2015
    Wed Mar 11 18:55:09 EET 2015
    ========== sending from 42 to 41
    Wed Mar 11 18:55:09 EET 2015
    Wed Mar 11 18:55:12 EET 2015