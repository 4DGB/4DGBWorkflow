#!/bin/bash

#
# Entrypoint script for the 'build' Docker container
#
# Expects the directories '/in' and '/out' to be bind-mounted to the
# input and output project directories. Builds the project in /in and
# places the result in /out
#

set -eu

# Report version
echo -ne "\e[1m> Workflow version: \e[0m"
./scripts/report_version.sh

# Build project
echo -e "\e[1m[\e[32m>\e[0m\e[1m]:\e[0m Building project... (this may take a while)" >&2
python3 ./scripts/workflow.py /in /out
