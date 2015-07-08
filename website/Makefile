all: prepare index convert publish
.PHONY: all prepare index convert publish 

PUBLISH_HOST = root@r2lab.inria.fr
PUBLISH_PATH = /var/www/html
PUBLISH_RSYNC = $(PUBLISH_HOST):$(PUBLISH_PATH)/

# this one apparently needs more work
LAYOUT = bootstrap3

# not too bad but not quite all right either
#LAYOUT = mixu-bootstrap-2col

#LAYOUT = github
#LAYOUT = roryg-ghostwriter
#LAYOUT = mixu-book



# temporary:
# consider all the md files we have under git

GITS = $(shell git ls-files ../)
GIT_MDS = $(filter %.md, $(GITS))

LOCAL_MDS = $(wildcard *.md)

# set this to true if you want to see all known mds in git as well
# make ALL=true

ifeq ("$(ALL)","")
ALL_MDS = $(LOCAL_MDS)
else
ALL_MDS = $(sort $(GIT_MDS) $(LOCAL_MDS))
endif

prepare:
	@[ -d markdown ] || mkdir markdown
	rsync -av --delete $(ALL_MDS) markdown

index:
	@[ -d html ] || mkdir html
	./index.py $(ALL_MDS)

convert: 
	generate-md --layout $(LAYOUT) --input markdown --output html

publish:
	rsync -av --delete html/ $(PUBLISH_RSYNC)

debug:
	echo ALL_MDS=$(ALL_MDS)

clean:
	rm -rf markdown html
