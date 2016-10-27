# the script to apply git changes in production site r2lab.inria.fr
# invoked every 10 minutes from cron through restart-website.sh
# which does make install

########## force both infra boxes to use latest commit
infra:
	apssh -u root -t faraday.inria.fr -t r2lab.inria.fr /root/r2lab/infra/scripts/restart-website.sh

.PHONY: infra
