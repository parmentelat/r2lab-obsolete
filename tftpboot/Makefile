# workflow is a bit awkward, but
# . we rebuild the new initramfs - aka irfs - on bemol where we can try it out
# then we push it back onto faraday
#
# so in short, don't use these targets directly 

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
