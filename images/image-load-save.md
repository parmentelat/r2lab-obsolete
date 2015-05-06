# setting stuff up

See pxe-image.md (this dorectory) for how to deal/install the various initramfs images

in short:

    nodes 39
    nextboot_pxe 39
    nextboot_listall
    reset 39
    <wait for some time>
    telnet fit39
    cd /images


# load
## server
    frisbeed -i 192.168.3.200 -m 224.0.0.1 -p 7000 -W 50000000 /var/lib/omf-images-6/baseline.ndz
## client
    frisbee -i 192.168.3.31 -m 224.0.0.1 -p 7000 /dev/sda

# save

## server 
    /bin/nc -d -l 192.168.3.200 9000 > /var/lib/omf-images-6/new_image.ndz
## client
    imagezip -o -z1 /dev/sda - | nc -n 192.168.3.200 9000


# Comparing the outputs from both versions

Data obtained with the `fedora21-ext2` image; server runs with 120 Mbps bandwidth


## old set of binaries

Typical client output reads

    /images # time ./frisbee-binaries-uth/frisbee-old-32 -i 192.168.3.39 -m 224.0.0.1 -p 10000 /dev/sda
    Progress: 10% 000011 000528
    Progress: 20% 000021 000469
    Progress: 30% 000031 000410
    Progress: 40% 000041 000352
    Progress: 50% 000051 000293
    Progress: 60% 000061 000234
    Progress: 70% 000071 000176
    Progress: 80% 000081 000117
    Progress: 90% 000091 000058

    Wrote 240056795136 bytes (4835807232 actual)
    533 6699 22982
    Left the team after 100 seconds on the field!real       1m 42.02s
    user    0m 9.92s
    sys     0m 4.54s
    
## new binaries (64 bits)

    /images/frisbee-binaries-inria # ./frisbee -i 192.168.3.39 -m 224.0.0.1 -p 10000 /dev/sda
    Actual socket buffer size is 425984 (instead of 1048576)
    Maximum socket buffer size of 425984 bytes
    Bound to port 10000
    Using Multicast 224.0.0.1
    Joined the team after 0 sec. ID is 991177963. File is 587 chunks (615514112 bytes)
    ..........ssssssssssssss....ssssssssss.ssss........................   6    549
    ......................ssssssssss.sss...............................  13    496
    ssssssssssssss....s............................ssssssssssss......ss  18    458
    ssssssssss.........................................s...............  26    402
    ....ssssssssssssss...............................................s.  33    350
    ...............................................ssssssssssssss......  40    297
    .....sssssssssssssss.............................................s.  48    246
    ................................................................sss  57    182
    sssssssssssssssssssssssss...................................ss....s  62    143
    sssssssssssss.....ssssssssssssss......sssss..ssssssssssssss........  65    122
    ..................ssssssssssssss............s....sssss.............  71     75
    ....................................................ssssssssssssss.  79     23
    .......................
    Client 991177963 Performance:
      runtime:                82.967 sec
      start delay:            0.000 sec
      real data written:      4835807232 (58973258 Bps)
      effective data written: 240056795136 (2927521891 Bps)
    Client 991177963 Params:
      chunk/block size:     1024/1024
      chunk buffers:        64
      disk buffering (MB):  64
      sockbuf size (KB):    416
      readahead/inprogress: 2/8
      recv timo/count:      30000/3
      re-request delay:     1000000
      writer idle delay:    1000
      randomize requests:   1
    Client 991177963 Stats:
      net thread idle/blocked:        294/0
      decompress thread idle/blocked: 317/945
      disk thread idle:        7290
      join/request msgs:       1/1713
      dupblocks(chunk done):   0
      dupblocks(in progress):  0
      partial requests/blocks: 1126/84039
      re-requests:             1126
      full chunk re-requests:  0
      partially-filled drops:  0
    
    Left the team after 82 on the field!
    Wrote 240056795136 byte seconds s (4835807232 actual)
    945 7290 22982
