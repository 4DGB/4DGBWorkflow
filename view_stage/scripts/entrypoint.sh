#!/bin/bash

#
# Entrypoint script for the 'View' Docker Container
#
# Expects a 4DGB Project directory to be bind-mounted at '/in'
# Starts a Gunicorn server hosting the project
#
# Expects two command-line arguments: PORT and NAME. These don't affect anything with the
# server itself. They are just used in creating the URL the script will tell the user to visit.
#       PORT is the port on the host-machine that the container publishes to
#       NAME is the name of the project
#

set -eu

# Report version
echo -ne "\e[1m> Browser version: \e[0m"
./scripts/report_version.sh

# Run Gunicorn
GUNICORN_CONF="$(pwd)/gunicorn.conf.py"
(
    cd /opt/4dgb
    export PROJECT_HOME="/in"
    gunicorn --config "$GUNICORN_CONF"
)

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

sleep infinity
