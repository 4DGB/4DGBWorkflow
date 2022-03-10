#
# Dockerfile for the 4DGB Browser Workflow
#
# This is a multi-stage build. The first stage exists mostly just to build
# the client-side code for the server (which requires nodejs and webpack and
# such), then the second stage installs and sets up everything needed for the
# workflow
#
# When running, the container's entrypoint script will do all the processing,
# but it requires two environment variables to be set: NEWUID and NEWGID.
# These specify the user and group ID's of the user running the container
# so that the files output by the script will be owned by the user. To ensure
# these variables are properly set, please run the container via the helper
# script, 4dgb-workflow
#

##############################
# Stage 1: Build gtk.min.js
##############################
FROM ubuntu:20.04 as js

# Install dependencies
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    ca-certificates build-essential curl libcurl4-openssl-dev

# Setup NodeJS PPA
RUN curl -fsSL 'https://deb.nodesource.com/setup_16.x' > setup_16.x
RUN bash setup_16.x
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs

# Build Browser JS
COPY submodules/4DGB /opt/git/4dgb
RUN cd /opt/git/4dgb \
    && npm install \
    && npx webpack --config client-js/webpack.config.js \
    && cp  client-js/gtk-dist/gtk.min.js /root/gtk.min.js

##############################
# Stage 2: Everything else
##############################
FROM ubuntu:20.04 as release

# Install dependencies
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    ca-certificates build-essential libcurl4-openssl-dev \
    python3 python3-pip rsync gosu ninja-build cpanminus \
    nginx lammps
RUN cpanm URI::Escape
RUN ln -s /usr/bin/python3 /usr/bin/python

#Setup Directories/Permissions
# We need to set permissions on a few things so nginx can
# read them when running as www-data (instead of root)
RUN mkdir -p /var/lib/nginx /var/log/nginx \
    && touch /run/nginx.pid \
    && chown -R www-data:www-data /var/lib/nginx /run/nginx.pid /var/log/nginx \
    # If the container is using a tty, then we'll need to be in the tty group
    # in order to write to stdout
    && usermod -aG tty www-data

# Install Python dependencies
COPY ./requirements.txt ./requirements.txt
RUN pip3 install -r ./requirements.txt

COPY submodules/4DGB /opt/git/4dgb

# Install hic2structure.py script
COPY submodules/3DStructure /opt/git/3DStructure
RUN cd /opt/git/3DStructure/src \
    && python3 setup.py install

# Copy files
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
    ; fi
# Copy configuration
RUN cp ./conf/nginx-${MODE}.conf /etc/nginx/nginx.conf

ENV BROWSERCONTAINER="yes"
ENTRYPOINT [ "./scripts/entrypoint.sh" ]
