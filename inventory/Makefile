TOOL = configure.py

OMF_SSH=root@faraday.inria.fr

all: run

push: json-push nagios-push

.PHONY: all run push

####################
run: fit.json

fit.json fit-nagios-nodes.cfg: $(TOOL) fit.csv 
	$(TOOL) fit.csv

####################
json-push: fit.json
	./inject-json.sh

json: json-push

.PHONY: json-push json

####################
nagios-push: fit-nagios-nodes.cfg fit-nagios-static.cfg
	rsync -a fit-nagios*.cfg root@faraday.inria.fr:/etc/nagios3/conf.d

nagios-restart:
	ssh root@faraday.inria.fr service nagios3 restart

nagios: nagios-push nagios-restart

.PHONY: nagios-push nagios-restart nagios

####################
UTILS = display_db.py

utils:
	rsync -av $(UTILS) $(OMF_SSH):/usr/bin
