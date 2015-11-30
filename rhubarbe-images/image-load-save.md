# setting stuff up

See pxe-image.md (this dorectory) for how to deal/install the various initramfs images

in short:

    nodes 39
    nextboot_pxe 39
    nextboot_listall
    reset 39
    <wait for some time>
    telnet fit39

As of **Nov. 2015** (and for quite some time already) the binaries for `frisbee`, `imagezip`, (on the pxefrisbee image) and `frisbeed` (on both bemol and faraday) are **the new ones**.

# load
## server
    frisbeed -i 192.168.3.200 -m 234.5.6.7 -p 10000 -W 90000000 /var/lib/omf-images-6/fedora21.ndz
## client
    ip=$(ifconfig | grep 192.168.3 | sed -e 's,:, ,' | awk '{print $3;}')
    frisbee -i $ip -m 234.5.6.7 -p 10000 /dev/sda

# save

## server 
    /bin/nc -d -l 192.168.3.200 9000 > /var/lib/omf-images-6/new_image.ndz
## client
    imagezip -o -z1 /dev/sda - | nc -n 192.168.3.200 9000


# Comparing the outputs from both versions

## old imagezip (from old pxe image)

### ubuntu - old std pxe image

**Note** Interestingly one cannot use `/usr/bin/imagezip -o -z1 /dev/sda /dev/null`

    ~ # /usr/bin/imagezip -o -z1 /dev/sda - | cat > /dev/null
      Slice 6 is unused, NOT SAVING.
      Slice 7 is unused, NOT SAVING.
      Slice 8 is unused, NOT SAVING.
      Slice 3 is unused, NOT SAVING.
      Slice 4 is unused, NOT SAVING.
    .............................................................    965164544    3
    .............................................................   2303785472    6
    .............................................................   4308552704    9
    .............................................................   5660389888   11
    .............................................................  65952636416   17
    ............................................................. 147379175936   24
    .............................................
    231582236672 input (4871983104 compressed) bytes in 31.269 seconds
    Image size: 432013312 bytes
    148.591MB/second compressed

### fedora - old std pxe image

    ~ # /usr/bin/imagezip -o -z1 /dev/sda - | cat > /dev/null
      Slice 3 is unused, NOT SAVING.
      Slice 4 is unused, NOT SAVING.
    .............................................................    395488768    2
    .............................................................    781942784    5
    .............................................................   1900670976    8
    .............................................................   2709018624   10
    .............................................................   3103745536   12
    .............................................................   3522172928   15
    .............................................................  49675804672   20
    .............................................................  50339937792   23
    .............................................................  50910098944   25
    .....................................
    214287024128 input (4844244992 compressed) bytes in 35.377 seconds
    Image size: 615514112 bytes
    130.589MB/second compressed

## new imagezip (from new std pxe image)

### ubuntu - new std pxe image

    ~ # fdisk -l /dev/sda
    
    Disk /dev/sda: 240.0 GB, 240057409536 bytes
    255 heads, 63 sectors/track, 29185 cylinders
    Units = cylinders of 16065 * 512 = 8225280 bytes
    
       Device Boot      Start         End      Blocks  Id System
    /dev/sda1   *           1       28155   226152448  83 Linux
    /dev/sda2           28155       29186     8275969   5 Extended
    /dev/sda5           28155       29186     8275968  82 Linux swap


    ~ # /usr/bin/imagezip -o -z1 /dev/sda /dev/null
    imagezip: P2 and P5 overlap!
    * * * Aborting * * *
     
### fedora - new std pxe image


    ~ # fdisk -l /dev/sda
    
    Disk /dev/sda: 240.0 GB, 240057409536 bytes
    255 heads, 63 sectors/track, 29185 cylinders
    Units = cylinders of 16065 * 512 = 8225280 bytes
    
       Device Boot      Start         End      Blocks  Id System
    /dev/sda1   *           1       26053   209263616  83 Linux
    /dev/sda2           26053       29186    25165824  82 Linux swap
    ~ # /usr/bin/imagezip -o -z1 /dev/sda /dev/null
    P3: unused, NOT SAVING.
    P4: unused, NOT SAVING.
    partitioner value (468862128) different than computed value (468860928); using the former
    WARNING: '/dev/null' does not support fsync, write errors may not be detected or corrected.
    .............................................................    395488768    2
    .............................................................    782006784    5
    .............................................................   1900688384    7
    .............................................................   2709018624   10
    .............................................................   3103745536   12
    .............................................................   3522173440   14
    .............................................................  49675804672   20
    .............................................................  50339937792   22
    .............................................................  50910098944   24
    .....................................
    214287024128 input (4844244992 compressed) bytes in 35.408 seconds
    Image size: 615514112 bytes
    130.474MB/second compressed
    Finished in 36.352 seconds

## new imagezip (from hybrid image)

### ubuntu - hybrid image

    /images/frisbee-binaries-inria # ./imagezip -o -z1 /dev/sda /dev/null
      Slice 6 is unused, NOT SAVING.
      Slice 7 is unused, NOT SAVING.
      Slice 8 is unused, NOT SAVING.
      Slice 3 is unused, NOT SAVING.
      Slice 4 is unused, NOT SAVING.
    WARNING: '/dev/null' does not support fsync, write errors may not be detected or corrected.
    .............................................................    965288960    2
    .............................................................   2303833600    5
    .............................................................   4308653568    8
    .............................................................   5660447232   10
    .............................................................  65952675840   16
    ............................................................. 147379304960   23
    .................................
    ............
    231582236672 input (4871983104 compressed) bytes in 30.815 seconds
    Image size: 432013312 bytes
    150.780MB/second compressed
    Finished in 31.799 seconds
    
For the record with `-z9`
    
    231582236672 input (4871983104 compressed) bytes in 190.347 seconds
    Image size: 382730240 bytes
    24.410MB/second compressed
    Finished in 191.324 seconds
    
### fedora - hybrid image

    /images/frisbee-binaries-inria # ./imagezip -o -z1 /dev/sda /dev/null
      Slice 3 is unused, NOT SAVING.
      Slice 4 is unused, NOT SAVING.
    WARNING: '/dev/null' does not support fsync, write errors may not be detected or corrected.
    .............................................................    395488768    2
    .............................................................    782006784    5
    .............................................................   1900688384    7
    .............................................................   2709018624   10
    .............................................................   3103745536   12
    .............................................................   3522173440   14
    .............................................................  49675804672   20
    .............................................................  50339937792   22
    .............................................................  50910098944   24
    .....................................
    214287024128 input (4844244992 compressed) bytes in 35.217 seconds
    Image size: 615514112 bytes
    131.182MB/second compressed
    Finished in 36.163 seconds
    
 For the record with `-z9`
 
    214287024128 input (4844244992 compressed) bytes in 200.951 seconds
    Image size: 564133888 bytes
    22.990MB/second compressed
    Finished in 201.888 seconds
