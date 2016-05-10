#!/bin/bash

help_message=""
function record_help () {
    for line in "$@"; do
	help_message="${help_message}${line}\n"
    done
}

function help () {
    echo $help_message
}

########################################
# UBUNTU
########################################

record_help "ubuntu_ssh: tweaks sshd_config, remove dummy r2lab user, remove root password, restart ssh"
function ubuntu_ssh () {

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


record_help "ubuntu_base: remove /etc/hostname, install base packages"
function ubuntu_base () {
    ###
    rm /etc/hostname

    packages="
rsync git make gcc emacs24-nox
iw ethtool tcpdump wireshark bridge-utils
"

    apt-get update
    apt-get -y install $packages
}


record_help "ubuntu_interfaces: overwrite /etc/network/interfaces"
function ubuntu_interfaces () {
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


record_help "ubuntu_dev: add udev rules for canonical interface names"
function ubuntu_udev () {
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

# todo...


# need to tweak /etc/sysconfig/network-scripts as well
# done manually:
# (*) renamed ifcfg-files
# renamed NAME= inside
# added DEVICE= inside


# need to tweak /etc/network/interfaces accordingly, of course
# turning on DHCP on the data interface cannot be tested on bemol (no data interface..)

if [[ -z "$@" ]] ; then
    help
else
    for subcommand in "$@"; do
	echo Running subcommand $subcommand
	$subcommand
    done
fi
