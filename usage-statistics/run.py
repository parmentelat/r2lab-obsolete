#!/usr/bin/env plcsh
# -*- coding: utf-8 -*-

#
# 20 novembre 2017
#
# ce script est conçu pour être lancé sur r2labapi
# dans usage-statistics
# dans lequel j'ai retrouvé des fichiers .json qui dataient de 2017-02-06
#
# comme le contenu de la db plc en novembre semble
# moins grand que ce qu'on avait en février, 
# dans l'urgence je bricole ce script
# qui merge le contenu de ces deux sources
#
# bref tout ça reste trè améliorable...

from __future__ import print_function, division

import time
import json

wire_timeformat = "%Y-%m-%dT%H:%M:%Z"

def human_readable(epoch):
    return time.strftime(wire_timeformat, time.gmtime(epoch))
#alias
hr = human_readable

def slice_name(slice_id, slice_names):
    try:
        return slice_names[slice_id]
    except:
        return "{} (removed)".format(slice_id)

def str_lease(lease, slice_names):
    return \
        "LEASE {:04d} by slice {} duration {}' from {}"\
        .format(lease['lease_id'], slice_name(lease['slice_id'], slice_names),
                (lease['t_until'] - lease['t_from'])//60,
                hr(lease['t_from']))


blacklist = ['auto_', 'nightly', 'maintenance', 'tutorial']
def relevant(lease, slice_names):
    name = slice_name(lease['slice_id'], slice_names)
    return not any(skip in name for skip in blacklist)

def display_items(leases, slices, persons):
    slice_names = { slice['slice_id'] : slice['name'] for slice in slices}

    # cleanup
    leases = [lease for lease in leases if relevant(lease, slice_names)]

    persons.sort(key=lambda p:p['person_id'])
    leases.sort(key=lambda l:l['t_from'])

    # le début du monde
    start = leases[0]['t_from']
    
    print(10*'=', "{} PERSONS".format(len(persons)))
    for person in persons:
        print("{:03d}: {}".format(person['person_id'], person['email']))
    print(10*'=', "{} SLICES".format(len(slices)))
    for slice in slices:
        print(slice['name'], "->", slice['person_ids'])
    print(10*'=', "{} LEASES".format(len(leases)))
    for lease in leases:
        print(str_lease(lease, slice_names))
        

    # compute total time
    total = sum(lease['t_until'] - lease['t_from'] for lease in leases)
    hours = total // 3600
    days = hours // 24
    print("total time: {}s - {} hours - {} days"\
          .format(total, hours, days))

    # le taux global
    since_start = time.time() - start
    rate = total / since_start

    # ramené aux heures ouvrables
    ouvrable = (5 * (19-9)) / (7 * 24)
    rate_ouvrable = rate / ouvrable

    print("taux utilisation: {:%}, {:%} ouvrable".format(rate, rate_ouvrable))
    
####################
# merge 2 lists of objects
def merge(objs1, objs2, key):
    keys1 = { obj[key] for obj in objs1 }
    keys2 = { obj[key] for obj in objs2 }

    new_keys = keys2 - keys1
    index2 = { obj[key]: obj for obj in objs2 }

    merged = objs1[:]
    merged += [ index2[key] for key in new_keys]

    return merged
                 

def forensics(date="2017-02-06"):
    def read_type(type):
        with open("{}.json.{}".format(type, date)) as feed:
            return json.loads(feed.read())
    items = [read_type(type) for type in ("leases", "slices", "persons")]
    print(30*'=', "forensics", date)
    display_items (*items)
    return items

channel = sys.stdout

with open("FORENSICS", "w") as sys.stdout:
    old_items = forensics()

def show_db():
    def read_type(type):
        methodname = "Get" + type.capitalize()
        query_method = getattr(shell, methodname)
        return query_method()
    items = [read_type(type) for type in ("leases", "slices", "persons")]
    print(30*'=', "current")
    display_items (*items)
    return items

with open("STATS", "w") as sys.stdout:
    current_items = show_db()

l1, s1, p1 = old_items
l2, s2, p2 = current_items

l3 = merge(l1, l2, 'lease_id')
s3 = merge(s1, s2, 'slice_id')
p3 = merge(p1, p2, 'person_id')
    
def show_all(leases, slices, persons):
    print(30*'=', "merged")
    display_items (leases, slices, persons)

with open("ALL", "w") as sys.stdout:
    show_all(l3, s3, p3)
    

