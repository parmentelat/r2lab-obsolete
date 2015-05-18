# workflow is a bit awkward, but
# . we rebuild the new initramfs on bemol where we can try it out
# then we push it back onto faraday
#
# so in short, don't use these targets directly 

SSH_INFRA	= root@faraday.inria.fr

SSH_PREPLAB	= root@bemol.pl.sophia.inria.fr

###
fetch:
	@echo sample fetch command
	@echo rsync -av $(SSH_INFRA):/tftpboot/ ./

fetch-conf:
	@echo sample fetch command
	@echo 'rsync -av $(SSH_INFRA):/tftpboot/\*.conf ./'

###
push:
	@echo "Sample push command"
	@echo rsync -av initramfs-omf6.igz.newfrisbee $(SSH_INFRA):/tftpboot/

# deploy all initramfs's from bemol to faraday
deploy:
	ssh $(SSH_INFRA) \
	 "(cd /tftpboot; rsync -av $(SSH_PREPLAB):/tftpboot/initramfs\* .)"
