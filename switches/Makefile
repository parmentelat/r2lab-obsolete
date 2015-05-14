all:
	echo pick one of the push- targets


# once you have made a make push you can run from the switch something like e.g.
# 
# switch-data#copy tftp://192.168.4.100/switch-data.conf startup-config
# switch-data#reload
push-dell:
	rsync -av switch-*.conf root@faraday.inria.fr:/tftpboot/

push-interfaces:
	rsync -av interfaces.faraday root@faraday.inria.fr:/etc/network/interfaces

push-dnsmasq:
	rsync -av dnsmasq.conf.faraday root@faraday.inria.fr:/etc/dnsmasq.conf
