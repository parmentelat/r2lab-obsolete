# the script to apply git changes in production site r2lab.inria.fr
# invoked every 10 minutes from cron through restart-website.sh
# which does make install

PUBLISH-PATH = /var/www/r2lab.inria.fr
EXCLUDES = .git
RSYNC-EXCLUDES = $(foreach exc,$(EXCLUDES), --exclude $(exc))

########## mirror this contents 
publish:
	rsync -av $(RSYNC-EXCLUDES) --delete --delete-excluded ./ $(PUBLISH-PATH)/

########## restart apache on r2lab.inria.fr
# maybe not strictly necessary when the python code is stable
# but that won't hurt us while developing as frequent changes
# are to be expected
apache:
	systemctl restart httpd

# 
install: publish apache

.PHONY: publish apache install

########## force both infra boxes to use latest commit
infra:
	apssh -l root -t faraday.inria.fr -t r2lab.inria.fr /root/r2lab/infra/scripts/restart-website.sh

.PHONY: infra

##########
tags:
	git ls-files | egrep -v '\.(pdf|png|jpg)' | xargs etags

.PHONY: tags
