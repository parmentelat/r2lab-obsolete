#!/bin/bash
# this is to work around omf-sfa failing to create users
# once users have created their account and slice, we end
# up with a missing user on the faraday side
#
# Usage: $0 expected_user_name
# e.g.
# user-finish.sh onelab.inria.anas_first.ping_example
#
# this script will
# (*) verify that name is known to omf-sfa (and exit if not)
# (*) create a Unix account if not already present
# (*) check its authorized_keys

verbose=""
case "$1" in
    -a|--all)   shift; arg="--all"; ;;
esac

verbose=true
function verbose-echo() {
    [ -n "$verbose" ] && echo "$@"
}

##########
# use shortcuts from ../user-env/faraday.sh
# ( cd /root/r2lab/; git pull )
source /root/r2lab/infra/user-env/faraday.sh

verbose-echo "retrieving all accounts in ACCOUNTS"
$CURL --silent $RU/accounts > ACCOUNTS 2> /dev/null

verbose-echo "retrieving all users in USERS"
$CURL --silent $RU/users > USERS 2> /dev/null

verbose-echo retrieving all keys in KEYS
$CURL --silent $RU/keys > KEYS

######################################## 
./migrate.py dump

########################################
for user_uuid in $(cat USER-uuids); do
    verbose-echo retrieving keys for user $user_uuid in $user_uuid.keys
    $CURL --silent $RU/users/$user_uuid/keys > $user_uuid.keys
done

