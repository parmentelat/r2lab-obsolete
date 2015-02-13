# once you have made a make push you can run from the switch something like e.g.
# 
# switch-data#copy tftp://192.168.3.100/switch-data.conf startup-config
# switch-data#reload

all: push

push:
	rsync -av switch-*.conf root@faraday.inria.fr:/tftpboot/

.PHONY: all push
