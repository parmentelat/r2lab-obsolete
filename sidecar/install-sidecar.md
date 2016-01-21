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
    listening on *:443	
    
NOTE: when running a devel server: we use 443 as the port number for sidecar to increase chances that a firewall would let this traffic pass. In addition, logging into /var/log/sidecar.log is not a good idea, so you need to do

    $ sudo sidecar.js -l
