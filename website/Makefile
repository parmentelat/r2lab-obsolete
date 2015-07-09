all: prepare index meta convert publish
.PHONY: all prepare index meta convert publish 

PUBLISH_HOST = root@r2lab.inria.fr
PUBLISH_PATH = /var/www/html
PUBLISH_RSYNC = $(PUBLISH_HOST):$(PUBLISH_PATH)/

# I am using the custom-made 'r2lab' layout
# that is available from my fork of markdown-styles on github

LAYOUT = ./r2lab-layout

# this one apparently needs more work
#LAYOUT = bootstrap3
# not too bad but not quite all right either
#LAYOUT = mixu-bootstrap-2col
#LAYOUT = github
#LAYOUT = roryg-ghostwriter
#LAYOUT = mixu-book



# temporary:
# consider all the md files we have under git

GITS = $(shell git ls-files ../)
GIT_MDS = $(filter %.md, $(GITS))

ALL_MDS = index.md overview.md tuto-*md status.md events.md
ALL_MEDIAS = *.png

prepare:
	@[ -d markdown ] || mkdir markdown
	rsync -av --delete $(ALL_MDS) $(ALL_MEDIAS) markdown

# index.py is hard-wired to output in markdown/
index:
	@[ -d markdown ] || mkdir markdown
	./index.py $(ALL_MDS)

# likewise
meta:
	@[ -d markdown ] || mkdir markdown
	./meta.py

convert: 
	generate-md --layout $(LAYOUT) --input markdown --output html

publish:
	rsync -av --delete html/ $(PUBLISH_RSYNC)

debug:
	echo ALL_MDS=$(ALL_MDS)

clean:
	rm -rf markdown html
