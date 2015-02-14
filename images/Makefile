#

get: get-tftpboot get-images

get-tftpboot:
	rsync -av root@faraday.inria.fr:/tftpboot .

get-images:
	rsync -av root@faraday.inria.fr:/var/lib/omf-images-6 .

.PHONY: get get-tftpboot get-images
