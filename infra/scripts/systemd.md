# Purpose

As of Sept. 2nd 2016, we run ubuntu-16.04 and fedora24 on faraday and r2lab resp. 
Both distros now feature `systemd` as the native init utility, so it feels like it's time to switch to `systemd` to handle the various services required by R2lab.

This document is an attempt at summarizing the various services on faraday and r2lab, and how they are currently started/managed. Objectives are to&nbsp;:

* smooth things out so that everything starts up properly after a reboot (right now, it's a cronjob that coincidentally triggers `monitor` and `sidecar`)
* only use proper systemd `.service` files to define everything in a homogeneous and simple way
* as a side effect, we have diminished the importance of `restart-website.sh`; reboot does not rely on that script anymore, and the script runs only once a day. Could hopefully be turned off entirely in the future.

# faraday

## cron jobs

`restart-website.sh` is now triggered only ***ONCE A DAY***

```
4,14,24,34,44,54 * * * * /root/diana/auto-update.sh
0 6 * * * /root/r2lab/infra/scripts/restart-website.sh
10 3 * * * /root/r2lab/infra/scripts/nightly.sh
30 3 * * * /root/r2lab/infra/scripts/sync-nightly-results-at-r2lab.sh
```

## omf_sfa
* Now runs under `systemd`, see `omf_sfa/init/omf-sfa.service`

## monitor
* ~~Triggered by `monitor.sh`~~
* ~~in turn called by `restart-website.sh` through cron~~
  * ~~Is **not** called at boot-time, so right now it starts within an hour~~
* Now uses `monitor.service` 

## www
* ~~There actually is a test page answering when pointing a web browser at faraday.inria.fr~~
* ~~It should either be turned off altogether, or if apache2 is a requirement, then redirect this to `http://r2lab.inria.fr`~~
* OK - this service is now turned off

## NOTES
* `restart-omf.sh` is only a convenience; 

# r2lab

## cron jobs

`restart-website.sh` is now triggered only ***ONCE A DAY***

```
4,14,24,34,44,54 * * * * /root/diana/auto-update.sh
0 6 * * * /root/r2lab/infra/scripts/restart-website.sh
```

***NOTE*** that `restart-website.sh` also pulls from git and pushes into `/var/www/r2lab.inria.fr`

## django
* actually part of the `httpd` service (through a wsgi app)
* `httpd` is an enabled service, so that starts up right away at boot-time
* it also - unsurprisingly - gets restarted when `restart-website.sh` triggers, through `r2lab.inria.fr/Makefile` and specifically its `apache` target

## sidecar

* ~~at first sight this is similar to `monitor`, it gets started through `sidecar.sh` itself invoked in `restart-website.sh`~~
* BNow uses `sidecar.service`

