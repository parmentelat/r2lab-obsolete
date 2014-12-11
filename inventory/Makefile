TOOL = configure.py

all: run

.PHONY: all run

####################
run: fit.json

fit.json fit-nagios-nodes.cfg: $(TOOL) fit.csv 
	$(TOOL) fit.csv

####################
json-push: fit.json
	rsync -a fit.json root@faraday.inria.fr:/root/inventory

json: json-push

####################
nagios-push: fit-nagios-nodes.cfg fit-nagios-static.cfg
	rsync -a fit-nagios*.cfg root@faraday.inria.fr:/etc/nagios3/conf.d

nagios-restart:
	ssh root@faraday.inria.fr service nagios3 restart

nagios: nagios-push nagios-restart

.PHONY: nagios-push nagios-restart nagios
