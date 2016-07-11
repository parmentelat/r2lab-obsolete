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

# for when a remap occurs
# xxx todo : edit /etc/rhubarbe/rhubarbe.conf on bemol to reflect the scope of rhubarbe -a
# xxx todo : tweak faraday.sh so that it gets the default all-nodes from rhubarbe.conf
# for now I do this manually each time
remap: all publish bemol spare-nodes

.PHONY: remap

####################
# march 2016 : no need to redo omf anymore, one single node that never changes
#publish: configure omf rhubarbe infra nagios
publish: configure rhubarbe infra nagios

.PHONY: all publish

SCRIPT = configure.py
SOURCE = r2lab.map

define byproducts
$(1)-omf.json $(1)-rhubarbe.json $(1).dnsmasq $(1).hosts 
endef

PRODUCTS         = $(call byproducts,$(OMF_NAME))
BEMOL-PRODUCTS   = $(call byproducts,$(PREP_OMF_NAME)) r2lab-prep.spare-nodes

####################
configure: $(PRODUCTS)
$(PRODUCTS) r2lab-nagios-nodes.cfg r2lab-nagios-groups.cfg: $(SCRIPT) $(SOURCE)
	python $(SCRIPT) $(SOURCE)

$(BEMOL-PRODUCTS): $(SCRIPT) $(SOURCE)
	python $(SCRIPT) -p $(SOURCE)
bemol-configure: $(BEMOL-PRODUCTS)

.PHONY: configure

####################
clean:
	rm -f $(PRODUCTS) $(BEMOL-PRODUCTS)

.PHONY: clean

####################
omf-push: $(OMF_NAME)-omf.json
	rsync -av $(OMF_NAME)-omf.json inject-omf-json.sh $(OMF_SSH):$(OMF_DIR)

omf-run:
	@echo -n "Are you sure you want to run inject-omf-json on $(OMF_SSH) (Ctrl-C to abort) ? "; read _
	ssh $(OMF_SSH) $(OMF_DIR)/inject-omf-json.sh $(OMF_NAME)

omf: omf-push omf-run

.PHONY: omf omf-push omf-run


rhubarbe-push:  $(OMF_NAME)-rhubarbe.json
	rsync -av $(OMF_NAME)-rhubarbe.json $(OMF_SSH):$(RHUBARBE_INVENTORY)

rhubarbe: rhubarbe-push

.PHONY: rhubarbe rhubarbe-push

####################
infra-push: $(OMF_NAME).dnsmasq $(OMF_NAME).hosts
	rsync -a $(OMF_NAME).dnsmasq $(OMF_SSH):/etc/dnsmasq.d/testbed.conf
	rsync -a $(OMF_NAME).hosts $(OMF_SSH):/etc/hosts

# make sure the leases file gets cleaned up otherwise the new node may
# need to wait for *some time* before it gets served its address
# getting stuff like 192.168.3.251 instead
infra-restart:
	ssh $(OMF_SSH) "service dnsmasq stop; rm -f /var/lib/misc/dnsmasq.leases; service dnsmasq start"

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
# purpose is to tweak /etc/rhubarbe/rhubarbe.conf
# on bemol only
# to reflect the actual spare nodes 
RC = /etc/rhubarbe/rhubarbe.conf
all-spares = $(shell cat r2lab-prep.spare-nodes)

spare-nodes: r2lab-prep.spare-nodes
	ssh root@bemol.pl.sophia.inria.fr \
          sed -i -e 's/all_scope.bemol.*/all_scope.bemol=$(all-spares)/' $(RC)


####################
# bemol-configure and other similar targets
BEMOL-TARGETS = configure rhubarbe infra

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
