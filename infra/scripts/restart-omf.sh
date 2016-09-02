#!/bin/bash

COMMAND=$(basename $0)

output=/var/log/restart-omf.log

function restart-omf () {
    echo "==================== Entering $COMMAND on" $(date)
    ### stop
    echo Stopping omf-sfa
    systemctl stop omf-sfa
    echo Stopping ntrc
    stop ntrc
    echo Stopping openfire
    service openfire stop
    echo Stopping dnsmasq
    service dnsmasq stop
    ### start
    echo Starting dnsmasq
    service dnsmasq start
    echo Starting openfire
    service openfire start
    echo Starting ntrc
    start ntrc
    echo Starting omf-sfa
    systemctl start omf-sfa
    echo "Exiting $COMMAND on" $(date)
}

if [[ -n "$@" ]]; then
    # if called with any argument, we show output on the terminal
    restart-omf
else
    # otherwise (for cron) this gets logged
    restart-omf >> $output
fi
