SHELL=/bin/sh
HOME=/root
PATH=/root/bin:/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/bin
#sync nightly db results
rsync -a /root/r2lab/nightly/nightly_data.json root@r2lab.inria.fr:/root/r2lab/r2lab.inria.fr/files/nightly/ > /var/log/sync-nightly.log 2>&1;
#sync maintenance db results
rsync -a /root/r2lab/nodes/maintenance_nodes.json root@r2lab.inria.fr:/root/r2lab/r2lab.inria.fr/files/nodes/ > /var/log/sync-maintenance.log 2>&1;
##sync info db, images and md files
rsync -a /root/r2lab/nodes/info_nodes.json root@r2lab.inria.fr:/root/r2lab/r2lab.inria.fr/files/nodes/ > /var/log/sync-info.log 2>&1;
rsync -a /root/r2lab/nodes/images/* root@r2lab.inria.fr:/root/r2lab/r2lab.inria.fr/files/nodes/images/ > /var/log/sync-info-images.log 2>&1;
rsync -a /root/r2lab/nodes/info/* root@r2lab.inria.fr:/root/r2lab/r2lab.inria.fr/files/nodes/info/ > /var/log/sync-info-files.log 2>&1;
