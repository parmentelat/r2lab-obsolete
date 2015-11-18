SHELL=/bin/sh
HOME=/root
PATH=/root/bin:/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/bin
python /root/fitsophia/nightly/reset_faraday.py -N 2,4,17,18,19,20,22,24,25,26,27,28,29 > /var/log/reset_faraday.log 2>&1;
