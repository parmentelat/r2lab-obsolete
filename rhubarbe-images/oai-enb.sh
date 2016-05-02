# configuration was about editing this file
# /root/openairinterface5g/targets/PROJECTS/GENERIC-LTE-EPC/CONF/enb.band7.tm1.usrpb210.epc.remote.conf
# in which we have
#
# * changed this line (was 92)
#     mobile_network_code =  "95";
#
# * changed this section to denote the remote (i.e. epc+hss) IP
#     mme_ip_address      = ( {ipv4 = "192.168.2.16";
#                              ipv6="192:168:30::17";
#                              active="yes";
#                              preference="ipv4";});
#
# changed the local IP address and interface name here
#
#     NETWORK_INTERFACES :
#    {
#        ENB_INTERFACE_NAME_FOR_S1_MME            = "data";
#        ENB_IPV4_ADDRESS_FOR_S1_MME              = "192.168.2.11/24";
#
#        ENB_INTERFACE_NAME_FOR_S1U               = "data";
#        ENB_IPV4_ADDRESS_FOR_S1U                 = "192.168.2.11/24";
#        ENB_PORT_FOR_S1U                         = 2152; # Spec 2152
#    };
#
# 
#
# then to run the node we did
cd /root/openairinterface5g/cmake_targets/lte_build_oai/build
./lte-softmodem -O /root/openairinterface5g/targets/PROJECTS/GENERIC-LTE-EPC/CONF/enb.band7.tm1.usrpb210.epc.remote.conf

# need to align these 

epc:          {MCC="208" ; MNC="95";  TAC = "1"; },                                  # YOUR TAI CONFIG HERE

with

enb:    tracking_area_code  =  "1";
