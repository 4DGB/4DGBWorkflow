#
# Dockerfile for the 'View' step of the workflow. Takes as input a project for the
# 4DGB Browser (as output by the 'build' step) and starts an instance of the browser
# running via Gunicorn
#

##############################
# Stage 1: Build gtk.min.js
##############################
FROM node:16-alpine as js

# Build Browser JS
COPY submodules/4DGB/client-js /opt/gtk
RUN cd /opt/gtk \
    && npm install \
    && NODE_ENV=production npx webpack \
    && cp gtk-dist/gtk.min.js /root/gtk.min.js

##############################
# Stage 2: Python dependencies
##############################

# Build all Python dependencies, placing the resulting wheels in WHEELDIR
FROM python:3.9.13-bullseye as python

COPY ./submodules/4DGB/server/requirements.txt ./requirements_server.txt
COPY ./view_stage/requirements.txt ./requirements_view.txt
RUN pip3 install wheel \
    && pip3 wheel -r requirements_server.txt --wheel-dir /root/wheels \
    && pip3 wheel -r requirements_view.txt --wheel-dir /root/wheels

# We also need Gunicorn
RUN pip3 wheel gunicorn --wheel-dir /root/wheels

##############################
# Stage 3: Release
##############################

FROM python:3.9.13-bullseye as release

# Install dependencies
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        cpanminus \
    && apt-get clean \
    && cpanm URI::Escape \
    && ln -s /usr/bin/python3 /usr/bin/python

# Install pre-compiled python dependencies
COPY ./submodules/4DGB/server/requirements.txt ./requirements_server.txt
COPY ./view_stage/requirements.txt ./requirements_view.txt
COPY --from=python /root/wheels ./wheels
RUN pip3 install --no-index --find-links=./wheels -r ./requirements_server.txt \
    && pip3 install --no-index --find-links=./wheels -r ./requirements_view.txt

# Copy files
COPY submodules/4DGB/server /opt/4dgb
COPY --from=js /root/gtk.min.js /opt/4dgb/static/gtk/js/
COPY ./view_stage/scripts ./scripts
COPY ./view_stage/gunicorn.conf.py ./gunicorn.conf.py

ENTRYPOINT [ "./scripts/entrypoint.sh" ]
