# r2lab.inria.fr

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
     
    [root@r2lab jsmap]# node r2lab-server.js
    listening on *:3000	     

