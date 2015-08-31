########## contents
ALL_MDS = index.md overview.md tuto-*md events.md topology.md hardware.md tools.md 

ALL_MEDIAS = *.png
ALL_PYTHONS = ../nepi_scripts/r2lab_testbed*.py


########## default target
all: preview-local

preview_and_nepiall: prepare index meta nepi_all topology convert resources
full_and_nepiall: prepare index meta nepi_all topology convert resources publish

preview: prepare index meta topology convert resources
full: prepare index meta topology convert resources publish

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

##############################
# Nodes functions
##############################

# check all nepi
nepi_all: nepi_alive nepi_answer nepi_status nepi_info

# load ubuntu 1410 at the nodes
nepi_load-u1410:
	python node_helper.py -A load-u1410 -N fit10,fit26 -U root -i ~/.ssh/id_rsa.pub -g faraday.inria.fr -u mario || (echo "command fail $$?"; exit 1)

# load ubuntu 1410 at the nodes
nepi_load-u1504:
	python node_helper.py -A load-u1504 -N fit10,fit26 -U root -i ~/.ssh/id_rsa.pub -g faraday.inria.fr -u mario || (echo "command fail $$?"; exit 1)

# load ubuntu 1410 at the nodes
nepi_load-f21:
	python node_helper.py -A load-f21 -N fit10,fit26 -U root -i ~/.ssh/id_rsa.pub -g faraday.inria.fr -u mario || (echo "command fail $$?"; exit 1)

# check the availability of the nodes
nepi_alive:
	python node_helper.py -A alive -N all -U root -i ~/.ssh/id_rsa.pub -g faraday.inria.fr -u mario || (echo "command fail $$?"; exit 1)

# check the answer of the nodes
nepi_answer:
	python node_helper.py -A answer -N all -U root -i ~/.ssh/id_rsa.pub -g faraday.inria.fr -u mario || (echo "command fail $$?"; exit 1)

# check the status of the nodes
nepi_status:
	python node_helper.py -A status -N all -U root -i ~/.ssh/id_rsa.pub -g faraday.inria.fr -u mario || (echo "command fail $$?"; exit 1)

# check the status of the nodes
nepi_info:
	python node_helper.py -A info -N fit10,fit26,fit12,fit18 -U root -i ~/.ssh/id_rsa.pub -g faraday.inria.fr -u mario|| (echo "command fail $$?"; exit 1)

temp:
	eval 'ssh-agent'
	#source $HOME/.keychain/$HOSTNAME-sh

temp_st: temp nepi_status
################################

# compile topology informatios  by Nepi check
topology:
	@[ -d markdown ] || mkdir markdown
	./topology.py

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
