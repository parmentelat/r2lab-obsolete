# scaffolding

not quite sure how to migrate from raw mode to vlan mode, especially from a remote location, as chances to lose touch with all switches is rather high; so local work is mandatory

possible roadmap

* it is essential to preserve IP connectivity between faraday and the switch interfaces (.4.10x) if we want to be able to grab config files with tftp

* probably start with the data subnet - 192.168.2.0/24 - vlan=20 - name=data as it is not crucial

* go from faraday to the end network
  * faraday : (check again if our /etc/network/interfaces works or not now that we have the auto directives added)
  * 

# test node (ubuntu)

this was done on fit37 (ubuntu)

enable interface `eth2`

    control=$(ip addr show p2p1 | grep -v inet6 | grep inet | awk '{print $2;}')
    data=$(echo $control | sed -e s,.3.,.2.,)
    echo control=$control data=$data
    ip addr add dev eth2 $data brd 192.168.2.255
    ping -c 2 192.168.2.100
 
# faraday (ubuntu)

    apt-get install vlan
    echo 8021q >> /etc/modules
    # virtual interface 'data' on vlan 20 and subnet 192.168.2.x
    ip addr del dev p2p1 192.168.2.100/24
    ip link add link p2p1 name data type vlan id 20
    ip link set dev data up
    ip addr add dev data 192.168.2.100/24 brd 192.168.2.255    
    # virtual interface 'reboot' on vlan 10 and subnet 192.168.1.x
    ip addr del dev p2p1 192.168.1.100/24
    ip link add link p2p1 name reboot type vlan id 10
    ip link set dev reboot up
    ip addr add dev reboot 192.168.1.100/24 brd 192.168.1.255    
	**WARNING**
    # virtual interface 'control' on vlan 30 and subnet 192.168.3.x
    ip addr del dev p2p1 192.168.3.100/24
    ip link add link p2p1 name control type vlan id 30
    ip link set dev control up
    ip addr add dev control 192.168.3.100/24 brd 192.168.1.255    

I have a first draft of /etc/network/interfaces in git, that needs to be tested again

# data switch (power connect 62xx)

See the various .conf files for hints on the syntax, in particular for
* interface range
* switchport mode & stuff
