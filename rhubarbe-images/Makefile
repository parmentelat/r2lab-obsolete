#
# This file is intended for keeping track of what was done
# not for being executed routinely

NAME		= faraday
INFRA		= $(NAME).inria.fr
SSH_INFRA	= root@$(INFRA)
IMAGES		= /var/lib/rhubarbe-images

###
pull:
	rsync -av $(SSH_INFRA):$(IMAGES)/ ./

###
push:
	@echo "Sample push command"
	@echo rsync -av initramfs-omf6.igz.newfrisbee $(SSH_INFRA):/tftpboot/
	rsync -av  --exclude Makefile ./ $(SSH_INFRA):$(IMAGES)/

.PHONY: pull push

###
install:
	rsync -av pull-from-preplab.sh $(SSH_INFRA):$(IMAGES)/
