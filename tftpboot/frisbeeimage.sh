#!/bin/bash
#
# inspired from
# http://www.evanjones.ca/software/pxeimager-scratch.html
# (not current any more)
#
# see also
# http://superuser.com/questions/519264/reboot-the-system-from-an-initrd-without-causing-a-kernel-panic
#
# this shell is meant to run inside a dedicated build box
# requirements
# running ubuntu (or at least have debootstrap)
# requires git, rsync, and similar tools, exact list unknown yet
# 
# we run this inside frisbeeimage.pl.sophia.inria.fr - a vivid VM
#
# a /build/ directory
# 
# /build/r2lab is expected to have been set up as a git clone of
#    https://github.com/parmentelat/r2lab.git
# this is the place where the frisbee binaries are being fetched
#
# NOTE about locating proper kernel image
# I could not at first sight figure out the naming scheme in
# the ubuntu repo and pacakges
# Ideally I would have liked to run something like
# apt-get download linux-image
# but this ends in some ghost package that I cannot do anything from
# so to start stuff up I did instead - manually :
# apt-get download linux-image-3.19.0.18-generic
# which was in line with vivid on may 26 2015
# and resulted in this file being downloaded in /build
# linux-image-3.19.0-18-generic_3.19.0-18.18_amd64.deb

COMMAND=$(basename $0 .sh)
LOG=/build/$COMMAND.log

###
### PRELUDE
###
#
# because frisbeeimage is a linux container (I think), I was not able
# to run mount from within there
# keeping it simple, I ran the following commands manually from the host (stupeflip)
#
# ISO=ubuntu-$VERSION-server-amd64.iso
#
DISTRO=vivid
VERSION=15.04
SH=/bin/sh
#
# root@stupeflip /vservers/frisbeeimage/build # mount -o loop ubuntu-15.04-server-amd64.iso mnt
# mount: /dev/loop0 is write-protected, mounting read-only
# root@stupeflip /vservers/frisbeeimage/build # cp mnt/install/netboot/ubuntu-installer/amd64/linux linux-15.04
# root@stupeflip /vservers/frisbeeimage/build # cp mnt/install/netboot/ubuntu-installer/amd64/initrd.gz initrd.gz-15.04
# root@stupeflip /vservers/frisbeeimage/build # umount mnt
#
# DISTRO=f21
# VERSION=21
# SH=/bin/bash
#
# root@stupeflip /vservers/frisbeeimage/build # mount -o loop Fedora-Server-netinst-x86_64-21.iso mnt
#mount: /dev/loop0 is write-protected, mounting read-only
#root@stupeflip /vservers/frisbeeimage/build # cp mnt/images/pxeboot/vmlinuz linux-f21
#root@stupeflip /vservers/frisbeeimage/build # cp mnt/images/pxeboot/initrd.img initrd.img-f21
#root@stupeflip /vservers/frisbeeimage/build # umount mnt

DISTRO=mini15.04
VERSION=mini15.04
SH=/bin/sh

# root@stupeflip /vservers/frisbeeimage/build # mount ubuntu-mini-remix-15.04-amd64.iso mnt
# root@stupeflip /vservers/frisbeeimage/build # cp mnt/casper/vmlinuz linux-mini15.04
# root@stupeflip /vservers/frisbeeimage/build # cp mnt/casper/initrd.lz initrd.lz-mini15.04
# root@stupeflip /vservers/frisbeeimage/build # umount mnt

function init_reference () {
    apt-get install -y rsync lzma
    cd /build
    [ -d $REF ] && { echo reference already present ; return 0; }
    # wthout --variant, this is equivalent to --variant=minbase
    mkdir -p $REF
    cd $REF
#    gzip -dc /build/initrd.gz-$VERSION | cpio -diu
    #    cat /build/initrd.img-$DISTRO | cpio -diu
    cat /build/initrd.lz-$VERSION | lzma -dc | cpio -diu
    
}

function clone_and_tweak () {

    cd /build
    [ -d $ROOT ] && { echo "Cleaning up sequels"; rm -rf $ROOT; }

    rsync -a $REF/ $ROOT/

    ########## entry point
    # install our entry point in image's /bin/pxe-init
    mkdir $ROOT/bin
    rsync -av pxe-init $ROOT/bin

# for the ubuntu old-style init-based image
#    # tweak inittab so that our init program gets used
#    sed --in-place=.ubuntu \
#	-e 's,^\(::sysinit.*\),#\1,' \
#	-e 's,^\(::respawn.*\),#\1,' \
#	$ROOT/etc/inittab
#    echo "::sysinit:/bin/pxe-init" >> $ROOT/etc/inittab

    # tmp - used in pxe-init - requires that build runs same ubuntu
    # probably requires dynamic libs anyway
    mkdir $ROOT/sbin
    rsync -av /sbin/fdisk $ROOT/sbin
    rsync -av /lib/x86_64-linux-gnu $ROOT/lib

    ########## networking
    chroot $ROOT $SH << CHROOT

cat > /etc/hostname << HOSTNAME
pxefrisbee
HOSTNAME

mkdir -p /etc/network
cat > /etc/network/interfaces << INTERFACES
# Used by ifup(8) and ifdown(8). See the interfaces(5) manpage or
# /usr/share/doc/ifupdown/examples for more information.
# The loopback network interface
auto lo
iface lo inet loopback
# The primary network interface
auto eth0
iface eth0 inet dhcp
INTERFACES

CHROOT

    # remove root password
    chroot $ROOT $SH << CHROOT
passwd --delete root
CHROOT

}

########## telnet /ssh
# might wish to start with ssh rather than telnet that seems to 
# pull a lot of dependencies
function create_entry () {
    [ -n "$WITH_SSH" ] && setup_ssh
    [ -n "$WITH_TELNET" ] && setup_telnet
}
    
function setup_ssh () {
    chroot $ROOT $SH << CHROOT
apt-get install -y openssh-server
CHROOT
    # looks like apt-get install enables the service with systemctl
    sed --in-place=.ubuntu \
	-e 's,^#\?PermitRootLogin.*,PermitRootLogin yes,' \
	-e 's,^#\?PermitEmptyPasswords.*,PermitEmptyPasswords yes,' \
	-e 's,^#\?PasswordAuthentication.*,PasswordAuthentication yes,' \
	-e 's,^#\?UsePAM.*,UsePAM no,' \
	$ROOT/etc/ssh/sshd_config
}

function setup_telnet () {
    echo deb http://archive.ubuntu.com/ubuntu $DISTRO universe > $ROOT/etc/apt/sources.list.d/universe.list
    chroot $ROOT $SH << CHROOT
apt-get update
apt-get install -y telnetd
CHROOT
    echo "XXX FIXME : telnet server setup incomplete"
}

####################
function install_newfrisbee () {
    cd /build/r2lab/frisbee-binaries-inria
    rsync -av frisbee* /$ROOT/usr/sbin
    rsync -av image* /$ROOT/usr/bin
}

function prune_useless_stuff () {
    # xxx this list probably needs more care
    # not sure that we care that much about image size any more in 2015,
    # since uploading 125Mb takes around 2s at 500Mbps
    to_trash="rsyslog adduser initramfs-tools cpio python3 python3-minimal
libnewt0.52 libpcap2 logrotate libpopt0 cron makedev apt apt-utils base-config 
"

    # normalize - remove newlines
    to_trash=$(echo $to_trash)
    
    chroot $ROOT $SH << CHROOT
dpkg --purge $to_trash
CHROOT
}

function wrap_up () {
    [ -n "$SKIP_WRAP" ] && { echo "SKIP_WRAP : no image produced"; return 0; }
    cd $ROOT
    find . | cpio -H newc -o | gzip -9 > /build/irfs-pxe$DISTRO.igz
#    find . | cpio -H newc -o > /build/irfs-pxe$DISTRO
}

function usage () {
    echo "$COMMAND [-d distro ] [ -w ] [ -0 | -s | -t | -2 ]"
    echo -e " -d distro\tspecify ubuntu distro (default $DEFAULT_DISTRO)"
    echo -e " -s | -t | -2 | -0\tselect sshd (-s, default) or telnetd (-t) or both (-2) or none (-0)"
    echo -e " -w\t\tskip creation of gzipped image, just root tree"
    exit 1
}

function main () {
    set -x

    WITH_SSH=true
    WITH_TELNET=
    # if this is set to non-empty, no igz is produced
    SKIP_WRAP=

########## end options

    while getopts "d:st20w" opt ; do
	case $opt in
	    d) DISTRO=$OPTARG;;
	    s) WITH_SSH="true"; WITH_TELNET="" ;;
	    t) WITH_SSH=""; WITH_TELNET="true" ;;
	    2) WITH_SSH="true"; WITH_TELNET="true" ;;
	    0) WITH_SSH=""; WITH_TELNET="" ;;
	    w) SKIP_WRAP=true ;;
	    *) usage ;;
	esac
    done

    shift $(($OPTIND - 1))
    [[ -z "$@" ]] || usage

    [ -z "$DISTRO" ] && DISTRO=$DEFAULT_DISTRO

    REF=/build/$DISTRO-root-ref
    ROOT=/build/$DISTRO-root
    init_reference
    clone_and_tweak
    prune_useless_stuff
    install_newfrisbee
    create_entry
#    echo "TMP END"
#    exit 0
    wrap_up
}

main "$@" > $LOG 2>&1 
