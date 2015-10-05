# wlan setup
* ad hoc mode
* on fixed channel 11 for now
* derive IP on
  * `10.0.0.<id>/24`  for `wlan01` and of course
  * `10.0.1.<id>/24` when using `wlan1`

# setup

## prerequisites

Define the following local shell variables, e.g.

    here=$(hostname | sed -e s,fit,,)

as well as a second node for testing stuff over

    peer=03
     

## Select wlan interface
Set this to select `wlan0` 

    w=0

## Initialize    

    iwconfig wlan$w mode ad-hoc
    iwconfig wlan$w channel 11
    iwconfig wlan$w essid 'r2lab'
    ip link set wlan$w up
    ip addr add 10.0.$w.$here/24 dev wlan$w

    iw dev wlan$w scan
    ping -c 1 10.0.$w.$peer
    
    iw dev wlan$w info

## create source file

    cd /tmp
    mega=$((1024*1024))
    dd if=/dev/zero bs=$mega count=128 of=128mb

## send traffic

    rsync -av /tmp/128mb 10.0.$w.$peer:/tmp/received


## stats

    head /sys/class/net/wlan$w/statistics/[rt]x_bytes
    
