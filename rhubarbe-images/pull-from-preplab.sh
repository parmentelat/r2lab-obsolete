#!/bin/bash

this=$(basename $0)

repo=/var/lib/rhubarbe-images
preplab=bemol.pl.sophia.inria.fr

hostname | grep -q faraday || { echo "Must run on faraday"; exit 1; }

rsync "$@" -av --delete --exclude $this --exclude archive --exclude \*.log --exclude root-node\* --exclude saving\* $preplab:$repo/ $repo/ 

