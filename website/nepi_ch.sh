# Install: keychain
# 		this is to ensure send the ssh key trougth nepi command line
# Execute: keychain ~/.ssh/id_rsa and keychain ~/.ssh/id_rsa.pub
#	This sh file is called from the task schedule in crontab (crontab -l / crontab -e).

/usr/bin/keychain $HOME/.ssh/id_rsa.pub
#source $HOME/.keychain/$LOCALHOST-sh
source $HOME/.keychain/pacify-sh
cd /home/mzancana/Inria/fitsophia/website/; make full_and_nepiall