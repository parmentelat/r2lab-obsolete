#!/usr/bin/env plcsh

keys = GetKeys()
keys_by_id = { key['key_id'] : key for key in keys }

for p in GetPersons():
    email = p['email']
    if len(p['key_ids']) != 2:
        print("{} has {} keys (!=2) - skipping"
              .format(email, len(p['key_ids'])))
        continue
    kid1, kid2 = p['key_ids']
    k1, k2 = keys_by_id[kid1]['key'], keys_by_id[kid2]['key']
    if k1 != k2:
        print("{} has 2 different keys - skipping"
              .format(email))
        continue

    print("MATCH with {} -> deleting key {}".format(email, kid2))
    DeleteKey(kid2)
