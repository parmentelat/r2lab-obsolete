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

## r2lab
 
    cd /root/r2lab/website/sidecar
    npm install --save socket.io
    npm install --save express
    
After what
     
    # cd /root/r2lab/website/sidecar
    [root@r2lab sidecar]# node sidecar.js
    listening on *:443	
    
NOTE: when running a devel server: we use 443 as the port number for sidecar to increase chances that a firewall would let this traffic pass. In addition, logging into /var/log/sidecar.log is not a good idea, so you need to do

    $ sudo sidecar.js -l

# install website on r2lab.inria.fr

## make

    yum install make
    
## markdown-styles 

Check you get at least 3.0

    npm install -g markdown-styles 
    
## Unicode

`r2lab.inria.fr` was not too happy to run `index.py`, because of accents
instead of messing with the system config I have tweaked `website/Makefile` to export LC_ALL and now it seems OK. Doing this system-wide would definitely be better.

## push from git to web

    make preview publish
