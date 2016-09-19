#!/bin/bash

help_message=""
function record-help () {
    for line in "$@"; do
	help_message="${help_message}${line}\n"
    done
}

function help () {
    echo $help_message
}

#################### README
# here's a list of additional stuff that we need to integrate in
# the standard image-building process
# * initialize r2lab/ and trigger infra/user-env/nodes.sh - together with a command to update from git
# * all images should have a common ssh key so that users don't need to mess with their known_hosts


########################################
# UBUNTU
########################################

record-help "ubuntu-ssh: tweaks sshd_config, remove dummy r2lab user, remove root password, restart ssh"
function ubuntu-ssh () {

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


record-help "ubuntu-base: remove /etc/hostname, install base packages"
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


record-help "ubuntu-interfaces: overwrite /etc/network/interfaces"
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


record-help "ubuntu-dev: add udev rules for canonical interface names"
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

record-help "init-infra-nodes: set up /root/r2lab and add infra/user-env/nodes.sh to /etc/profile.d"
function init-infra-nodes () {
    type -p git 2> /dev/null || { echo "git not installed - cannot proceed"; return; }
    cd /root
    [ -d r2lab ] || git clone https://github.com/parmentelat/r2lab.git
    cd /root/r2lab
    git pull
    cd /etc/profile.d
    ln -sf /root/r2lab/infra/user-env/nodes.sh .
}


record-help "init-node-ssh-key: install standard R2lab key as the ssh node's key"
function init-node-ssh-key () {
    [ -f /root/r2lab/rhubarbe-images/r2lab-nodes-key -a \
	 -f /root/r2lab/rhubarbe-images/r2lab-nodes-key.pub ] || {
	echo "Cannot find standard R2lab node key - cannot proceed"; return;
    }
    for ext in "" ".pub"; do
	cp /root/r2lab/rhubarbe-images/r2lab-nodes-key${ext} /etc/ssh/ssh_host_rsa_key${ext}
	chown root:root /etc/ssh/ssh_host_rsa_key${ext}
    done
    chmod 600 /etc/ssh/ssh_host_rsa_key
    chmod 444 /etc/ssh/ssh_host_rsa_key.pub
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
