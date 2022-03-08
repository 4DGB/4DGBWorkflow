#!/bin/bash

#
# This script is run by the docker container's entrypoint. It is run with the
# permissions of the user who started the container and performs the
# setup/build of the project. It ends by starting up the gunicorn instance
# running the browser
#

if [ "$BROWSERCONTAINER" != "yes" ] ; then
    echo "This script needs to be run inside the 4DGB Workflow docker container" 1>&2
    exit 1
fi

set -eu

PROJECT="$1"
OUTPUT="$PROJECT/.build/"

GUNICORN_CONF="$(pwd)/conf/gunicorn.conf.py"

python3 ./scripts/configure.py "$PROJECT" "$OUTPUT" "/opt/git/4dgb/"

cd "$OUTPUT"

# Ninja's output only confuses end-users, so we just hide it
ninja > /dev/null

gunicorn --config "$GUNICORN_CONF"
