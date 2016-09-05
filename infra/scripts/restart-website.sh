#!/bin/bash
###
# this utility script is called every 10 minutes through cron on both faraday and r2lab
#

GIT_REPO=/root/r2lab
LOG=/var/log/$command.log

#### updates the contents of /root/r2lab on both boxes
cd $GIT_REPO
git reset --hard HEAD >> $LOG 2>&1
./auto-update.sh

#### depending on which host:
case $(hostname) in
    faraday*)
	systemctl restart monitor
	;;
    r2lab*)
	systemctl restart sidecar
	make -C $GIT_REPO/r2lab.inria.fr install >> $LOG 2>&1
	;;
    *)
	echo Unknown host $(hostname); exit 1;;
esac

