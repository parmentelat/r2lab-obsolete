# retrieve locally-rebuilt frisbee binaries

BUILD_SSH=root@frisbee.pl.sophia.inria.fr

FRISBEE_DIR=/build/emulab-stable/clientside/os/frisbee.redux
FRISBEE_BINS=frisbee,frisbee.debug,frisbeed,frisbeed.debug,frisupload,frisupload.debug

IMAGEZIP_DIR=/build/emulab-stable/clientside/os/imagezip
IMAGEZIP_BINS=imagedump,imageunzip,imagezip

fetch:
	rsync -av $(BUILD_SSH):$(FRISBEE_DIR)/'{$(FRISBEE_BINS)}' ./
	rsync -av $(BUILD_SSH):$(IMAGEZIP_DIR)/'{$(IMAGEZIP_BINS)}' ./

INFRA=bemol.pl.sophia.inria.fr
INFRA_SSH=root@$(INFRA)

# install this new stuff right into the server side
push-server:
	rsync frisbeed $(INFRA_SSH):/usr/sbin

# to install on a node is an entirely different matter
# need to create an entire initramfs...
