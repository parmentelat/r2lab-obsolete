#!/bin/bash

CODEDIR=/root/r2lab/sidecar
DATADIR=/var/lib/sidecar
LOG=/var/log/sidecar.log

mkdir -p $DATADIR

function action() {
    verb=$1; shift
    case $verb in
	start)
	    cd $CODEDIR
	    nohup node sidecar.js "$@" >> $LOG 2>&1 &
	    echo started
	    ;;
	stop)
	    pids=$(pgrep node)
	    if [ -n "$pids" ] ; then
		pkill node && echo stopped
	    else
		echo not running
	    fi
	    ;;
	status)
	    pids=$(pgrep node)
	    if [ -z "$pids" ] ; then
		echo No instance of node running
	    else
		ps $pids
	    fi
	    ;;
	restart)
	    action stop
	    action start
	    ;;
	*)
	    echo unknown subcommand $1
	    exit 1
	    ;;
    esac
}

action "$@"
