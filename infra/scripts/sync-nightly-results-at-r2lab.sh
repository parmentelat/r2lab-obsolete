SHELL=/bin/sh
HOME=/root
PATH=/root/bin:/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/bin
rsync -a /root/r2lab/nightly/nightly_data.json root@r2lab.inria.fr:/root/r2lab/r2lab.inria.fr/files/nightly/ > /var/log/sync-nightly.log 2>&1;
rsync -a /root/r2lab/nodes/maintenance_nodes.json root@r2lab.inria.fr:/root/r2lab/r2lab.inria.fr/files/nodes/ > /var/log/sync-nightly.log 2>&1;
