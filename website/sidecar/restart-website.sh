#!/bin/bash

case $(hostname) in
    faraday*)
	command=monitor;;
    r2lab*)
	command=sidecar;;
    *)
	echo Unknown host $(hostname); exit 1;;
esac

LOG=/var/log/$command.log

cd /root/fitsophia
git reset --hard HEAD >> $LOG
./auto-update.sh

$command.sh stop >> $LOG
sleep 1
$command.sh start >> $LOG
