#!/bin/bash

this=$(basename $0)

repo=/var/lib/rhubarbe-images
preplab=bemol.pl.sophia.inria.fr

hostname | grep -q faraday || { echo "Must run on faraday"; exit 1; }

case "$1" in
    push|reverse)
	shift
	from=$repo/
	to=$preplab:$repo/
	;;
    *)
	from=$preplab:$repo/
	to=$repo/
	;;
esac
    
# Thierry - Apr 26 2016 : 
# it is much safer to *NOT* mention --delete
# as images can be saved directly on faraday 
rsync "$@" -av --exclude $this --exclude archive --exclude \*.log --exclude root-node\* --exclude saving\* $from $to

