#!/bin/bash
###
# this utility script is called every 10 minutes through cron on both faraday and r2lab
# 

GIT_REPO=/root/fitsophia

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

$command.sh stop >> $LOG 2>&1 
sleep 1
$command.sh start >> $LOG 2>&1


if [ -n "$run_publish" ]; then
    make -C $GIT_REPO/website install >> $LOG 2>&1
fi
