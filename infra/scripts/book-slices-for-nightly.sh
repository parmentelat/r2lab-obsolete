SHELL=/bin/sh
HOME=/root
PATH=/root/bin:/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/bin
python3 /root/r2lab/nightly/book-nightly.py -p 2016-9-8 2016-9-18 -d sun,wed > /var/log/book-nightly.log 2>&1;
