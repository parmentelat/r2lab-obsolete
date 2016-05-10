# 2016 May 2 `oai-enb-*`

This is more informal as the initial setup was done by Thierry T. on fit 11.

However the same general principle should apply, using the `oai-enb` alias, that points at `/root/r2lab/rhubarbe-images/oai-enb.sh` and that supports the same subcommands as `oai-gw` like `base`, `builds`, `configure`, `run`, etc..

So in a nutshell

* `oai-as-enb`
* `oai base`
* save as `oai-enb-base`
* `oai-as-enb`
* `oai builds`
* save as `oai-enb-builds`


## Pushing tmp code to enb fit11

```
# laptop
r push1 rsync -av oai-*.sh nodes.sh $(plr faraday):
# root@faraday
r push2@fit11 rsync -av oai-*.sh nodes.sh fit11:/tmp/
```



****
****
****
# 2016 Apr 27 `oai-gw-*`

* done first on fit38, then moved on fit16
* based on
  * git's `openair-cn/DOCS/EPC_User_Guide.pdf`
  *  [this document](https://gitlab.eurecom.fr/oai/openairinterface5g/wikis/HowToConnectCOTSUEwithOAIeNB)

## Bootstrap

```
cd
git clone https://github.com/parmentelat/r2lab.git
ln -s r2lab/infra/user-env/nodes.sh .bash_aliases
```

This has the side effect of defining convenience bash functions like e.g.

* `help` : micro help
* `gitup` : run git pull in the git repos `/root/r2lab`, `/root/openair-cn` and `/root/openairinterface5g` when present
* `bashrc` : reload `r2lab/infra/user-env/nodes.sh`
* `oai-gw` : run `oai-gw.sh` - for the 5g gateway node - requires a subcommand
* `oai-enb` : run `oai-enb.sh` - for the 5g eNodeB node - requires a subcommand


## Pushing tmp code

## Pushing tmp code to gw fit16

```
# laptop
r push1 rsync -av oai-*.sh nodes.sh $(plr faraday):
# faraday
r push2@fit16 rsync -av oai-*.sh nodes.sh fit16:/tmp/
```

## Base

passwords and interactive installs

##### Automated : in principle this is equivalent to

```
/root/r2lab/infra/user-env/oai-gw.sh base
```

##### Manual

We do these 2 installs first off so we can redirect outputs on files in later stages.


```
apt-get install -y mysql-server
```

 * set mysql server password to `linux` (enter twice for confirmation)

```
apt-get install -y phpmyadmin
```

 * First prompt is about using `apache2`
 * Then you're prompted for the mysql password (enter `linux` once)
 * Then for a phpmyadmin password (enter `admin`, twice for confirmation)


Git cloning, and `cpufrequtils`

```
cd
echo -n | \
   openssl s_client -showcerts -connect gitlab.eurecom.fr:443 2>/dev/null | \
   sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' >> \
   /etc/ssl/certs/ca-certificates.crt
git clone https://gitlab.eurecom.fr/oai/openair-cn.git
git clone https://github.com/parmentelat/r2lab.git

apt-get install -y cpufrequtils
echo 'GOVERNOR="performance"' > /etc/default/cpufrequtils
update-rc.d ondemand disable
/etc/init.d/cpufrequtils restart
# this seems to be purely informative ?
cpufreq-info
```

****
Saved in `oai-gw-base`
****

## Builds

```
oai-gw build
```

which is equivalent to `/root/r2lab/infra/user-env/oai-gw.sh build`

****
Saved in `oai-gw-builds`
****

### reconfigure

```
oai-gw configure
```

### run

```
oai-gw start
oai-gw status
oai-gw stop
```

****
****
****
****
****

# Backup section : 

## a summary of previous - not quite working - attempts

### HSS

```
cd /root/openair-cn/SCRIPTS
./build_hss -i -F -f localhost >& build_hss.log
# `-i` for installing dependencies 
# `-F` is to force installs - note that we have installed mysql-server separately in `core0`
# `-f` in this context is to specify the hostname 
```

### EPC

```
cd /root/openair-cn/SCRIPTS
./build_epc -i -f -H localhost >& build_epc.log
# `-i` for installing dependencies 
# `-f` is to force installs - note that we have installed mysql-server separately in `core0`
# `-H` in this context is to specify the hostname 
```

### Config

```
fitid=16
cd
git clone https://github.com/parmentelat/r2lab.git
cd openair-cn/BUILD/EPC/
sed -e s,xxx,$fitid,g /root/r2lab/rhubarbe-images/epc-r2lab.sed.in > epc-r2lab.sed
sed -f epc-r2lab.sed epc.conf.in > epc.conf
```

at which point `diff epc.conf.in epc.conf` should show 2 pairs of 2 lines changed to use the `data` interface

```
cd /root/openair-cn/SCRIPTS
./build_epc -C -l >& build_epc.conf.log
```

* `-C` : create config
* `-l` : use localhost as hss

```
./run_epc -i -r
```

* `-i` : set up interfaces
* `-r` : remove gptu kmodule 

****
****
****

```
root@fit16:~/openair-cn/SCRIPTS# ./run_epc -i -r
setting network interfaces: 1
rmmod: ERROR: Module xt_GTPUSP is not currently loaded
OPENAIR_DIR    =
GTPU kernel module installed
Cannot find /usr/local/bin/mme_gw executable, have a look at the output of build_epc executable
```

need to dig into the `build_epc.log` file
****
****
****



# 2016 Apr 26 `ubuntu-14.04-k3.19-lowl`

* done on fit01
* started from `ubuntu-14.04`

## untrimmed version 

#####  this version has both the stock and lowlat kernels

* installed the following

```
apt-get install \
  linux-headers-3.19.0-58-lowlatency \
  linux-image-3.19.0-58-lowlatency \
  module-init-tools
```

* edited `/etc/default/grub` so that 

```
GRUB_DEFAULT="1>2"
``` 

*  Which means
  
  * it means we want the submenu that shows up in second position in the grub main menu; and then the third entry in that submenu
  * this should be stable enough, as the 2 first ones (in the submenu) were the stock `4.2.0-27-generic` kernel and associated recovery mode, then the one we are interested in
  * also beware of **using quotes** as this looks like a shell script (I'm guessing); in any case without the quotes I always the stock kernel
  * See detailed doc here
[https://help.ubuntu.com/community/Grub2/Submenus]()

* Then run `update-grub` to push on `/boot`
* ended up with a **800Mb** image

## trimmed version

##### Only the lowlatency kernel on board

* spotted the stock kernels with 

```
dpkg -l | grep 4.2
```

* removed them using

```
dpkg --purge remove <the list>
```

* edited again `/etc/default/grub`

```
GRUB_DEFAULT="1>0"
```

* ran `update-grub`
* ended up with a **694 Mb** image

