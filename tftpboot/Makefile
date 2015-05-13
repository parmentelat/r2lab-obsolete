#
# This file is intended for keeping track of what was done
# not for being executed routinely

NAME		= faraday
INFRA		= $(NAME).inria.fr
SSH_INFRA	= root@$(INFRA)

###
pull:
	rsync -av $(SSH_INFRA):/tftpboot/ ./

pull-conf:
	rsync -av $(SSH_INFRA):/tftpboot/\*.conf ./

###
push:
	@echo "Sample push command"
	@echo rsync -av initramfs-omf6.igz.newfrisbee $(SSH_INFRA):/tftpboot/

.PHONY:  pull push
