# convenience tools for r2lab.inria.fr
#
# not sure where this log file is going to end up
alias logs-django="tail -f /var/lib/r2lab.inria.fr/django.log /var/log/httpd/*log"
doc-admin logs-django alias
alias logs-r2lab=logs-django
doc-admin logs-r2lab alias

alias logs-sidecar="tail -f /var/log/sidecar.log"
alias jour-sidecar="journalctl -b -f --unit=sidecar"
doc-admin logs-sidecar alias
doc-admin jour-sidecar alias

