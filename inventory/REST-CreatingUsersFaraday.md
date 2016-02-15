# GENERAL NOTE

All these commands are for root; in our current setup the root user
has a full pem, so no need to mention the private key:

    # curl -k --cert /root/certificates-omf/user_cert.pem \
        ...

Would then become for a regular user:

    $ curl -k --cert ~/.omf/user_cert.pem --key ~/.omf/user_cert.pkey \
        ...

See help in faraday for env. variables that are defined to hopefully ease this whole thing.

# Get command example
In general you can use GET on `/resources/nodes` (or `/resources/users`, etc.., in plural) to get a list of all the resources of that type. 
You can also use the parameters `name` and `uuid` to list a specific resource (eg `/resources/nodes?name=fit31` or `/resources/nodes?uuid=THE_UUID`), 
as far as possible the uuid should be used instead of the name, because the property name is not unique.

    # curl -k --cert /root/certificates-omf/user_cert.pem \
    -H "Accept: application/json" -H "Content-Type:application/json" \
    -X GET -i https://localhost:12346/resources/users

# Deleting an entry

    # curl -k --cert /root/certificates-omf/user_cert.pem \
    -H "Accept: application/json" -H "Content-Type:application/json" \
    -X DELETE -d '{"uuid":"ACCOUNT_UUID"}'  \
    -i https://localhost:12346/resources/users

# To create a user:
    # curl -k --cert /root/certificates-omf/user_cert.pem \
    -H "Accept: application/json" -H "Content-Type:application/json" \
    -X POST -d '{"name":"USERNAME"}' -i https://localhost:12346/resources/users

# To create an account:
    # curl -k --cert /root/certificates-omf/user_cert.pem \
    -H "Accept: application/json" -H "Content-Type:application/json" \
    -X POST -d '{"name":"ACCOUNT_NAME"}' -i https://localhost:12346/resources/accounts

This will also generate the linux account and all configuration files / certificates.

# To associate a user with an account

You will need the user uuid and the account uuid, you can get them either by the response of the above commands 
or you can use GET on `/resources/users?name=user_name` or `/resources/accounts?name=account_name`

    # curl -k --cert /root/certificates-omf/user_cert.pem \
    -H "Accept: application/json" -H "Content-Type:application/json" \
    -X PUT -d '{"uuid":"ACCOUNT_UUID"}' \
    -i https://localhost:12346/resources/users/USER_UUID/accounts

This will also create the `/home/account_name/.ssh/authorized_keys` file and add all user ssh keys to it.

# To create an ssh key:

    # curl -k --cert /root/certificates-omf/user_cert.pem \
    -H "Accept: application/json" -H "Content-Type:application/json" \
    -X POST -d '{"name":"KEY_NAME","ssh_key":"THE_KEY"}' \
    -i https://localhost:12346/resources/keys

# To associate a user with an ssh key:

    # curl -k --cert /root/certificates-omf/user_cert.pem \
    -H "Accept: application/json" -H "Content-Type:application/json" \
    -X PUT -d '{"uuid":"ACCOUNT_UUID"}' \
    -i https://localhost:12346/resources/users/USER_UUID/accounts

after the update this will also create `/home/account_name/.ssh/authorized_keys` file (for all user accounts) and add all user ssh keys to them.

# Delete and add a user's key

    # $CURL -X DELETE \
    -d '{"uuid":"key_uuid"}' \
    -i https://localhost:12346/resources/users/user_uuid/keys
    
    # $CURL -X PUT \
    -d '{"uuid":"key_uuid"}' \
    -i https://localhost:12346/resources/users/user_uuid/keys
    

# leases 

```
curl -k https://localhost:12346/resources/leases
```

There are 5 statuses for leases "Pending, Accepted, Cancelled, Active, Past"

* Pending means that it couldn't be completed so it does not contain any resources for the moment
* Accepted means that it was created successfully and the corresponding resources have been reserved
* Cancelled means that this lease was cancelled by the user or an admin
* Active means that its timespan has started
* Past means that its timespan has ended


**Notes**

* this returns all leases in the future
* including the active ones, but not the past ones
* when a creation request fails, a 'dummy' lease object does get created in the db and is marked 'pending' (as opposed to being trashed altogether); it has no component attached (at least in the r2lab context)
* and so some care must be taken to ignore such leases
  * one should consider only leases marked as accepted or active provided that they have some component inside. 
* One could think of using something like the following; it's not a good idea; when 'now' is in the middle of a lease lifespan, it is marked 'active' even if is was 'pending' before.

~~```
curl -k https://localhost:12346/resources/leases?status=accepted
```~~

