########## contents
ALL_MDS = index.md overview.md tuto-*md events.md topology.md hardware.md tools.md 

ALL_MEDIAS = *.png
ALL_PYTHONS = ../nepi_scripts/r2lab_testbed*.py


########## default target
all: preview-local

preview: prepare index meta convert resources
full: prepare index meta convert resources publish

.PHONY: all preview full prepare index meta convert publish 

########## global vars
PUBLISH_HOST = root@r2lab.inria.fr
PUBLISH_PATH = /var/www/html
PUBLISH_RSYNC = $(PUBLISH_HOST):$(PUBLISH_PATH)/

# I am using the custom-made 'r2lab' layout
# which was 'exported' (copied) from markdown-styles' 'bootstrap3' 

LAYOUT = ./r2lab-layout

##########
prepare:
	@[ -d markdown ] || mkdir markdown
	rsync -av --delete --relative $(ALL_MDS) markdown

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

resources:
	rsync -av $(ALL_PYTHONS) $(ALL_MEDIAS) html/

publish:
	rsync -av --delete html/ $(PUBLISH_RSYNC)

debug:
	echo ALL_MDS=$(ALL_MDS)

clean:
	rm -rf markdown html

############################## 
# see also AA-local-markdown.md
# for using our own brew of markdown-styles until this gets merged upstream
convert-local:
	NODE_PATH=$HOME/git/markdown-styles/lib:/usr/local//lib/node_modules/markdown-styles/node_modules \
	../../markdown-styles/bin/generate-md --layout ./r2lab-layout --input markdown --output html

preview-local: prepare index meta convert-local resources
full-local: prepare index meta convert-local resources publish

.PHONY: convert-local preview-local full-local
