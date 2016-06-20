This directory will receive some static files produced by the nightly routine to be served like "assets".
They came from a rsync instruction in crontab of faraday server that sync to r2lab server.

source:
 faraday.inria.fr:/root/r2lab/nightly/nightly_data.json
target:
 r2lab.inria.fr:/root/r2lab/r2lab.inria.fr/files/nightly/nigthly_data.json

then, in r2lab/infra/scripts we have this .sh called from the cron of faraday:
rsync -a /root/r2lab/nightly/nightly_data.json root@r2lab.inria.fr:/root/r2lab/r2lab.inria.fr/files/nightly/ > /var/log/sync-nightly.log 2>&1;
