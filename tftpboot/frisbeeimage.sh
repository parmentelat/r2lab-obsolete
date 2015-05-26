see dedicated VM frisbeeimage in stupeflip

UBUNTU=vivid

function init_debootstrap () {
    cd /build
    [ -d $UBUNTU-root-ref ] && { echo reference already present ; return 0; }
    debootstrap -no-gpg-check $UBUNTU $UBUNTU-root-ref
    apt-get install rsync
}

function clone_and_tweak () {

    cd /build
    rsync -av $UBUNTU-root-ref/ $UBUNTU-root/

    chroot /build/$UBUNTU-root << CHROOT

cat > /etc/fstab << FSTAB
# /etc/fstab: static file system information.
# <file system>	<mount point>	<type>	<options>	<dump>	<pass>
/dev/ram0	/		ext2	defaults	0	0
proc		/proc		proc	defaults	0	1
tmpfs		/tmp		tmpfs	defaults	0	1
FSTAB

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

##########
# kernel modules

########## telnet /ssh
# might wish to start with ssh 
    
# sources.list for 'universe'
# telnetd


CHROOT


}

function install_newfrisbee () {
    cd /build/fitsophia
    git pull
    cd frisbee-binaries-inria
    rsync -av frisbee* /build/$UBUNTU-root/usr/sbin
    rsync -av image* /build/$UBUNTU-root/usr/bin
}

function prune_useless_stuff () {

    packages="
ppp pppconfig pppoe pppoeconf whiptail libnewt0.51 libpcap0.7
logrotate libpopt0 at sysklogd klogd
iptables ipchains
cron exim4 exim4-base exim4-config exim4-daemon-light mailx
base-config adduser makedev
apt apt-utils base-config aptitude tasksel 
gettext-base
nano nvi ed
man-db manpages groff-base info
pciutils bsdmainutils fdutils cpio modutils
console-tools console-common console-data libconsole
"
    chroot /build/$UBUNTU-root << CHROOT
dpkg --purge $packages
CHROOT
}

function wrap_up () {
    cd /build/$UBUNTU-root
    find . | cpio -H newc -o | gzip -9 > /build/pxevivid.igz    
}

init_debootstrap
clone_and_tweak
install_newfrisbee
prune_useless_stuff
wrap_up
