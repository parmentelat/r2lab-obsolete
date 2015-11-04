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
    echo Stopping dnsmasq
    service dnsmasq stop
    ### start
    echo Starting dnsmasq
    service dnsmasq start
    echo Starting ntrc
    start ntrc
    echo Starting omf-sfa
    service omf-sfa start
    echo "Exiting $COMMAND on" $(date)
}


restart-all >> $output
