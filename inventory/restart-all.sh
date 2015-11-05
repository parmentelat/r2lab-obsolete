#!/bin/bash

COMMAND=$(basename $0)

output=/var/log/restart-all.log

function restart-all () {
    echo "==================== Entering $COMMAND on" $(date)
    ### stop
    echo Stopping omf-sfa
    service omf-sfa stop
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
    service omf-sfa start
    echo "Exiting $COMMAND on" $(date)
}

if [[ -n "$@" ]]; then
    # if called with any argument, we show output on the terminal
    restart-all
else
    # otherwise (for cron) this gets logged
    restart-all >> $output
fi
