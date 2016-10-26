# convenience tools for r2lab.inria.fr
#
# not sure where this log file is going to end up
alias logs-django="tail -f /var/lib/r2lab.inria.fr/django.log /var/log/httpd/*log"
alias logs-r2lab=logs-django

alias logs-sidecar="journalctl -b -f --unit=sidecar"
