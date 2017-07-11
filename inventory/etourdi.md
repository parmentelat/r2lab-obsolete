# stupidest mistake so far

One day I ran a harmless rhubarbe command in `/etc/dnsmasq.d`. This had the result of creating a file named `/etc/dnsmasq.d/rhubarbe.log`. 

Next time dnsmasq tried to run, it complained about a syntax error in this file, refused to start; no DNS, ouch .. 

Took me 1 hour to figure that out. 

# another glitch seen on `etourdi` 

One day after a power outage:

* `etourdi` failed to restart on its own once power was back on
* and, after we manually rebooted it, `etourdi`'s iptables were off somehow

So I have reconfigured the BIOS so that `etourdi` will now come back on in case of a power outage.

Googling the second issue a bit brought up this:

* https://unix.stackexchange.com/questions/339465/how-to-disable-firewalld-and-keep-it-that-way
* so I followed that advice and just did

   `dnf remove firewalld` 

Which seems to have done it once and for good.