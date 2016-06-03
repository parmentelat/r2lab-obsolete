#!/bin/bash
###
# this utility script is called every 10 minutes through cron on both faraday and r2lab
#

GIT_REPO=/root/r2lab

case $(hostname) in
    faraday*)
	command=monitor
	run_publish=""
	;;
    r2lab*)
	command=sidecar
	run_publish=true
	;;
    *)
	echo Unknown host $(hostname); exit 1;;
esac

LOG=/var/log/$command.log

cd $GIT_REPO
git reset --hard HEAD >> $LOG 2>&1
./auto-update.sh

# invoking monitor.sh or sidecar.sh accordingly
# note that monitor.sh comes with rhubarbe
# and sidecar.sh is a symlink manually created in /usr/bin
$command.sh stop >> $LOG 2>&1 
sleep 1
$command.sh start >> $LOG 2>&1

# publish website contents
if [ -n "$run_publish" ]; then
    make -C $GIT_REPO/r2lab.inria.fr install >> $LOG 2>&1
fi
