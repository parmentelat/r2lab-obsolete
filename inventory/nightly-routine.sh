SHELL=/bin/sh
HOME=/root
PATH=/root/bin:/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/bin
python /root/fitsophia/nightly/reset_faraday.py -N [4-37] > /var/log/reset_faraday.log 2>&1;
