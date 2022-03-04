#!/usr/bin/env python3

#
# Given a YAML file for a project (the one defined in this repository), and
# an output project directory, write a project.json file for the 4DGB Browser
#
# This is run by the build process *after* the LAMMPS simulation, because
# this script needs to read some information from the resulting
# structure and contact map files to put in the project.json
#
# Usage:
#    ./project_yaml2json.py path/to/workflow.yaml path/to/project_dir
#

import sys
import json
import subprocess
from pathlib import Path

import yaml
from yaml import Loader

if len(sys.argv) < 3:
    print("Usage: ./project_yaml2json.py path/to/project.yaml path/to/project/dir")
    exit(1)

# Output starts from the template in project_template.json
TEMPLATE_FILE = Path(__file__).parents[0].joinpath('project_template.json')
with open(TEMPLATE_FILE, 'r') as f:
    OUTPUT = json.load(f)

# Load input
with open(sys.argv[1], 'r') as f:
    INPUT = yaml.load(f, Loader=Loader)
INPROJ=INPUT['project']

# Get output directory
OUTDIR=Path(sys.argv[2]).resolve()
if not OUTDIR.is_dir():
    print(f"Output '{OUTDIR}' is not a directory.")
    exit(1)

# Set project parameters
OUTPUT['project']['name'] = INPROJ['name']

INTERVAL = INPROJ.get('interval', 200000)
OUTPUT['project']['interval'] = INTERVAL

BLACKOUT = INPROJ.get('blackout', [])

# Fill out data sets
# The actual files referenced here are generated in the build process
# from the files specified in the input
for (i, dataset) in enumerate(INPUT['datasets']):

    structure_file  = OUTDIR.joinpath(f'lammps_{i}', 'out', 'structure.csv')
    contactmap_file = OUTDIR.joinpath(f'lammps_{i}', 'out', 'contactmap.tsv')

    # We need the number of segments in the structure, which we can get by
    # counting the lines of its csv file
    wc = subprocess.run(['wc', '--lines', structure_file],
        capture_output=True, check=True, text=True
    )
    num_segments = int(wc.stdout.split()[0]) - 1

    # Add contact map info
    OUTPUT['data']['md-contact-map'].append({
        'id': i,
        'version': "1.0",
        'url': str(contactmap_file.relative_to(OUTDIR)),
        'interval': INTERVAL
    })

    # Add structure info
    OUTPUT['data']['structure'].append({
        'id': i,
        'type': {
            'version': "1.0",
            'name': "LAMMPS"
        },
        'md-contact-map': i,
        'unmapped_segments': BLACKOUT,
        'num_segments': num_segments,
        'url': str(structure_file.relative_to(OUTDIR)),
        'interval': INTERVAL
    })

    # Add dataset entry
    OUTPUT['datasets'].append({
        'id': i,
        'name': dataset['name'],
        'structure': {
            'id': i,
            'md-contact-map': i,
        },
        'epigenetics': i
    })

OUTFILE=OUTDIR.joinpath("project.json")
with open(OUTFILE, 'w') as f:
    json.dump(OUTPUT, f)
