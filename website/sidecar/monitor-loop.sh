#!/bin/bash
# to be run in faraday

hostname | grep -q faraday || {
    echo $0 is designed for faraday only
    exit 1
    }

# details on where to put stuff
remote=root@r2lab.pl.sophia.inria.fr
remote_dest=/var/lib/sidecar/news.json

# nodes can be specified on the command line, defaults to all nodes

# xxx  todo - add option to specify delay
delay = 5


cd /root/fitsophia/website/sidecar
# just in case
ssh $remote mkdir -p $(dirname $remote_dest)

while true; do
    echo ==================== Running script
    ./monitor.py -v -o monitor.json "$@"
    echo ==================== Installing result
    # a bit surprisingly, pushing with rsync won't do it, it feels like it uses tricks that bypass fs.watch
    cat monitor.json | ssh $remote cat \> $remote_dest
    sleep $delay
done
