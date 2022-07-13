#!/bin/bash

#
# Entrypoint script for the docker container
#
# Switches to the UID/GID of the specified user, then builds the project
# and starts Gunicorn (in the docker-setup.sh script). It then switches to
# www-data and runs Nginx which will proxy the Gunicorn server.
#

if [ "$BROWSERCONTAINER" != "yes" ] ; then
    echo "This script needs to be run inside the 4DGB Workflow docker container" 1>&2
    exit 1
fi

if [ "${NEWUID:-0}" -eq 0 ] || [ "${NEWGID:-0}" -eq 0 ] && [ "${ROOTLESS:-no}" != "yes" ] ; then
    echo "Container cannot be run as root!" 1>&2
    exit 1
fi

set -eu

function run_as_user {
    if [ "${ROOTLESS:-no}" = "yes" ] ; then
        "$@"
    else
        gosu "$NEWUID:$NEWGID" "$@"
    fi;
}

# Report version
./scripts/docker-version.sh

#
# Build project
#

echo -e "\e[1m[\e[32m>\e[0m\e[1m]:\e[0m Building project... (this may take a while)" >&2
run_as_user python3 ./scripts/workflow.py /project{,/.build} /opt/git/4dgb/

#
# Exit here if in BUILDONLY mode
#
if [ "${BUILDONLY:-no}" == "yes" ] ; then
    exit
fi

#
# Run Gunicorn
#

GUNICORN_CONF="$(pwd)/conf/gunicorn.conf.py"
(
    cd /opt/git/4dgb/server
    export PROJECT_HOME="/project/.build"
    run_as_user gunicorn --config "$GUNICORN_CONF"
)

#
# Print some user-friendly info if in local mode
#
if [ "$MODE" = "local" ] ; then
    # These arguments are provided by the runner script.
    # They don't affect the actual configuration. They're only
    # used so that the script can give the user the correct URL
    PORT="$1"
    NAME="$2"

    URLNAME="$(perl -MURI::Escape -e 'print uri_escape($ARGV[0]);' "$NAME")"

    echo -e "
        \e[1m#
        \e[1m# \e[32mReady!\e[0m
        \e[1m# Open your web browser and visit: 
        \e[1m# http://localhost:${PORT}/compare.html?gtkproject=$URLNAME
        \e[1m#
        \e[1m# Press [Ctrl-C] to exit
        \e[1m#
        "
fi

#
# Start nginx
#
gosu www-data:tty nginx
