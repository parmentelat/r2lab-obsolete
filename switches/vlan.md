# Status

## faraday

* could not get /etc/network/interfaces right for now; 
  * see below for how to do it manually
* dnsmasq
  * need to understand how current setup works at all (should send packets tagged with VLAN-40..)
  * check for multi-net configs if available
* do more tests
  * check we always use the intended network interface...

# test node (ubuntu)


enable interface `eth2`

this was done on fit37 (ubuntu)

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
 
# faraday (ubuntu)

    apt-get install vlan
    echo 8021q >> /etc/modules
    
    # cleanup if starting from previous config
    ip addr del dev p2p1 192.168.2.100/24
    ip addr del dev p2p1 192.168.1.100/24
    ip addr del dev p2p1 192.168.3.100/24
    ip addr del dev p2p1 192.168.4.100/24
    
    # virtual interface 'data' on vlan 20 and subnet 192.168.2.x
    ip link add link p2p1 name data type vlan id 20
    ip link set dev data up
    ip addr add dev data 192.168.2.100/24 brd 192.168.2.255    
    # virtual interface 'reboot' on vlan 10 and subnet 192.168.1.x
    ip link add link p2p1 name reboot type vlan id 10
    ip link set dev reboot up
    ip addr add dev reboot 192.168.1.100/24 brd 192.168.1.255    
    # virtual interface 'control' on vlan 30 and subnet 192.168.3.x
    ip link add link p2p1 name control type vlan id 30
    ip link set dev control up
    ip addr add dev control 192.168.3.100/24 brd 192.168.1.255    
    # virtual interface 'switches' on vlan 40 and subnet 192.168.4.x
    ip link add link p2p1 name switches type vlan id 40
    ip link set dev switches up
    ip addr add dev switches 192.168.4.100/24 brd 192.168.4.255    

I have a first draft of /etc/network/interfaces in git, that needs to be tested again

