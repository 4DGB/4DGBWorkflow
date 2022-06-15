#
# Dockerfile for the 4DGB Browser Workflow
#
# This is a multi-stage build. The first stage builds the client-side
# javascript library for the server, the second stage builds all Python
# dependencies, and the third stage brings it all together
#
# When running, the container's entrypoint script will do all the processing,
# but it requires two environment variables to be set: NEWUID and NEWGID.
# These specify the user and group ID's of the user running the container
# so that the files output by the script will be owned by the user. To ensure
# these variables are properly set, please run the container via the helper
# script, 4DGBWorkflow
#

##############################
# Stage 1: Build gtk.min.js
##############################
FROM node:16-alpine as js

# Build Browser JS
COPY submodules/4DGB /opt/git/4dgb
RUN cd /opt/git/4dgb/client-js \
    && npm install \
    && NODE_ENV=production npx webpack \
    && cp  gtk-dist/gtk.min.js /root/gtk.min.js

##############################
# Stage 2: Python dependencies
##############################

FROM python:3.10.4-bullseye as python

COPY ./requirements.txt ./requirements.txt
RUN pip3 install wheel \
    && pip3 wheel -r requirements.txt --wheel-dir /root/wheels

# Install hic2structure.py script
COPY submodules/3DStructure /opt/git/3DStructure
RUN cd /opt/git/3DStructure/ \
    && pip3 wheel . --wheel-dir /root/wheels

##############################
# Stage 3: Putting it all together
##############################
FROM python:3.10.4-bullseye as release

# Install dependencies
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        rsync gosu cpanminus nginx lammps \
    && apt-get clean \
    && cpanm URI::Escape \
    && ln -s /usr/bin/python3 /usr/bin/python

#Setup Directories/Permissions
# We need to set permissions on a few things so nginx can
# read them when running as www-data (instead of root)
RUN mkdir -p /var/lib/nginx /var/log/nginx \
    && touch /run/nginx.pid \
    && chown -R www-data:www-data /var/lib/nginx /run/nginx.pid /var/log/nginx \
    # If the container is using a tty, then we'll need to be in the tty group
    # in order to write to stdout
    && usermod -aG tty www-data

# Install pre-compiled python dependencies
COPY ./requirements.txt ./requirements.txt
COPY --from=python /root/wheels ./wheels
RUN pip3 install --no-index --find-links=./wheels -r ./requirements.txt \
    && pip3 install --no-index --find-links=./wheels hic2structure

# Copy files
COPY submodules/4DGB /opt/git/4dgb
COPY --from=js /root/gtk.min.js /opt/git/4dgb/server/static/gtk/js/
COPY ./scripts ./scripts
COPY ./conf ./conf

#Determine if this is going to be a production, or a local setup
ARG MODE=local
ENV MODE ${MODE}
RUN if [ "${MODE}" != "production" ] && [ "${MODE}" != "local" ] ; then \
        echo "MODE must be either 'production' or 'local'" \
        && exit 1 \
    ; fi
# If in production mode, symlink nginx's access log to stdout
RUN if [ "${MODE}" = "production" ] ; then \
    ln -sf /dev/stdout /var/log/nginx/access.log \
    ; fi \
    && cp ./conf/nginx-${MODE}.conf /etc/nginx/nginx.conf

# Copy version
COPY ./version.txt ./version.txt

ENV BROWSERCONTAINER="yes"
ENTRYPOINT [ "./scripts/entrypoint.sh" ]
