# default is for the production deployment
OMF_SSH  = root@faraday.inria.fr
OMF_DIR  = /root/omf_sfa
OMF_NAME = fit

# see the prep-* targets
PREP_OMF_SSH  = root@bemol.pl.sophia.inria.fr
PREP_OMF_DIR  = /root/omf_sfa
PREP_OMF_NAME = fit-prep

# a convenience
PREP_MAKE = $(MAKE) OMF_SSH=$(PREP_OMF_SSH) OMF_DIR=$(PREP_OMF_DIR) OMF_NAME=$(PREP_OMF_NAME)

# see AA-README.md

all: configure 

faraday: json infra nagios
faraday-json: json

.PHONY: all faraday faraday-json

SCRIPT = configure.py
SOURCE = fit.csv
BYPRODUCTS = $(OMF_NAME).json $(OMF_NAME).dnsmasq $(OMF_NAME).hosts fit-nagios-nodes.cfg fit-nagios-groups.cfg

# once everything has been redone, this target pushes everything, and commits to git
fullmonty: configure
	@echo "Enter git comment for these changes (one line) "; read comment; git commit -m "$comment"
	git push
	$(MAKE) json infra nagios


# if you've imported the csv file from google spreadsheet
# and this ends up in your ~/Downloads directory
import:
	mv ${HOME}/Downloads/"00-FIT nodes - Feuille 1.csv" fit.csv

.PHONY: fullmonty import
####################
configure: $(BYPRODUCTS)

$(BYPRODUCTS): $(SCRIPT) $(SOURCE)
	$(SCRIPT) $(SOURCE)

.PHONY: configure

####################
clean:
	rm -f $(BYPRODUCTS)

.PHONY: clean

####################
json-push: $(OMF_NAME).json
	rsync -a inject-json.sh $(OMF_NAME).json $(OMF_SSH):$(OMF_DIR)
	ssh $(OMF_SSH) $(OMF_DIR)/inject-json.sh $(OMF_NAME)

json: json-push

.PHONY: json-push json

####################
infra-push: $(OMF_NAME).dnsmasq $(OMF_NAME).json
	rsync -a $(OMF_NAME).dnsmasq $(OMF_SSH):/etc/dnsmasq.d/testbed.conf
	rsync -a $(OMF_NAME).hosts $(OMF_SSH):/etc/hosts

infra-restart:
	ssh $(OMF_SSH) service dnsmasq restart

infra: infra-push infra-restart

.PHONY: infra-push infra-restart infra

####################
# this one makes sense only for faraday
nagios-push: fit-nagios-static.cfg fit-nagios-nodes.cfg fit-nagios-groups.cfg
	rsync -a fit-nagios*.cfg $(OMF_SSH):/etc/nagios3/conf.d

nagios-restart:
	ssh $(OMF_SSH) service nagios3 restart

nagios: nagios-push nagios-restart

.PHONY: nagios-push nagios-restart nagios

####################
TOOLS = display-db.py plugin-onoff.py

tools:
	rsync -av $(TOOLS) $(OMF_SSH):/usr/bin

####################
# refreshing the bemol deployment
# the --prep-lab option creates files named fit-prep*

prep-files:
	configure.py --prep-lab

prep-push:
	$(PREP_MAKE) json infra

bemol: prep-files prep-push

bemol-tools:
	$(PREP_MAKE) tools

.PHONY: prep-files prep-push bemol bemol-tools

####################
