OMF_SSH=root@faraday.inria.fr

all: configure 

push: json-push nagios-push

.PHONY: all push

SCRIPT = configure.py
SOURCE = fit.csv
BYPRODUCTS = fit.json fit.dnsmasq fit.hosts fit-nagios-nodes.cfg fit-nagios-groups.cfg

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
json-push: fit.json
	./inject-json.sh

json: json-push

.PHONY: json-push json

####################
infra-push: fit.dnsmasq fit.json
	rsync -a fit.dnsmasq $(OMF_SSH):/etc/dnsmasq.d/testbed.conf
	rsync -a fit.hosts $(OMF_SSH):/etc/hosts

infra-restart:
	ssh $(OMF_SSH) service dnsmasq restart

infra: infra-push infra-restart

.PHONY: infra-push infra-restart infra

####################
nagios-push: fit-nagios-static.cfg fit-nagios-nodes.cfg fit-nagios-groups.cfg
	rsync -a fit-nagios*.cfg $(OMF_SSH):/etc/nagios3/conf.d

nagios-restart:
	ssh $(OMF_SSH) service nagios3 restart

nagios: nagios-push nagios-restart

.PHONY: nagios-push nagios-restart nagios

####################
UTILS = display-db.py plugin-onoff.py

utils:
	rsync -av $(UTILS) $(OMF_SSH):/usr/bin

####################

prep-files:
	configure.py -p

prep-push:
	rsync -av *-prep* root@bemol.pl.sophia.inria.fr:preplab/

prep: prep-files prep-push

.PHONY: prep-files prep-push prep
