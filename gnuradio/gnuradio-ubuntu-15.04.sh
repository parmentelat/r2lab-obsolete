#!/bin/sh

# helper for creating a gnuradio image
#

set -x

#################### REQUIREMENTS / PREPARATION

########## as root

### tester account
useradd --password tester --comment 'USRP GNURadio user' tester
# add tester in group sudo
usermod -aG sudo tester
# 
echo 'tester ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/tester
chmod 440 /etc/sudoers.d/tester
# so that experimenters can enter the node as tester if they need to
passwd --delete tester

### base install
apt-get update
sudo apt-get install -y git libboost-all-dev libusb-1.0-0-dev libcppunit-dev libfftw3-dev gsl-bin libgsl0-dev python-cheetah doxygen python-docutils cmake libzmq-dev xterm emacs

### interface names and IP config
# there is a need to rename the ethernet interface 'data' into 'usrp'

# rename interface 'data' into 'usrp'
sed -i -e 's,data,usrp,g' /etc/udev/rules.d/70-persistent-net.rules
# comment out the definition of 'data' 
sed -i -e 's,^auto data,#auto data,' /etc/network/interfaces
# create a specific file for usrp
cat > /etc/network/interfaces.d/usrp <<EOF
####################
# static IP address attached to the ethernet link towards USRP
auto usrp
iface usrp inet static
  	address 192.168.10.1
  	netmask 255.255.255.0
####################
EOF

########## as tester : prepare 
su - tester <<EOF

cd
echo export PYTHONPATH=/usr/local/lib/python2.7/site-packages:/usr/local/lib/python2.7/dist-packages >> ~/.bashrc
source ~/.bashrc

mkdir gnuradio && cd gnuradio
wget http://www.sbrac.org/files/build-gnuradio

wget http://www.sbrac.org/files/build-gnuradio
mv build-gnuradio build-gnuradio.broken
sed -e s,libzmq1-dev,libzmq-dev,g build-gnuradio.broken > build-gnuradio
chmod a+x ./build-gnuradio 
EOF

set +x

#################### BUILD UHD and gnuradio

cat <<EOF
You now need to run these commands manually (and answer 'y' to most questions)

su - tester
cd ~/gnuradio
./build-gnuradio

EOF
