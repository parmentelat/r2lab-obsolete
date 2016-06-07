SHELL=/bin/sh
HOME=/root
PATH=/root/bin:/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/bin
python /root/r2lab/nightly/nightly.py -N all -a 11,19 > /var/log/nightly.log 2>&1;
