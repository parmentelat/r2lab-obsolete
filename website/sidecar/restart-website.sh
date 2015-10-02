#!/bin/bash

cd /root/fitsophia
git reset --hard HEAD
./auto-update.sh

case $(hostname) in
    faraday*)
	command=monitor.sh;;
    r2lab*)
	command=sidecar.sh;;
    *)
	echo Unknown host $(hostname); exit 1;;
esac

$command stop
sleep 1
$command start
