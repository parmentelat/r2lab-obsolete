# tweaks of /etc/ssh/sshd_config
# xxx not implemented yet

# tweaks in /etc/hosts (replace actual hostname for loopback address)
# xxx not implemented yet

# the logic on ubuntu is as follows
# * make sure your node has the usual dual-partition disk layout (NO extended partition)
# * reload another image on your target node if unsure (fedora21 is just fine)
# * get the amd64 server iso
# * use USB-startup-creator to make a bootable

# xxx to be completed xxx

# tweak sshd_config
# beware of
# systemctl restart sshd
# vs
# service ssh restart

# root@r2lab:/etc/ssh# grep -v '^#' /etc/ssh/sshd_config | egrep -i 'Root|Password|PAM'
# PermitRootLogin yes
# PermitEmptyPasswords yes
# PasswordAuthentication yes
# UsePAM no
function ubuntu_ssh () {
    sed -iutilities \
	-e 's,^#\?PermitRootLogin.*,PermitRootLogin yes,' \
	-e 's,^#\?PermitEmptyPasswords.*,PermitEmptyPasswords yes,' \
	-e 's,^#\?PasswordAuthentication.*,PasswordAuthentication yes,' \
	-e 's,^#\?UsePAM.*,UsePAM no,' \
	/etc/ssh/sshd_config
    cat <<EOF
Do not forget to restart sshd and to test password-less access to root before quitting
Depending on your release:
systemctl restart sshd
or
service ssh restart
EOF
}

function ubuntu_base () {
    ###
    passwd --delete root
    userdel --remove ubuntu
    rm /etc/hostname

    packages="
rsync git make gcc emacs24-nox
iw ethtool tcpdump wireshark bridge-utils
"

    apt-get -y install $packages

}

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
auto data
#iface data inet dhcp
EOF

}

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


# need to tweak /etc/sysconfig/network-scripts as well
# done manually:
# (*) renamed ifcfg-files
# renamed NAME= inside
# added DEVICE= inside


# need to tweak /etc/network/interfaces accordingly, of course
# turning on DHCP on the data interface cannot be tested on bemol (no data interface..)

for subcommand in "$@"; do
    echo Running subcommand $subcommand
    $subcommand
done
