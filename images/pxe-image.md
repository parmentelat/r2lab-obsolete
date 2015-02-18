# Preparing the image

As a short reminder, here's the gist of how I came up with my modified PXE image

* start from the PXE image in operation with other OMF deployments

###
    parmentelat ~/git/fitsophia/images/tftpboot $ ls -l initramfs-omf6.igz.oldfrisbee
    -rwxr-xr-x  1 parmentelat  staff  71103697 Feb 17 10:04 initramfs-omf6.igz.oldfrisbee
* unwrap it

###
    mkdir unwrap-initramfs-omf6
    cd unwrap-initramfs-omf6
    gzip -cd ../tftpboot/initramfs-omf6.igz | cpio -diu
    
* overwrite old binaries / install new stuff 

###
    cp .../frisbee usr/sbin
    cp .../frisbeed usr/sbin
    cp .../imagezip usr/bin
    cp .../imageunzip usr/bin
    cp .../imagedump usr/bin

* check (against a pristine unwrapped copy)

###        
    parmentelat ~/git/fitsophia/images $ diff -r unwrap-initramfs-omf6 wrap-new-frisbee
    diff: unwrap-initramfs-omf6/etc/mtab: No such file or directory
    diff: wrap-new-frisbee/etc/mtab: No such file or directory
    diff: unwrap-initramfs-omf6/sbin/udevadm: No such file or directory
    diff: wrap-new-frisbee/sbin/udevadm: No such file or directory
    diff: unwrap-initramfs-omf6/usr/bin/ar: No such file or directory
    diff: wrap-new-frisbee/usr/bin/ar: No such file or directory
    diff: unwrap-initramfs-omf6/usr/bin/ckbcomp: No such file or directory
    diff: wrap-new-frisbee/usr/bin/ckbcomp: No such file or directory
    Binary files unwrap-initramfs-omf6/usr/bin/imagedump and wrap-new-frisbee/usr/bin/imagedump differ
    Binary files unwrap-initramfs-omf6/usr/bin/imageunzip and wrap-new-frisbee/usr/bin/imageunzip differ
    Binary files unwrap-initramfs-omf6/usr/bin/imagezip and wrap-new-frisbee/usr/bin/imagezip differ
    Binary files unwrap-initramfs-omf6/usr/sbin/frisbee and wrap-new-frisbee/usr/sbin/frisbee differ
    Binary files unwrap-initramfs-omf6/usr/sbin/frisbeed and wrap-new-frisbee/usr/sbin/frisbeed differ
    diff: unwrap-initramfs-omf6/var/lib/dpkg/info/amd64: recursive directory loop
    
* rebuild the new image

###
    find . | cpio -H newc -o | gzip -9 > ../tftpboot/initramfs-omf6.igz.newfrisbee
    
* results
 
###
    parmentelat ~/git/fitsophia/images/tftpboot $ ls -l initramfs-omf6.igz.*
    -rwxr-xr-x  1 parmentelat  staff  70491187 Feb 17 10:35 initramfs-omf6.igz.newfrisbee
    -rwxr-xr-x  1 parmentelat  staff  71103697 Feb 17 10:04 initramfs-omf6.igz.oldfrisbee
    
    
# Installing on the infrastructure side (bemol)

## the frisbee binaries
    cd /usr/sbin
    mv frisbee frisbee-old-64
    mv frisbeed frisbeed-old-64

and then install the 2 binaries from frisbee-binaries-inria/ instead

## the pxe image

    cd /tftpboot/
    mv initramfs-omf6.igz initramfs-omf6.igz.oldfrisbee

and then install `initramfs-omf6.igz.newfrisbee` 

**NOTE** that using a symlink for `initramfs-omf6.igz` does not seem to work so my convenience functions do `rsync` and not 	 `ln -s`

## convenience tools

    root@bemol:~# pxe_new
    new pxe-frisbee config
    -rwxr-xr-x 1 root root 70556800 Feb 17 15:51 /tftpboot/initramfs-omf6.igz
    -rwxr-xr-x 1 root root 70556800 Feb 17 15:51 /tftpboot/initramfs-omf6.igz.newfrisbee
    -rwxr-xr-x 1 root root 71103697 Feb 17 10:04 /tftpboot/initramfs-omf6.igz.oldfrisbee
    -rwxr-xr-x 1 root root  1026664 Feb 17 14:22 /usr/sbin/frisbee
    -rwxr-xr-x 1 root root  1026664 Feb 17 14:22 /usr/sbin/frisbee-new-64
    -rwxr-xr-x 1 root root   975160 Aug  9  2012 /usr/sbin/frisbee-old-64
    -rwxr-xr-x 1 root root   981304 Feb 17 14:22 /usr/sbin/frisbeed
    -rwxr-xr-x 1 root root   981304 Feb 17 14:22 /usr/sbin/frisbeed-new-64
    -rwxr-xr-x 1 root root   917624 Aug  9  2012 /usr/sbin/frisbeed-old-64

    root@bemol:~# pxe_old
    old pxe-frisbee config
    -rwxr-xr-x 1 root root 71103697 Feb 17 10:04 /tftpboot/initramfs-omf6.igz
    -rwxr-xr-x 1 root root 70556800 Feb 17 15:51 /tftpboot/initramfs-omf6.igz.newfrisbee
    -rwxr-xr-x 1 root root 71103697 Feb 17 10:04 /tftpboot/initramfs-omf6.igz.oldfrisbee
    -rwxr-xr-x 1 root root   975160 Aug  9  2012 /usr/sbin/frisbee
    -rwxr-xr-x 1 root root  1026664 Feb 17 14:22 /usr/sbin/frisbee-new-64
    -rwxr-xr-x 1 root root   975160 Aug  9  2012 /usr/sbin/frisbee-old-64
    -rwxr-xr-x 1 root root   917624 Aug  9  2012 /usr/sbin/frisbeed
    -rwxr-xr-x 1 root root   981304 Feb 17 14:22 /usr/sbin/frisbeed-new-64
    -rwxr-xr-x 1 root root   917624 Aug  9  2012 /usr/sbin/frisbeed-old-64