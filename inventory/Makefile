# default is for the production deployment
OMF_SSH  = root@faraday.inria.fr
OMF_DIR  = /root/omf_sfa
OMF_NAME = r2lab

RHUBARBE_INVENTORY = /etc/rhubarbe/inventory.json

# see the prep-* targets
PREP_OMF_SSH  = root@bemol.pl.sophia.inria.fr
PREP_OMF_DIR  = /root/omf_sfa
PREP_OMF_NAME = r2lab-prep

# see AA-README.md

all: configure 

publish: configure json infra nagios

.PHONY: all publish

SCRIPT = configure.py
SOURCE = r2lab.map

define byproducts
$(1)-omf.json $(1)-rhubarbe.json $(1).dnsmasq $(1).hosts 
endef

PRODUCTS         = $(call byproducts,$(OMF_NAME))
BEMOL-PRODUCTS   = $(call byproducts,$(PREP_OMF_NAME))

# once everything has been redone, this target pushes everything, and commits to git
fullmonty: configure
	@echo "Enter git comment for these changes (one line) "; read comment; git commit -m "$$comment"
	git push
	$(MAKE) configure json infra nagios


.PHONY: fullmonty
####################
configure: $(PRODUCTS)
$(PRODUCTS) r2lab-nagios-nodes.cfg r2lab-nagios-groups.cfg: $(SCRIPT) $(SOURCE)
	$(SCRIPT) $(SOURCE)

$(BEMOL-PRODUCTS): $(SCRIPT) $(SOURCE)
	$(SCRIPT) -p $(SOURCE)
bemol-configure: $(BEMOL-PRODUCTS)

.PHONY: configure

####################
clean:
	rm -f $(BYPRODUCTS)

.PHONY: clean

####################
json-push: $(OMF_NAME)-omf.json $(OMF_NAME)-rhubarbe.json
	rsync -av $(OMF_NAME)-omf.json inject-omf-json.sh $(OMF_SSH):$(OMF_DIR)
	rsync -av $(OMF_NAME)-rhubarbe.json $(OMF_SSH):$(RHUBARBE_INVENTORY)

json-run:
	@echo -n "Are you sure you want to run inject-omf-json on $(OMF_SSH) (Ctrl-C to abort) ? "; read _
	ssh $(OMF_SSH) $(OMF_DIR)/inject-omf-json.sh $(OMF_NAME)

json: json-push json-run

.PHONY: json json-push json-run

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
nagios-push: r2lab-nagios-static.cfg r2lab-nagios-nodes.cfg r2lab-nagios-groups.cfg
	rsync -a r2lab-nagios*.cfg $(OMF_SSH):/etc/nagios3/conf.d

nagios-restart:
	ssh $(OMF_SSH) service nagios3 restart

nagios: nagios-push nagios-restart

.PHONY: nagios-push nagios-restart nagios

####################
TOOLS = display-db.py plugin-onoff.py

tools:
	rsync -av $(TOOLS) $(OMF_SSH):/usr/bin

####################
# bemol-configure and other similar targets
BEMOL-TARGETS = configure json infra publish

define bemol-target
bemol-$(1): OMF_SSH=$(PREP_OMF_SSH)
bemol-$(1): OMF_DIR=$(PREP_OMF_DIR)
bemol-$(1): OMF_NAME=$(PREP_OMF_NAME)
bemol-$(1): $(1)

prep-$(1): bemol-$(1)

.PHONY: bemol-$(1) prep-$(1)
endef

$(foreach target,$(BEMOL-TARGETS),$(eval $(call bemol-target,$(target))))

bemol: force $(foreach target,$(BEMOL-TARGETS), bemol-$(target))

force:

.PHONY: bemol
