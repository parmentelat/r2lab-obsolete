# load
## server
    frisbeed -i 192.168.3.200 -m 224.0.0.1 -p 7000 -W 50000000 /var/lib/omf-images-6/baseline.ndz
## client
    frisbee -i 192.168.3.31 -m 224.0.0.1 -p 7000 /dev/sda

# save

## server 
    /bin/nc -d -l 192.168.3.200 9000 > /var/lib/omf-images-6/new_image.ndz
## client
    imagezip -o -z1 /dev/sda - | nc -n 192.168.3.200 9000

