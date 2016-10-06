#!/bin/bash

source $(dirname $(readlink -f $BASH_SOURCE))/r2labutils.sh

create-doc-category imaging "tools for creating images"
augment-help-with imaging

########################################
# UBUNTU
########################################

# looks like dpkg -i $url won't work ..
# so this utility fetches a bunch of URLs and shoves them into dpkg
function -dpkg-from-urls() {
    urls="$@"
    debs=""
    for url in $urls; do
	curl -O $url
	debs="$debs $(basename $url)"
    done
    
    if dpkg -i $debs; then
	rm $debs
	return 0
    else
	echo dpkg failed - preserving debs $debs
	return 1
    fi
}

function -dpkg-is-installed() {
    package="$1"
    if dpkg -l $package >& /dev/null; then
	echo package $package already installed
	return 0
    else
	return 1
    fi
}

####################
# started with this howto here:
# http://ubuntuhandbook.org/index.php/2016/07/install-linux-kernel-4-7-ubuntu-16-04/
# see also of course here for any new stuff:
# http://kernel.ubuntu.com/~kernel-ppa/mainline/v4.7/
# won't work with ubuntu-14 though
doc-imaging ubuntu-k47-lowlatency "install 4.7 lowlatency kernel"
function ubuntu-k47-lowlatency() {
    
    -dpkg-is-installed linux-image-4.7.0-040700-lowlatency && return
    
    urls="
http://kernel.ubuntu.com/~kernel-ppa/mainline/v4.7/linux-headers-4.7.0-040700_4.7.0-040700.201608021801_all.deb
http://kernel.ubuntu.com/~kernel-ppa/mainline/v4.7/linux-headers-4.7.0-040700-lowlatency_4.7.0-040700.201608021801_amd64.deb
http://kernel.ubuntu.com/~kernel-ppa/mainline/v4.7/linux-headers-4.7.0-040700-generic_4.7.0-040700.201608021801_amd64.deb
http://kernel.ubuntu.com/~kernel-ppa/mainline/v4.7/linux-image-4.7.0-040700-lowlatency_4.7.0-040700.201608021801_amd64.deb
"

    -dpkg-from-urls $urls
}

# this one is based on the mainstream kernel for 16.10/yikkety
# it works fine on top of both ubuntu 14 and ubuntu 16
function ubuntu-k48-lowlatency() {

    -dpkg-is-installed linux-image-4.8.0-21-lowlatency && return
    
    urls="
http://fr.archive.ubuntu.com/ubuntu/pool/main/l/linux/linux-headers-4.8.0-21_4.8.0-21.23_all.deb
http://fr.archive.ubuntu.com/ubuntu/pool/main/l/linux/linux-headers-4.8.0-21-lowlatency_4.8.0-21.23_amd64.deb
http://fr.archive.ubuntu.com/ubuntu/pool/main/l/linux/linux-headers-4.8.0-21-generic_4.8.0-21.23_amd64.deb
http://fr.archive.ubuntu.com/ubuntu/pool/main/l/linux/linux-image-4.8.0-21-lowlatency_4.8.0-21.23_amd64.deb
"

    -dpkg-from-urls $urls

}

doc-imaging ubuntu-setup-ntp "installs ntp"
function ubuntu-setup-ntp () {
    apt-get install -y ntp ntpdate
    # let's not tweak ntp.conf, use DHCP instead
    # see faraday:/etc/dnsmasq.conf
    systemctl restart ntp || service ntp start
    # I have no idea how to do this on systemctl-less ubuntus
    # hopefully the dpkg install will do it
    systemctl enable ntp || echo "systemctl-less ubuntus : not supported"
}

doc-imaging "ubuntu-setup-ssh: tweaks sshd_config, remove dummy r2lab user, remove root password, restart ssh"
function ubuntu-setup-ssh () {

####################
# expected result is this
# root@r2lab:/etc/ssh# grep -v '^#' /etc/ssh/sshd_config | egrep -i 'Root|Password|PAM'
# PermitRootLogin yes
# PermitEmptyPasswords yes
# PasswordAuthentication yes
# UsePAM no

    # tweak sshd_config
    sed -i.utilities \
	-e 's,^#\?PermitRootLogin.*,PermitRootLogin yes,' \
	-e 's,^#\?PermitEmptyPasswords.*,PermitEmptyPasswords yes,' \
	-e 's,^#\?PasswordAuthentication.*,PasswordAuthentication yes,' \
	-e 's,^#\?UsePAM.*,UsePAM no,' \
	/etc/ssh/sshd_config

    # remove dummy user
    userdel --remove ubuntu

    # remove root password
    passwd --delete root
    
    # restart ssh
    echo "Restarting sshd"
    type systemctl >& /dev/null \
	&& systemctl restart sshd \
        || service ssh restart
    cat << EOF
You should now be able to ssh as root without a password
CHECK IT NOW before you quit this session
EOF
}


doc-imaging "ubuntu-base: remove /etc/hostname, install base packages"
function ubuntu-base () {
    ###
    rm /etc/hostname

    packages="
rsync git make gcc emacs24-nox
iw ethtool tcpdump wireshark bridge-utils
"

    apt-get update
    apt-get -y install $packages
}


doc-imaging "ubuntu-interfaces: overwrite /etc/network/interfaces"
function ubuntu-interfaces () {
    cat > /etc/network/interfaces <<EOF
source /etc/network/interfaces.d/*

# The loopback network interface
auto lo
iface lo inet loopback

# the control network interface - required
auto control
iface control inet dhcp

# the data network interface - optional
#auto data
iface data inet dhcp
EOF

}


doc-imaging "ubuntu-dev: add udev rules for canonical interface names"
function ubuntu-udev () {
####################
# udev
#
# see insightful doc in
# http://reactivated.net/writing_udev_rules.html 
#
# on ubuntu, to see data about a given device (udevinfo not available)
# udevadm info -q all -n /sys/class/net/p2p1
#  -- or --     (more simply)
# udevadm info /sys/class/net/p2p1
#  -- or --
# udevadm info --attribute-walk /sys/class/net/wlp1s0
# 
# create new udev rules for device names - hopefully fine on both distros ?
# 
# p2p1 = control = igb = enp3s0
# eth0 = data = e1000e = enp0s25

cat > /etc/udev/rules.d/70-persistent-net.rules <<EOF
# kernel name would be enp3s0
SUBSYSTEM=="net", ACTION=="add", DRIVERS=="igb", NAME="control"
# kernel name would be enp0s25
SUBSYSTEM=="net", ACTION=="add", DRIVERS=="e1000e", NAME="data"
EOF

# extra rules for fedora and wireless devices
# might work on ubuntu as well
# but was not used when doing the ubuntu15.04 image in the first place
cat > /etc/udev/rules.d/70-persistent-wireless.rules <<EOF
# this probably is the card connected through the PCI adapter
KERNELS=="0000:00:01.0", ACTION=="add", NAME="wlan0"
# and this likely is the one in the second miniPCI slot
KERNELS=="0000:04:00.0", ACTION=="add", NAME="wlan1"
EOF

}

########################################
# FEDORA
########################################
# very incomplete for now...
doc-imaging fedora-setup-ntp "installs ntp"
function fedora-setup-ntp() {
    dnf -y install ntp
    systemctl enable ntpd
    systemctl start ntpd
}

########################################
# common
########################################
doc-imaging "common-setup-user-env: set up /root/r2lab and add infra/user-env/nodes.sh to /etc/profile.d"
function common-setup-user-env () {
    type -p git 2> /dev/null || { echo "git not installed - cannot proceed"; return; }
    cd /root
    [ -d r2lab ] || git clone https://github.com/parmentelat/r2lab.git
    cd /root/r2lab
    git pull
    cd /etc/profile.d
    ln -sf /root/r2lab/infra/user-env/nodes.sh .
    # to make sure to undo previous versions that were wrong in creating this
    rm -f /root/r2lab/infra/r2labutils.sh
}


doc-imaging "common-setup-node-ssh-key: install standard R2lab key as the ssh node's key"
function common-setup-node-ssh-key () {
    [ -f /root/r2lab/rhubarbe-images/r2lab-nodes-key -a \
	 -f /root/r2lab/rhubarbe-images/r2lab-nodes-key.pub ] || {
	echo "Cannot find standard R2lab node key - cannot proceed"; return;
    }
    for ext in "" ".pub"; do
	cp -v /root/r2lab/rhubarbe-images/r2lab-nodes-key${ext} /etc/ssh/ssh_host_rsa_key${ext}
	chown root:root /etc/ssh/ssh_host_rsa_key${ext}
    done
    chmod 600 /etc/ssh/ssh_host_rsa_key
    chmod 444 /etc/ssh/ssh_host_rsa_key.pub
}

########################################
define-main "$0" "$BASH_SOURCE"
main "$@"
