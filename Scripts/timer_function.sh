#!/bin/bash
#
# Elapsed time.  Usage:
#
#   t=$(timer)
#   ... # do something
#   printf 'Elapsed time: %s\n' $(timer $t)
#      ===> Elapsed time: 0:01:12
#
#
#####################################################################
# If called with no arguments a new timer is returned.
# If called with arguments the first is used as a timer
# value and the elapsed time is returned in the form HH:MM:SS.
#
function timer()
{
    if [[ $# -eq 0 ]]; then
        echo $(date '+%s')
    else
        local  stime=$1
        etime=$(date '+%s')

        if [[ -z "$stime" ]]; then stime=$etime; fi

        dt=$((etime - stime))
        ds=$((dt % 60))
        dm=$(((dt / 60) % 60))
        dh=$((dt / 3600))
        printf '%d:%02d:%02d' $dh $dm $ds
    fi
}

# If invoked directly run test code.
if [[ $(basename $0 .sh) == 'timer' ]]; then
    t=$(timer)
    read -p 'Enter when ready...' p
    printf 'Elapsed time: %s\n' $(timer $t)
fi

## vim: tabstop=4: shiftwidth=4: noexpandtab:
## kate: tab-width 4; indent-width 4; replace-tabs false;
