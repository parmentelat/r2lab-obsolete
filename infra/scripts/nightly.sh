SHELL=/bin/sh
HOME=/root
PATH=/root/bin:/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/bin
python /root/r2lab/nightly/nightly_shift.py -N all > /var/log/nightly_shift.log 2>&1;
