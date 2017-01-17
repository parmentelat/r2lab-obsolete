# install sidecar on r2lab.inria.fr

## git

    yum install git
    cd /root
    git clone https://github.com/parmentelat/r2lab.git
    
## node.js

### r2lab (fedora)
    yum install -y nodejs npm
    
### faraday (ubuntu)

I some point I thought I would install this on faraday too; however

~~`apt-get install nodejs`~~
    
This does not work right away; some kind of unmet dependency...

I put this in standby for now; not crucial anyway

## install nodejs dependencies
 
    cd /root/r2lab/sidecar
    npm install --save socket.io
    npm install --save express
    
After what
     
    # cd /root/r2lab/website/sidecar
    [root@r2lab sidecar]# node sidecar.js
    listening on *:999	
    
NOTE: when running a devel server: as of Jan 2017 : we use 999 and not 443 any longer as the port number for sidecar, as r2lab.inria.fr runs on https
In any case you need to run your devel instance of `sidecar.js` like as follows, option `-l` allows to log in a local file instead of `/var/log/sidecar.log`:

    $ sudo sidecar.js -l
