#!/bin/bash

CODEDIR=/root/fitsophia/website/sidecar
LOG=/var/log/sidecar.log

case $1 in
    start)
	cd $CODEDIR
	nohup node sidecar.js > $LOG 2>&1 &
	echo started
    ;;
    stop)
	pkill node && echo stopped
    ;;
    status)
	ps $(pgrep node)
    ;;
    *)
	echo unknown subcommand $1
	exit 1
	;;
esac
