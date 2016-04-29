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

available="$available gitup"
function gitup() {
    for repo in $git_repos; do
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

available="$available oai-gw"
alias oai-gw=/root/r2lab/rhubarbe-images/oai-gw.sh

available="$available oai-enb"
alias oai-enb=/root/r2lab/rhubarbe-images/oai-enb.sh

function help() { echo Available commands; echo "$available"; }
