# prelude

Early 2018, when it was time to redo images with more recent distros, I ran into the frisbee issue again; and nothing has changed on that matter, and probably won't.

So I had a closer look at other possible options, and came across a few things

## the pieces

in order to replace frisbee, we need a few things

### disk imaging
 a tool that stores and restores disk images;
  it needs to know about the recent file systems like ext4;
  it's ok if it supports only identical hardwares, but better if it can be used
  with slightly different geometries

**clonezilla** could maybe do the trick Here

### multicast file transfer

**udpcast** could be our boy;

* see `udp-sender` and `udp-receive`
* that I have installed on `etourdi` as part if the `udpcast` stock rpm
* these 2 binaries are dynamically linked though


### a boot image

* I have started to play with the image as provided by `udpcast`
* they give a standard initramfs image, which is small already
* and it comes with an online configurator that allows to pick some components so as to make it even smaller - [called cast-o-matic](http://www.udpcast.linux.lu/cast-o-matic/)
* this results in a really small initrd image (< 1Mb)
* while the generic one is hardly larger (7.5 Mb)

However at this point I see the following issues

##### dynamically linked
* not sure how to ship dynamically binaries
* nor even to add binaries actually (one experiment was to copy /bin/cat - a dynamically linked binary in the image, and call it from /init, but that ended in a weird message from busibox)

##### telnet or not
* now our image is huge; it comes with a running telnet server, and we get in touch with that in order to trigger image loading or cloning
* this allows to specify stuff like server details (IP & ports and the like); it is not clear how multiple sessions of udp-* coexist
* this matters because if we could avoid the telnet business altogether, it would be nicer; it might be workable to create images on the fly instead.

##### imaging
first and foremost, I'd need to get a better grip on how clonezilla can be triggered from a regular environment, and make tests that involve a complet cycle

* old-node
* -> save new image format
* -> restore node from that
* -> save again


## Note on drivers

Here are the drivers that seem important for us

Note that if we could get to using this method, we could probably enable AHCI on the hard drive controllers.

##### (wired) ethernet drivers

* `igb` for `control`
* optionnally `e1000e` for `data`


##### hard drive drivers

* `ata_piix` is the one needed for running the hard drive in IDE mode
* `ahci` is the one needed with the hard drive in AHCI mode which is 4-5 times faster
