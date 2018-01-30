#!/bin/bash

repo=/var/lib/rhubarbe-images
preplab=etourdi.pl.sophia.inria.fr

# waterfall model : MUST run on faraday
hostname | grep -q faraday || { echo "Must run on faraday"; exit 1; }

###
command=$(basename $0)

case $command in
    pull*)
	from=$preplab:$repo/
	to=$repo/
	;;
    push*)
	from=$repo/
	to=$preplab:$repo/
	;;
    *)
esac
    
# Thierry - Apr 26 2016 : 
# it is much safer to *NOT* mention --delete
# as images can be saved directly on faraday 
rsync "$@" -av --exclude '*preplab*' --exclude archive\* --exclude \*.log --exclude root-node\* --exclude saving\* $from $to
