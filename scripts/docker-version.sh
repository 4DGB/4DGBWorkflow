#!/bin/bash
#
# Script run inside the Docker container to print version information
# according the the version files for different components
#
# This is run at the start when in 'local' mode, but it's also
# used as the entrypoint script by the runner when run with
# the 'version' command
#

if [ "$BROWSERCONTAINER" != "yes" ] ; then
    echo "This script needs to be run inside the 4DGB Workflow docker container" 1>&2
    exit 1
fi

echo -ne "\e[1m> Workflow version: \e[0m"
cat ./version.txt

echo -ne "\e[1m> Browser version:  \e[0m"
cat /opt/git/4dgb/server/version.md