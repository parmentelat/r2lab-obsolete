all: prepare convert publish
.PHONY: all prepare convert publish 

PUBLISH_HOST = root@r2lab.pl.sophia.inria.fr
PUBLISH_PATH = /var/www/html
PUBLISH_RSYNC = $(PUBLISH_HOST):$(PUBLISH_PATH)/

# this one apparently needs more work
#LAYOUT = bootstrap3

LAYOUT = mixu-bootstrap-2col


# temporary:
# consider all the md files we have under git

ALL_GITS = $(shell git ls-files ../)
ALL_MDS = $(filter %.md, $(ALL_GITS))


prepare:
	@[ -d markdown ] || mkdir markdown
	rsync -av --delete $(ALL_MDS) markdown

convert: 
	@[ -d html ] || mkdir html
	./index.py
	generate-md --layout $(LAYOUT) --input markdown --output html

publish:
	rsync -av --delete html/ $(PUBLISH_RSYNC)

debug:
	echo ALL_MDS=$(ALL_MDS)

clean:
	rm -rf markdown html
