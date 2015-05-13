# imagezip

Program invoked when saving an image

    /usr/bin/imagezip -o -z1 /dev/sda - | nc 192.168.3.200 7001

problem seems to be with `/dev/sda` which is not present when booting off the pxe image

# current setup is

## fit41 
* has AHCI enabled
* has fedora21 installed manually (while AHCI enabled)
* and ready to be omf6-save'd

## fit42
* has a fedora21 installed (while on IDE btw)
* then AHCI was turned on
* one can there see a working fedora with an AHCI disk (which it turns out is named /dev/sda as well)

## PXE image

currently runs this kernel :

    fit41 (pxe) # uname -a
    Linux fit41 3.13.0-37-generic #64-Ubuntu SMP Mon Sep 22 21:28:38 UTC 2014 x86_64 GNU/Linux