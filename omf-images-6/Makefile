#
# This file is intended for keeping track of what was done
# not for being executed routinely

NAME		= faraday
INFRA		= $(NAME).inria.fr
SSH_INFRA	= root@$(INFRA)

###
pull:
	rsync -av $(SSH_INFRA):/var/lib/omf-images-6/ ./

###
push:
	@echo "Sample push command"
	@echo rsync -av initramfs-omf6.igz.newfrisbee $(SSH_INFRA):/tftpboot/
	rsync -av  --exclude Makefile ./ $(SSH_INFRA):/var/lib/omf-images-6/

.PHONY: pull push
