# install sidecar on r2lab.inria.fr

## git

    yum install git
    cd /root
    git clone https://github.com/parmentelat/fitsophia.git
    
## node.js

### r2lab (fedora)
    yum install -y nodejs npm
    
### faraday (ubuntu)

I some point I thought I would install this on faraday too; however

~~`apt-get install nodejs`~~
    
This does not work right away; some kind of unmet dependency...

I put this in standby for now; not crucial anyway

## fitsophia
 
    cd /root/fitsophia/website/jsmap
    npm install --save socket.io
    npm install --save express
    
After what
     
    # cd /root/fitsophia/website/sidecar
    [root@r2lab sidecar]# node r2lab-sidecar.js
    listening on *:8000	
    

# install website on r2lab.inria.fr

## make

    yum install make
    
## markdown-styles 

Check you get at least 3.0

    npm install -g markdown-styles 
    
## Unicode

`r2lab.inria.fr` was not too happy to run `index.py`, because of accents
instead of messing with the system config I have tweaked `website/Makefile` to export LC_ALL and now it seems OK. Doing this system-wide would definitely be better.