#!/bin/bash
# to be run in faraday

hostname | grep -q faraday || {
    echo $0 is designed for faraday only
    exit 1
    }

# details on where to put stuff
REMOTE_ID=root@r2lab.pl.sophia.inria.fr
REMOTE_DEST=/var/lib/sidecar/news.json
LOCAL_LOG=/var/log/monitor.log

function display() {
    echo $(date '+%m/%d %H:%M:%S') "$@"
}

# nodes can be specified on the command line, defaults to all nodes

# options
delay=3
verbose=

while getopts ":d:" opt; do
    case $opt in
	d)
	    delay=$OPTARG;;
	v)
	    verbose=-v ;;
    esac
done
shift $((OPTIND-1))

cd /root/fitsophia/website/sidecar
# just in case
ssh $REMOTE_ID mkdir -p $(dirname $REMOTE_DEST)

display "Destination is $REMOTE_ID:$REMOTE_DEST" >> $LOCAL_LOG

while true; do
    display probing
    ./monitor.py $verbose -o monitor.json "$@"
    display pushing
    # a bit surprisingly, pushing with rsync won't do it, it feels like it uses tricks that bypass fs.watch
    cat monitor.json | ssh $REMOTE_ID cat \> $REMOTE_DEST
    display sleep $delay s
    sleep $delay
done >> $LOCAL_LOG 2>&1 &
