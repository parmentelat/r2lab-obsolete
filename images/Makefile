#
# This file is intended for keeping track of what was done
# not for being executed routinely

INFRA		= faraday.inria.fr
SSH_INFRA	= root@$(INFRA)

pull: pull-tftpboot pull-images

pull-tftpboot:
	rsync -av $(SSH_INFRA):/tftpboot .

pull-images:
	rsync -av $(SSH_INFRA):/var/lib/omf-images-6 .

.PHONY: pull pull-tftpboot pull-images

###

push-initramfs:
	rsync -av tftpboot/initramfs-omf6.igz.newfrisbee $(SSH_INFRA):/tftpboot

push-images:
	rsync -av omf-images-6/ $(SSH_INFRA):/var/lib/omf-images-6/

.PHONY:  push-initramfs push-images
