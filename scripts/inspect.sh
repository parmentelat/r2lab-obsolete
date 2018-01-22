SHELL=/bin/sh
HOME=/root
PATH=/root/bin:/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/bin

python3 /root/r2lab/infra/inspect/inspect.py > /var/log/inspect.log 2>&1;
