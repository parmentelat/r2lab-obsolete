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

--------

# new pxe image (anaconda)

## workflow

painful; we have

* `~/git/fitsophia/tftpboot` local git repo
* `frisbeeimage.pl.sophia.inria.fr`: a debian-15.04 VM on stupeflip, for running frisbeeimage.sh (which incidentally does not work right now)
* `boxtops:/vservers/pxelinux` a place where to run a qemu-based node that alows to try out images; some known limitations 
  * in terms of display (uses curses, no graphic mode), 
  * and in terms of networking (not sure how to ping running node even when it does turn on its IP address...)
* plus of course bemol and faraday for more tests

## anaconda / fedora netinst
approach is to use fedora anaconda as-is

host side - tap23 - 10.0.2.2
guest 10.0.2.15

IMPORTANT use PXE images **uncompressed** - ideally as is; with fedora 21 netinstall iso mounted in `mnt/`, we need `initrd.img` and `vmlinuz`

    root@boxtops /vservers/pxelinux # ls -l mnt/images/pxeboot/
    total 88822
    -r--r--r-- 1 root root        664 Dec  4 01:44 TRANS.TBL
    -rw-r--r-- 2 root 101737 43766528 Dec  4 01:41 initrd.img
    -rw-r--r-- 2 root 101737 41433796 Dec  4 01:43 upgrade.img
    -rwxr-xr-x 2 root 101737  5751144 Nov 27  2014 vmlinuz

these boot all right from PXE; using a **compressed** version of initrd.img kicks a **kernel panic** though; 
additionally, setting `inst.sshd` in the **pxelinux.cfg** file should trigger an ssh server inside node

however a simple test on bemol is inconclusive; it might be that we use the wrong interface name ?

working with qemu on pxelinux 


--------

# new PXE image (oldies)
   
## plusieurs approches qui ne marchent pas

* from scratch : deboostrap and all

  ne marche pas bien; kernel panic
  
* a partir d'images pxelinux deja toutes faites

voir divers restes dans `frisbeeimage.sh`

  * plain ubuntu: base sur init sysv-like; quelques succes en modifiant inittab et en injectant un script a moi a la place de sysinit (qui sinon lance l'installer). cependant l'image est tres etriquee, manque `dpkg` et `ifup` et tout un tas de trucs de ce genre

  * ubuntu mini remix: base cette fois sur systemd; pas trouve de moyen simple de customiser; en principe on devrait avoir le reseau as-is, mais pas moyen de pinger le noeud...

  * fedora: image pxe tres etrange, toute petite (44 K apres untar); il y a clairement 
   
### ubuntu mini remix

* downloaded `ubuntu-mini-remix-15.04-amd64.iso` from ubuntu (in os-images)
* pushed onto bemol in `/root` for future work

* mounted -> subdirectory `casper` that has an `inird.lz` and a `vmlinuz`
* created `/tftpboot/initramfs-mini1504.igz` as a gzip from that initrd
* created `/tftpboot/linux-mini1504` from that vmlinuz
* created /tftpboot/ahci

* robustified the `nextboot-` toolset

remains to test this simple collection of files (ahci + kernel +
initrd) on an AHCI node

### vivid - debootstrap

see tftpboot/frisbeeimage.sh

### fedora

Francis said anaconda had an option to do what we need
https://rhinstaller.github.io/anaconda/boot-options.html
inst.sshd
