#!/bin/sh

# helper for creating a gnuradio image
#

set -x

function usrp_interface () {
    # rename interface 'data' into 'usrp'
    sed -i -e 's,data,usrp,g' /etc/udev/rules.d/70-persistent-net.rules
    # forget about the definition of 'data'
    cd /etc/sysconfig/network-scripts
    mv -f ifcfg-data ifcfg-usrp
    sed -i -e s,data,usrp,g -e 's,^\(BOOTPROTO\)=dhcp,#\1,' ifcfg-usrp
    cat >> ifcfg-usrp <<EOF
BOOTPROTO=static
IPADDR=192.168.10.1
NETMASK=255.255.255.0
EOF
    cd -

}

function setup_pythonpath () {
    echo export PYTHONPATH=/usr/local/lib/python2.7/site-packages >> ~/.bashrc
}

function install_from_yum () {
    yum install gnuradio uhd
}

usrp_interface
setup_pythonpath
install_from_yum

exit

# sequels : only for rebuilding from source

########## as root
function install_requirements () {
    yum groupinstall -y "Engineering and Scientific" "Development Tools" 

    yum install -y fftw-devel cppunit-devel wxPython-devel libusb-devel \
  guile boost-devel alsa-lib-devel numpy gsl-devel python-devel pygsl \
  ice-devel ice-python-devel swig python-sphinx orc-devel orc-compiler\
  python-cheetah python-lxml guile-devel PyOpenGL PyQt4-devel qwt-devel \
  qwtplot3d-qt4-devel cmake xmlto graphviz PyQwt PyQwt-devel zeromq-devel \
  python-zmq comedilib-devel SDL-devel

}

### xxx
# checkpointing in gnuradio-fedora21-requirements.ndz

# xxx
# need to proceed with
# https://gnuradio.org/redmine/projects/gnuradio/wiki/FedoraInstall

# to be completed some other day if at all
