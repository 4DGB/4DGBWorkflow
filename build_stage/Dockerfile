#
# Dockerfile for the 'build' stage of the Workflow. That is, the part that
# takes an input project, runs LAMMPS and outputs an project for the browser
#
# NOTE: This image should be built from the root directory of the repository
# not from the 'build_stage' directory.
#

##############################
# Stage 1: Python dependencies
##############################

# Build all Python dependencies, placing the resulting wheels in WHEELDIR
FROM python:3.10.4-bullseye as python

COPY ./submodules/3DStructure/requirements.txt ./requirements_hic.txt
COPY ./build_stage/requirements.txt ./requirements_workflow.txt
RUN pip3 install wheel \
    && pip3 wheel -r requirements_hic.txt --wheel-dir /root/wheels \
    && pip3 wheel -r requirements_workflow.txt --wheel-dir /root/wheels

# Install hic2structure module
COPY submodules/3DStructure /opt/3DStructure
RUN cd /opt/3DStructure \
    && pip3 wheel . --wheel-dir /root/wheels

##############################
# Stage 2: Release
##############################

FROM python:3.10.4-bullseye as release

# Install dependencies
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    lammps \
    && apt-get clean \
    && ln -s /usr/bin/python3 /usr/bin/python

# Install pre-compiled python dependencies
COPY ./submodules/3DStructure/requirements.txt ./requirements_hic.txt
COPY ./build_stage/requirements.txt ./requirements_workflow.txt
COPY --from=python /root/wheels ./wheels
RUN pip3 install --no-index --find-links=./wheels -r ./requirements_hic.txt \
    && pip3 install --no-index --find-links=./wheels -r ./requirements_workflow.txt \
    && pip3 install --no-index --find-links=./wheels hic2structure 

# Copy files
COPY ./build_stage/scripts ./scripts
COPY ./version.txt ./version.txt

# We also need the db_pop script from the browser
# (which itself needs the browser's version file in a certain position
# relative to it)
COPY ./submodules/4DGB/bin/db_pop /opt/4DGB/bin/db_pop
COPY ./submodules/4DGB/server/version.md /opt/4DGB/server/version.md
ENV PATH ${PATH}:/opt/4DGB/bin

ENTRYPOINT [ "./scripts/entrypoint.sh" ]
