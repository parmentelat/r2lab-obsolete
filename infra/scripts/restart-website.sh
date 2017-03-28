#!/bin/bash
###
# this utility script is cron'ed to run every morning at 6:00 on both faraday and r2lab
#

LOG=/var/log/restart-website.log

#### depending on which host:
case $(hostname) in
    faraday*)
	GIT_REPOS=/root/r2lab
	;;
    r2lab*)
	GIT_REPOS="/root/r2lab"
	;;
    *)
	echo Unknown host $(hostname); exit 1;;
esac

#### updates the contents of selected git repos
for git_repo in $GIT_REPOS; do
    cd $git_repo
    git reset --hard HEAD >> $LOG 2>&1
    git pull >> $LOG 2>&1
done

cd

#### depending on which host:
case $(hostname) in
    faraday*)
	systemctl restart monitor
	systemctl restart monitorphones
	;;
    r2lab*)
	make -C /root/r2lab/r2lab.inria.fr publish >> $LOG 2>&1
	systemctl restart sidecar
	systemctl restart httpd
	;;
esac

