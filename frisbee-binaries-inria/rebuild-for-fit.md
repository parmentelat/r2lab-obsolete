# imagezip
* Started from a standard fedora21 (PL) build VM
* Used a fresh git clone from emulab's repo - branch master
* sources located in clientside/os/imagezip
* yum installed the following packages for static libraries
  * glibc-static
  * zlib-static
  * openssl-static (probably not required w/ WITH_CRYPTO=0) 
* ran `make -f Makefile-linux.sa WITH_CRYPTO=0`

* In a first attempt I was not turning off crypto and then I had to add `-ldl` before `-lz` but crypto does not seem like a very useful addition in our case

# frisbee
* Quite identical - same location - same make options
* tried to apply OMF patch but the change in client.c does not apply any more, so I left it out for now