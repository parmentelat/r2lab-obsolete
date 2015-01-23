OMF_SSH=root@faraday.inria.fr

all: configure 

push: json-push nagios-push

.PHONY: all push

####################
configure: configure.py fit.json

fit.json fit-nagios-nodes.cfg: configure.py fit.csv 
	configure.py fit.csv

.PHONY: configure

####################
clean:
	rm -f fit.json fit-nagios-nodes.cfg fit-nagios-groups.cfg

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
