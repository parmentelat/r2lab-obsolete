# workflow is a bit awkward, but
# . we rebuild the new initramfs - aka irfs - on bemol where we can try it out
# then we push it back onto faraday
#
# so in short, don't use these targets directly 

RSYNC_COND_DRY_RUN	:= $(if $(findstring n,$(MAKEFLAGS)),--dry-run,)
RSYNC = rsync $(RSYNC_COND_DRY_RUN)

SSH_INFRA	= root@faraday.inria.fr

SSH_PREPLAB	= root@bemol.pl.sophia.inria.fr

###
fetch:
	@echo sample fetch command
	@echo rsync -avn $(SSH_PREPLAB):/tftpboot/ ./

fetch-conf:
	@echo sample fetch command
	@echo 'rsync -avn $(SSH_PREPLAB):/tftpboot/\*.conf ./'

###
push:
	@echo "Sample push commands"
	@echo rsync -avn irfs-* $(SSH_PREPLAB):/tftpboot/
	@echo rsync -avn pxelinux.cfg/ $(SSH_PREPLAB):/tftpboot/pxelinux.cfg/

# deploy all initramfs's from bemol to faraday
deploy:
	ssh $(SSH_INFRA) \
	 "(cd /tftpboot; rsync -avn $(SSH_PREPLAB):/tftpboot/initramfs\* .)"

# push the script to run on the frisbeeimage specialized VM
BUILD=frisbeeimage.pl.sophia.inria.fr
BUILD_SSH=root@$(BUILD)

build:
	+$(RSYNC) -av frisbeeimage.sh pxe-init $(BUILD_SSH):/build/
	ssh $(BUILD_SSH) "cd /build; ./frisbeeimage.sh"

X = --exclude *~ --exclude default

config-pxelinux:
	+$(RSYNC) -av pxe-run.sh qemu-ifup root@boxtops.pl.sophia.inria.fr:/vservers/pxelinux/
	+$(RSYNC) -av $(X) pxelinux.cfg/ root@boxtops.pl.sophia.inria.fr:/vservers/pxelinux/tftpboot/pxelinux.cfg/

config-bemol:
	+$(RSYNC) -av $(X) pxelinux.cfg/ root@bemol.pl.sophia.inria.fr:/tftpboot/pxelinux.cfg/

config-faraday:
	+$(RSYNC) -av $(X) pxelinux.cfg/ root@faraday.inria.fr:/tftpboot/pxelinux.cfg/
