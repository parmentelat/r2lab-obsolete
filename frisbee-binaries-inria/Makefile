# retrieve locally-rebuilt frisbee binaries

####################
BUILD_SSH=root@frisbee.pl.sophia.inria.fr

FRISBEE_DIR=/build/emulab-stable/clientside/os/frisbee.redux
FRISBEE_BINS=frisbee,frisbee.debug,frisbeed,frisbeed.debug,frisupload,frisupload.debug

IMAGEZIP_DIR=/build/emulab-stable/clientside/os/imagezip
IMAGEZIP_BINS=imagedump,imageunzip,imagezip

fetch:
	rsync -av $(BUILD_SSH):$(FRISBEE_DIR)/'{$(FRISBEE_BINS)}' ./
	rsync -av $(BUILD_SSH):$(IMAGEZIP_DIR)/'{$(IMAGEZIP_BINS)}' ./

####################
INAME=bemol
INFRA=$(INAME).pl.sophia.inria.fr
INFRA_SSH=root@$(INFRA)

# install this new stuff right into the server side
push-server:
	rsync -av frisbeed $(INFRA_SSH):/usr/sbin

####################
# installing on a node means updating an initramfs image
# this area on bemol is dedicated to that

UNWRAP_SSH=root@bemol.pl.sophia.inria.fr
UNWRAP_DIR=/root/images/unwrap-initramfs-omf6-newfrisbee
# do not push frisbeed on the node, this is not needed
UNWRAP_SBINS = frisbee
UNWRAP_BINS  = imagedump imagezip imageunzip

push-image:
	rsync -av $(UNWRAP_SBINS) $(UNWRAP_SSH):$(UNWRAP_DIR)/usr/sbin/
	rsync -av $(UNWRAP_BINS) $(UNWRAP_SSH):$(UNWRAP_DIR)/usr/bin/

wrap-image:
	ssh $(UNWRAP_SSH) \
	"(cd $(UNWRAP_DIR); find . | cpio -H newc -o | gzip -9 > /tftpboot/initramfs-omf6.igz.newfrisbee)"

