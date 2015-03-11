# FIT Inventory tools

the workflow for maintaining our inventory from the googl spreadsheet is as follows

## get the latest `csv` file

make sure to get the latest `fit.csv` from the spreadsheet

* if your browser stores stuff under `~/Downloads` you can probably use `make import` 

## update the faraday deployment

for deploying this on faraday you can just run

`make faraday`

 that will take care of

  * populating the DB from JSON
  * updating `/etc/hosts`
  * updating `/etc/dnsmasq.d/testbed.conf` and restarting `dnsmasq`
  * and finally update the details of the `nagios` config, as well as restarting the `nagios` service

## updating bemol

Likewise you can just run

`make bemol` 

that will do the same for `bemol`, except for the `nagios` since there is no such service on nagios.

## **NOTES**

* The config on `faraday` needs to change if for example you replace the node on physical position `15` with the node labelled `39`

  This is because from then on, OMF needs to reach IP 192.168.1.39 for restarting logical node 15, but at the same time for DHCP we assign the MAC addresses of physical-node-39 to the 192.168.{2,3}.15 IP addresses

* OTOH for bemol there is no such trick, so the config for bemol is expected to be more stable and to need less frequently to be updated.

## Miscell

* `make tools` lets you update utilities like `display-db.py` and others

* `make bemol-tools` does what you expect
