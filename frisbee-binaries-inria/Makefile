# retrieve locally-rebuilt frisbee binaries

BUILD_SSH=root@frisbee.pl.sophia.inria.fr

FRISBEE_DIR=/build/emulab-stable/clientside/os/frisbee.redux
FRISBEE_BINS=frisbee,frisbee.debug,frisbeed,frisbeed.debug,frisupload,frisupload.debug

IMAGEZIP_DIR=/build/emulab-stable/clientside/os/imagezip
IMAGEZIP_BINS=imagedump,imageunzip,imagezip

fetch:
	rsync -av $(BUILD_SSH):$(FRISBEE_DIR)/'{$(FRISBEE_BINS)}' ./
	rsync -av $(BUILD_SSH):$(IMAGEZIP_DIR)/'{$(IMAGEZIP_BINS)}' ./
