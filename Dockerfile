FROM ubuntu:20.04

#
# Dockerfile for the 4DGB Browser Workflow
#
# The images from this Dockerfile run a script that takes a project directory
# as input, processes the data, then runs an instance of the 4DGB Browser to
# view it.
#
# This will pull in the tools needed from their respective repositories:
#   - https://github.com/lanl/4DGB (the 4DGB Browser)
#   - https://github.com/4DGB/3DStructure (the hic2structure.py script)
# For each of these, the Dockerfile has hard-coded a commit ID to checkout
# for the repo. If an update is made to one of these repos and you'd like
# to pull that update in, simply update the 'ENV' line that specifies the
# commit ID
#
# NOTE: For the time being, the 3DStructure repository is *private*
# So in order to pull it, you need to build this image using BuildKit and
# have a running ssh agent with keys to acess GitHub. You can use BuildKit
# by setting the environment variable DOCKER_BUILDKIT to '1', and forward your
# ssh agent with the flag '--ssh default' e.g:
#
#   DOCKER_BUILDKIT=1 docker build -t 4dgbworkflow --ssh default .
#
# When running, the container's entrypoint script will do all the processing,
# but it requires two environment variables to be set: NEWUID and NEWGID.
# These specify the user and group ID's of the user running the container
# so that the files output by the script will be owned by the user. To ensure
# these variables are properly set, please run the container via the helper
# script, run_project
#

# Install dependencies
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3 python3 python3-pip rsync cpanminus gosu git \
    ca-certificates build-essential curl libcurl4-openssl-dev \
    nginx jq ninja-build lammps
RUN ln -s /usr/bin/python3 /usr/bin/python
# Install scroller (for pretty output!)
RUN cpanm Term::Scroller

# Setup NodeJS PPA
RUN curl -fsSL 'https://deb.nodesource.com/setup_16.x' > setup_16.x
RUN bash setup_16.x
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs

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

# Build Browser JS
COPY submodules/4DGB /opt/git/4dgb
RUN cd /opt/git/4dgb \
    && npm install \
    && npx webpack --config client-js/webpack.config.js \
    && cp  client-js/gtk-dist/gtk.min.js server/static/gtk/js/gtk.min.js

# Install hic2structure.py script
COPY submodules/3DStructure /opt/git/3DStructure
RUN cd /opt/git/3DStructure/src \
    && python3 setup.py install

# Copy files
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
