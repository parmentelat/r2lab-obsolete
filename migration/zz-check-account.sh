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
    -v|--verbose)   shift; verbose=true;;
esac

ACCOUNT=$1; shift

function verbose-echo() {
    [ -n "$verbose" ] && echo "$@"
}

##########
# use shortcuts from ../user-env/faraday.sh
( cd /root/r2lab/; git pull )
source /root/r2lab/infra/user-env/faraday.sh

cd /tmp

verbose-echo retrieving details for account $ACCOUNT in ACCOUNT
$CURL --silent $RU/accounts?name=$ACCOUNT > ACCOUNT 2> /dev/null

if [ -d /home/$ACCOUNT ]; then
    echo /home/$ACCOUNT already present - preserved
else
    echo "Creating account $ACCOUNT"
    useradd --create-home --shell /bin/bash $ACCOUNT
fi

#################### retrieving authorized keys

verbose-echo retrieving all keys in KEYS
$CURL --silent $RU/keys > KEYS

cat << FIN > parse.py
import json
def parse_omf(inputname, key):
    try:
        with open(inputname) as feed:
#            print("Parsing file {}".format(inputname))
            return json.loads(feed.read())['resource_response'][key]
    except Exception as e:
        print("Could not parse {} -- {}".format(inputname, e))
        exit(1)
FIN

cat << FIN > pass1.py
#!/usr/bin/env python3
from parse import parse_omf

ACCOUNT = parse_omf("ACCOUNT", 'resource')

###
account_users = ACCOUNT['users']
for user in account_users:
#    print("located user {}".format(user['urn']))
    print(user['uuid'])

FIN

cat << FIN > pass2.py
#!/usr/bin/env python3
from parse import parse_omf

import sys
user_uuids = sys.argv[1:]

for user_uuid in user_uuids:
    keys = parse_omf("{}.keys".format(user_uuid),
                       "resources")
    for key in keys:
        print(key['user_id'])
FIN

cat << FIN > pass3.py
#!/usr/bin/env python3
from parse import parse_omf

import sys
user_ids = set(int(arg) for arg in sys.argv[1:])

keys = parse_omf("KEYS", "resources")

for key in keys:
   if key['user_id'] in user_ids:
      print(key['ssh_key'])

FIN

user_uuids=$(python3 pass1.py)

if [ -z "$user_uuids" ] ; then
    echo "ERROR - cannot find anything about account $ACCOUNT - bailing out"
    exit 1
fi

verbose-echo user_uuids=$user_uuids

for user_uuid in $user_uuids; do
    verbose-echo retrieving keys for user $user_uuid in $user_uuid.keys
    $CURL --silent $RU/users/$user_uuid/keys > $user_uuid.keys
done

key_user_ids=$(python3 pass2.py $user_uuids)

verbose-echo key_user_ids=$key_user_ids

# this sentence generates the authorized_keys for that user
python3 pass3.py $key_user_ids > $ACCOUNT.authorized_keys

auth=/home/$ACCOUNT/.ssh/authorized_keys

if [ ! -f $auth ]; then
    echo "Creating $auth"
    mkdir -p /home/$ACCOUNT/.ssh
    cp $ACCOUNT.authorized_keys $auth
else
    if ! diff $ACCOUNT.authorized_keys $auth ; then
	echo Difference found in authorized_keys
	echo -n 'want to replace ? [y]/n ? '
	read answer
	case $answer in
	    *n*|*N*)   echo skipped;;
	    *)         echo replacing; mv -f $ACCOUNT.authorized_keys $auth ;;
	esac
    else
	echo authorized_keys already OK - left as-is
    fi
fi
       
chmod 700 /home/$ACCOUNT/.ssh
chmod 600 $auth
chown -R $ACCOUNT:$ACCOUNT /home/$ACCOUNT/.ssh
