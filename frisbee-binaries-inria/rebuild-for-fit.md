# build vm
* 1$st$ attempt 
  * used a standard fedora21 (PL) build VM
* 2$nd$ 
  * created a dedicated build VM in buzzcocks for that purpose only

#
    $ ssh root@buzzcocks.pl.sophia.inria.fr
    buzzcocks # lce frisbee
    frisbee # cd /build

# build requirements
yum installed the following packages for static libraries

    yum -y install git make gcc wget tar	
    yum -y install glibc-static zlib-static openssl-static 

although this last one probably is not required w/ WITH_CRYPTO=0

# pulling code

On frisbee.pl.sophia.inria.fr

    cd /build
    git clone git://git-public.flux.utah.edu/emulab-stable.git
    cd emulab-stable
    git checkout master

# imagezip

    cd /build/emulab-stable/clientside/os/imagezip/
    make -f Makefile-linux.sa WITH_CRYPTO=0

* In a first attempt I was not turning off crypto and then I had to add `-ldl` before `-lz` but crypto does not seem like a very useful addition in our case

# frisbee
* Quite identical - same location - same make options
* tried to apply OMF patch but the change in client.c does not apply any more, so I left it out for now

