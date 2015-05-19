# Status

## faraday

not even sure the vlan package was required as we do not use `vconfig` at all

    apt-get install vlan
    echo 8021q >> /etc/modules

* network OK at reboot - see /etc/network/interfaces
* dnsmasq OK on control (dhcp+tftp) data (dhcp+tftp) switches (tftp only hopefully)

## test node (ubuntu)

here is a convenience script to check for connectivity on the data plane

it does not test for DHCP

should work with both our ubuntu and fedora images - although this is probably greatly improvable (figure ethernet device name from `ip show addr` or something)


    function init_subnet2 () {
       set -x
       [ -f /etc/lsb-release ] && control_dev=p2p1 || control_dev=enp3s0
       ip addr show $control_dev >& /dev/null || { 
          echo Could not find control device - "$control_dev" does not exist; 
          return 1;}
       [ -f /etc/lsb-release ] && data_dev=eth2 || data_dev=enp0s25
       ip addr show $data_dev >& /dev/null || { 
          echo Could not find control device - "$data_dev" does not exist; 
          return 1;}
       control_ip=$(ip addr show $control_dev | grep -v inet6 | grep inet | awk '{print $2;}')
       data_ip=$(echo $control_ip | sed -e s,.3.,.2.,)
       echo control=$control_ip on $control-dev, data=$data_ip on $data_dev 
       ip addr add dev $data_dev $data_ip brd 192.168.2.255
       ip addr show $data_dev
       set +x
    }
    function ping_subnet2 () {
       set -x
       [ -f /etc/lsb-release ] && data_dev=eth2 || data_dev=enp0s25
       ip addr show $data_dev >& /dev/null || { 
          echo Could not find control device - "$data_dev" does not exist; 
          return 1;}
       ping -c 2 -I $data_dev 192.168.2.100
       set +x
    }

