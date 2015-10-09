########## contents
ALL_MDS = index.md overview.md tuto-*md tutorial.md status.md hardware.md tools.md blog.md

ALL_PYTHONS = ../nepi_scripts/r2lab_testbed*.py
ALL_PLUGINS = plugins/*.{js,css,html}
ALL_CODES = codes_examples/*.py

########## default target
all: preview

preview: prepare index meta convert resources codes_examples
# this is what is invoked by restart-website.sh that is crontab'ed
install: preview publish

.PHONY: all preview publish install prepare index meta convert resources codes_examples

preview_and_nepiall: prepare index meta nepi_all convert resources
install_and_nepiall: preview_and_nepiall publish

.PHONY: preview_and_nepiall install_and_nepiall

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
	export LC_ALL=en_US.UTF-8; ./index.py $(ALL_MDS)

# likewise
meta:
	@[ -d markdown ] || mkdir markdown
	./meta.py

################################

# compile status informations  by Nepi check
status:
	@[ -d markdown ] || mkdir markdown
	./status.py

# export the codes at codes_examples folder
codes_examples:
	rsync -av $(ALL_CODES) html/codes_examples

convert: 
	generate-md --layout $(LAYOUT) --input markdown --output html

resources:
	rsync -av $(ALL_PYTHONS) html/
	rsync -av $(ALL_PLUGINS) html/plugins

# default is ti publish locally as this runs right from r2lab.inria.fr
publish:
	rsync -av --delete html/ $(PUBLISH_PATH)/

publish-remote:
	rsync -av --delete html/ $(PUBLISH_RSYNC)

debug:
	echo ALL_MDS=$(ALL_MDS)

clean:
	rm -rf markdown html

############################## 
# NOTE - older targets in '-local' are no longer needed
# see also AA-local-markdown.md 



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
	python node_helper.py -A info -N all -U root -i ~/.ssh/id_rsa.pub -g faraday.inria.fr -u mario|| (echo "command fail $$?"; exit 1)

