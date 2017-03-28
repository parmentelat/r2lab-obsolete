# R2lab inventory : purpose

This subdir contains various tools for interacting with the `omf_sfa` instance deployed on `faraday.inria.fr`, as well as the various companion tools like `dnsmasq`.

Mainly we maintain a local map in `r2lab.map`; this is where we map physical numbers (i.e. the  on the label that is glued to the node) and logical numbers (the actual location in the room). 

Most of the time of course there is no discrepency; however when a spare node needs to be deployed instead, the testbed needs to be reconfigured.

# Workflow

Here is how to implement a change

## edit `r2lab.map`

Edit `r2lab.map`. Lines starting with a `#` are comments. Typically this file would include lines like

```
# phy   mac                     room slot       wlan0                   wlan1
01      00:03:1d:0e:03:19       01              7c:c3:a1:a8:1b:70       7c:c3:a1:a2:67:f5 
<snip>
38      00:03:1d:0e:24:79       preplab         04:54:53:00:e2:65       7c:c3:a1:a8:0b:63
```

Which means that node labeled `fit01` is deployed in position, while node labeled `fit38` is not deployed in the chamber, but in the preplab instead. So you can change the `room slot` column (mac addresses must of course be kept intact) to reflect your change.

Imagine we now need to **take out `fit27` for maintenance**, and **replace it with node `fit42`**, we would then write instead

```
# phy   mac                     room slot       wlan0                   wlan1
<snip>
27      00:03:1d:0d:e1:9b       preplab         e4:ce:8f:53:f4:08       7c:c3:a1:a8:0a:fd
<snip>
42      00:03:1d:0e:03:5b       27              7c:c3:a1:a8:26:9e       7c:c3:a1:a8:1c:2a
```

## faraday 

### compute new config

```
parmentelat ~/git/r2lab/inventory $ make configure
configure.py r2lab.map
r2lab.map:27 - undeployed physical node 27 - ignored
r2lab.map:38 - undeployed physical node 38 - ignored
r2lab.map:39 - undeployed physical node 39 - ignored
r2lab.map:40 - undeployed physical node 40 - ignored
r2lab.map:41 - undeployed physical node 41 - ignored
(Over)wrote r2lab-omf.json from r2lab.map
(Over)wrote r2lab-rhubarbe.json from r2lab.map
(Over)wrote r2lab.dnsmasq from r2lab.map
(Over)wrote r2lab.hosts from r2lab.map
(Over)wrote r2lab-nagios-nodes.cfg from r2lab.map
(Over)wrote r2lab-nagios-groups.cfg from r2lab.map
(Over)wrote r2lab-diana.db from r2lab.map
```

The warning messages are normal, then let you check which node definitions were not used to compute the new configuration for faraday.

### apply new config

for deploying this on faraday you can just run

 * `make infra` 

   to push the dnsmasq tables into faraday, so that DHCP knows about the new mapping, and optionnally
 * `make nagios` 

   to refresh the configuration for `faraday.inria.fr/nagios3`; note that this should be done even when swapping a spare node for a broken node, because the IP address of the CMC card is burned into the box and cannot be defined through DHCP.

 * `make json`

    to push the omf-sfa config 

**NOTES** 
* the last operation is optional because, since late 2015 the omf-sfa config only exposes a single node (named `37nodes`) upstream to the portal, so that reservation is simpler; the consequence of this is that the omf-sfa configuration does not change very often any more, if at all.
* also the nagios thing is probably not very useful anymore, now that we have our own decent monitoring system in place.

## preplab (preplab)

In the preplab, there is no notion of a physical location, of course. So a node labeled `fit23` or `fit42` will always we accessible as `fit23` or `fit42` resp., regardless of the `room slot` column in `r2lab.map`. So in this particular example no change is required on preplab.

Regardless, the following targets are available when targetting `preplab` instead; the `preplab-` prefix can be replaced with `prep-` 

* `make preplab-configure` 
* `make preplab-json` 
* `make preplab-infra` 

## Miscell

* `make tools` lets you update utilities like `display-db.py` and others

* `make preplab-tools` does what you expect
