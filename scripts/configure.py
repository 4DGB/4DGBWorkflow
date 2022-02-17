#!/usr/bin/env python3

#
# Given an input project directory, an output directory and the paths
# to some dependencies, generates a Ninja file to build a project bundled
# with the browser.
#
# Usage:
#   ./configure.py INPUT_DIR OUTPUT_DIR PATH_TO_BROWSER_REPO
#
# For this to work, we expect the script hic2structure.py to be in the PATH,
# as well as the LAMPPS executable, lmp. (And all required python modules should
# already be installed). This script is really only called inside the docker
# container, which ensures it's all set up properly, so it's not a problem.
#

import sys
from pathlib import Path
import typing as T
from typing import TypedDict

import yaml
from yaml import Loader

import ninja_syntax as ninja

########################
# PARSE / LOAD ARGUMENTS
########################

# Parse arguments
if len(sys.argv) < 4:
    print("Usage: /configure.py INPUT_DIR OUTPUT_DIR PATH_TO_BROWSER_REPO")
    exit(1)
[ INDIR, OUTDIR, BROWSER_DIR ] = map(Path, sys.argv[1:4])

# Find project file
search = [ INDIR.joinpath(f) for f in ['workflow.yaml', 'project.yaml'] ]
try:
    PROJECT_FILE = next( f for f in search if f.is_file() )
except StopIteration:
    print(f"Could not find project file. (Looked for '{search[0]}' and '{search[1]}')")
    exit(1)

# Load project file
with open(PROJECT_FILE, 'r') as f:
    SPEC = yaml.load(f, Loader=Loader)

OUTDIR = OUTDIR.resolve()
PROJECT_DIR = OUTDIR.joinpath('static','project')

########################
# PARSE PROJECT SPEC
########################

# 'Hic' represents an input Hi-C file alongside the files it will output
# when processed
Hic = TypedDict('HicFile', index=int, name=str, path=Path, outdir=Path, outfiles=T.List[Path])
def parse_hic(t: T.Tuple[int, T.Dict]) -> Hic:
    outdir = PROJECT_DIR.joinpath(f"lammps_{t[0]}")
    return {
        'index': t[0],
        'name': t[1]['name'],
        'path': INDIR.joinpath(t[1]['data']).resolve(),
        'outdir': outdir,
        'outfiles': [ outdir.joinpath('out', f) for f in 
            ['structure.csv', 'contactmap.tsv']
        ]
    }

HIC_FILES = list(map( parse_hic, enumerate(SPEC['datasets']) ))

OUTDIR.mkdir(exist_ok=True)
with open(OUTDIR.joinpath("build.ninja"), 'w') as f:

    ########################
    # WRITE NINJA RULES
    ########################

    WRITER = ninja.Writer(f, width=120)
    WRITER.comment("Build file generated by configure.py. DO NOT edit by hand!")

    # Run LAMMPS
    WRITER.rule(
        'lammps', 'hic2structure.py -vv --output ${out}/out --directory $out $in',
        description="Run LAMMPS Simulation"
    )

    # Generate project.json
    project_json_script = Path(__file__).parents[0].joinpath("project_yaml2json.py").resolve()
    WRITER.rule(
        'project', f'"{project_json_script}" "$in" "{PROJECT_DIR}"',
        description="Generate project.json"
    )

    # Copy files into output directory
    WRITER.rule(
        'copy', f'cp -rt "{OUTDIR}" $in',
        description="Copy files into project directory"
    )

    # Generate SQLite Database
    dbpop_script = BROWSER_DIR.joinpath('bin', 'db_pop')
    WRITER.rule(
        'dbpop', f'python3 "{dbpop_script}" "{PROJECT_DIR}" "{OUTDIR}"',
        description="Generate project database" #            👆
                                                # this second argument
                                                # to the db_pop script specifies 
                                                # the server directory, we
                                                # just need it to find the
                                                # 'version.md' file
    )

    ########################
    # WRITE NINJA BUILDS
    ########################

    # LAMMPS builds
    for hic in HIC_FILES:
        WRITER.build(
            outputs=str(hic['outdir']),
            implicit_outputs=[
                str(path) for path in hic['outfiles']
            ],
            rule='lammps',
            inputs=str(hic['path'])
        )

    # Generate project.json
    project_json = PROJECT_DIR.joinpath('project.json')
    WRITER.build(
        outputs=str(project_json),
        implicit=str(project_json_script),
        inputs=str(PROJECT_FILE.resolve()),
        order_only=[
            str(path) for h in HIC_FILES for path in h['outfiles']
        ],
        rule='project'
    )

    # Files to copy
    for path in [ 'gtkserver.py', 'gunicorn.conf.py', 'static', 'version.md' ]:
        inpath  = BROWSER_DIR.joinpath('server', path)
        outpath = OUTDIR.joinpath(path)
        WRITER.build(
            outputs=str(outpath),
            rule='copy',
            inputs=str(inpath)
        )

    # Generate database
    WRITER.build(
        outputs=str(PROJECT_DIR.joinpath('generated')),
        implicit=[str(dbpop_script), str(OUTDIR.joinpath('version.md'))],
        inputs=str(project_json),
        rule='dbpop'
    )
