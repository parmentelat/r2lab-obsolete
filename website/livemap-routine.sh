# Install: keychain
# 		this is to ensure send the ssh key trougth nepi command line
# Execute: keychain ~/.ssh/id_rsa and keychain ~/.ssh/id_rsa.pub
#	This sh file is called from the task schedule in crontab (crontab -l / crontab -e).

/usr/bin/keychain $HOME/.ssh/id_rsa.pub
#source $HOME/.keychain/$LOCALHOST-sh
source $HOME/.keychain/pacify-sh
# Place the routine to execute or use the make file
# Logs are at:  /var/log/livemap-routine.log
# Place at crontab: 00 00 * * * <complete_path_to>/website/livemap-routine.sh >> /var/log/livemap-routine.log 2>&1
#cd /home/mzancana/Inria/fitsophia/website/; make full_and_nepiall
