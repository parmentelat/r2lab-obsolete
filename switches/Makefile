all:
	echo pick one of the push- targets


# once you have made a make push you can run from the switch something like e.g.
# 
# copy tftp://192.168.4.100/switch-c007.conf startup-config
# copy tftp://192.168.4.100/switch-c007.conf running-config
# copy tftp://192.168.4.100/switch-data.conf startup-config
# copy tftp://192.168.4.100/switch-data.conf running-config
# copy tftp://192.168.4.100/switch-control.conf startup-config
# copy tftp://192.168.4.100/switch-control.conf running-config
# copy tftp://192.168.4.100/switch-reboot.conf startup-config
# copy tftp://192.168.4.100/switch-reboot.conf running-config
# reload

push-dell:
	rsync -av switch-*.conf root@faraday.inria.fr:/tftpboot/

push-interfaces:
	rsync -av interfaces.faraday root@faraday.inria.fr:/etc/network/interfaces

push-dnsmasq:
	rsync -av dnsmasq.conf.faraday root@faraday.inria.fr:/etc/dnsmasq.conf
