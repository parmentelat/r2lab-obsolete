SHELL=/bin/sh
HOME=/root
PATH=/root/bin:/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/bin
#python /root/r2lab/nightly/nightly.py -N all > /var/log/nightly.log 2>&1;
#Now I call the fetch to check if a nightly lease is schedule once
#the users can move it in the UI
python /root/r2lab/nightly/fetch-nightly.py -N all > /var/log/fetch-nightly.log 2>&1;
