![](oai-nodes.pdf)


# prep

```
#rload -i oai-gw-builds3 23
#rload -i oai-gw-kgen-builds3 16
rload -i oai-gw-builds4 23 16
rload -i oai-enb-builds2 11
```

# common scenario

```
rwait; ss
---
refresh
demo
o init
o build
o configure
o start
o logs
```

# Details

*****
*****
*****

# ONGOING

* have rebuilt image `oai-enb-builds`

# DB report

```
select imsi, imei, access_restriction,  mmeidentity_idmmeidentity from users where imsi = 208950000000002;

select * from mmeidentity where mmerealm='r2lab.fr' ;
```

# `build_hss` 

 * patched version in my own repo, which is what the master branch on the images point at

# NOTES on generic kernel

* tried to rebuild from scratch (14.04)
* created `oai-epc-kgen-builds` (skipped the base step)
* that turned out to have 4.2, so
* created `oai-epc-k319-builds` 
* however this turned out to have a broken build for freediameter (no network or something - see build_epc-i.log)
* so now that I know how to switch kernels:
  * restarted from `oai-gw-builds3`
  * reinstalled `3.19.0-58-generic`
  * set `DEFAULT="1>2"` in `/etc/default/grub`
  * applied `grub-update`
  * and produced `oai-gw-kgen-builds3`