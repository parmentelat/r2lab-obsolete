# set of convenience tools to be used on the nodes
# 
# we start with oai-oriented utilities
# on these images, we have a symlink
# /root/.bash_aliases
# that point at
# /root/r2lab/infra/userenv/nodes.sh
# 
#

available=""


git_repos="/root/r2lab /root/openair-cn /root/openairinterface5g"

##########
available="$available gitup"
function gitup() {
    [[ -n "$@" ]] && repos="$@" || repos="$git_repos"
    for repo in $repos; do
	[ -d $repo ] || continue;
	echo "========== Updating $repo"
	cd /root/r2lab
	git pull
	cd - >& /dev/null
    done
}

# reload this file after a gitup
available="$available bashrc"
function bashrc() { echo "Reloading ~/.bashrc"; source ~/.bashrc; }

# update and reload
available="$available refresh"
function refresh() { gitup /root/r2lab; bashrc; }

##########
available="$available check_hostname"
function check_hostname() {
    # when hostname is correctly set, e.g. fit16
    fitid=$(hostname)
    id=$(sed -e s,fit,, <<< $fitid)
    origin="from hostname"
    if [ "$fitid" == "$id" ]; then
	# sample output
	#inet 192.168.3.16/24 brd 192.168.3.255 scope global control
	id=$(ip addr show control | \
		    grep 'inet '| \
		    awk '{print $2;}' | \
		    cut -d/ -f1 | \
		    cut -d. -f4)
	fitid=fit$id
	origin="from ip addr show"
	echo "Forcing hostname to be $fitid" >&2-
	hostname $fitid
    fi
    echo "Using id=$id and fitid=$fitid - $origin" >&2-
    echo $id
}    


available="$available oai-gw"
alias oai-gw=/root/r2lab/infra/user-env/oai-gw.sh

available="$available oai-enb"
alias oai-enb=/root/r2lab/infra/user-env/oai-enb.sh



function help() { echo Available commands; echo "$available"; }
