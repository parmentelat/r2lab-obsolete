# install sidecar on r2lab.inria.fr

## git

    yum install git
    cd /root
    git clone https://github.com/parmentelat/fitsophia.git
    
## node.js

    yum install -y nodejs npm
    

## fitsophia
 
    cd /root/fitsophia/website/jsmap
    npm install --save socket.io
    npm install --save express
    
After what
     
    # cd /root/fitsophia/website/sidecar
    [root@r2lab sidecar]# node r2lab-sidecar.js
    listening on *:8000	
    

