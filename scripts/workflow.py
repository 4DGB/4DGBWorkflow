#!/usr/bin/env python3

#
# This script implements the brunt of the workflow. That is, taking a project
# directory as input, parsing the project.yaml/workflow.yaml file, running the
# LAMMPS simulations, etc. and ultimatly outputting a directory with a "project"
# in the format the 4DGB Browser expects.
#
# This script runs *inside* the Docker container. Specifically, it's called by
# the docker-setup.sh script and is run with the permissions of the user who
# launched the container.
#
# Usage:
#   ./workflow.py INPUT_DIR OUTPUT_DIR PATH_TO_BROWSER_REPO
#
#   (we need the path to the browser repository 'cuz we gotta run the
#    db_pop script that's in there)
#

from cgitb import text
import sys
import os
import copy
import json
import shlex
import subprocess
import multiprocessing
import tempfile
import shutil
from pathlib import Path

import yaml
from yaml import Loader

from hic2structure_lib.hic import HIC, HICError
from hic2structure_lib.lammps import run_lammps, LAMMPSError
from hic2structure_lib.out import write_structure, write_contacts
from hic2structure_lib.contact import find_contacts

####################################
#
#    CONSTANTS
#
###################################

# Path to template for output project.json
TEMPLATE_FILE = Path(__file__).parents[0].joinpath('project_template.json')

with open(TEMPLATE_FILE, 'r') as f:
    BROWSER_PROJECT_TEMPLATE: dict = json.load(f)

# Default values for input project specification
DEFAULT_PROJECT = {
    'project': {
        'name': "Untitled",
        'interval': 200000,
        'chromosome': 'X',
        'threshold': 2.0,
        'blackout': [],
        'timesteps': 1000000,
        'bond_coeff': 55
    },
    'datasets': [],
    'tracks': []
}

# Set of keys under 'project' in configuration that constitute the settings
# for processing Hi-C files. A change in any of these means that the file will
# need to be processed again.
SETTINGS_KEYS = [
    'interval',
    'chromosome',
    'threshold',
    'timesteps',
    'bond_coeff'
]

# Parse arguments
if len(sys.argv) < 4:
    print("Usage: ./workflow.py INPUT_DIR OUTPUT_DIR PATH_TO_BROWSER_REPO")
    exit(1)

# Input/Output directories
[ INDIR, OUTDIR, BROWSER_DIR ] = map(
    lambda dir: Path(dir).resolve(),
    sys.argv[1:4]
)

####################################
#
#    HELPER FUNCTIONS
#
###################################

def deep_update(a: dict, b: dict) -> dict:
    '''
    Recrusive update on two dicts. The first argument (a) is modified
    '''
    for (k, v) in b.items():
        if isinstance(v, dict):
            a[k] = deep_update( a.get(k, {}), v )
        else:
            a[k] = v 
    return a

####################################
#
#    WORKFLOW FUNCTIONS
#
###################################

def load_project_spec() -> dict:
    '''
    Load the project.yaml or workflow.yaml (either filename is acceptable)
    for the input project
    '''
    # Find and load file
    search = [ INDIR.joinpath(f) for f in ['workflow.yaml', 'project.yaml'] ]
    try:
        project_file = next( f for f in search if f.is_file() )
    except StopIteration:
        print(f"Could not find project file. (Looked for '{search[0]}' and '{search[1]}')")
        exit(1)

    with open(project_file, 'r') as f:
        project_input = yaml.load(f, Loader=Loader)
    
    # Resolve default settings
    return deep_update(
        copy.deepcopy(DEFAULT_PROJECT),
        project_input
    )

########################
# Hi-C Processing
########################

def process_hic(settings: dict, input: Path, outdir: Path):
    '''
    Process a Hi-C file. The run is
    performed in a temporary directory, with the results being copied to
    the provided output directory. If the output directory has a later
    last-modified time than the input file, it won't be run, though a
    change in the settings can override that.

    Returns a dict of Paths to the various output files
    '''
    log_name = 'sim.log'
    log_file       = outdir.joinpath(log_name)
    settings_file  = outdir.joinpath('settings.json')
    structure_file = outdir.joinpath('structure.csv')
    contact_file   = outdir.joinpath('contactmap.tsv')

    # Print info about current processing run
    def info(message):
        print(f"  \033[1m[\033[94m!\033[0m\033[1m {input.name}]:\033[0m {message}")

    # Print error for current processing run
    def error(message):
        print(f"  \033[1m[\033[31mX\033[0m\033[1m {input.name}]:\033[0m {message}")

    # Load the settings used for the last run (if there are any)
    try:
        with open(settings_file, 'r') as f:
            previous_settings = json.load(f)
    except:
        previous_settings = None

    # The run is considered "out-of-date" and needs to be run again
    # if the input was modified more recently, or if the settings
    # have changed
    out_of_date = (not outdir.exists()) or \
       ( os.path.getmtime(input) > os.path.getmtime(outdir) ) or \
       ( settings != previous_settings )

    if out_of_date:
        try:
            info("Processing Hi-C file...")
            outdir.mkdir(parents=False, exist_ok=True)

            # Run in temp directory
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)

                # Read records from Hi-C file
                try:
                    data = HIC(input)
                    records = data.get_contact_records(
                        settings['chromosome'],
                        settings['interval'],
                        settings['threshold']
                    )
                except HICError as e:
                    error(f"Error reading contact records: {e}")
                    raise e

                # Run LAMMPS
                try:
                    info("Running LAMMPS...")
                    lammps_out = run_lammps(
                        tmpdir_path,
                        records,
                        timesteps=settings['timesteps'],
                        bond_coeff=settings['bond_coeff'],
                    )
                except LAMMPSError as e:
                    log_path = log_file.relative_to(OUTDIR)
                    error(f"Error running LAMMPS! A log may be available in the output directory in {log_path}")
                    raise e
                finally:
                    # Copy LAMMPS log file
                    shutil.copy2( tmpdir_path.joinpath(log_name), log_file )

                # Write output
                info("LAMMPS Finished! Saving output...")
                contacts = find_contacts(lammps_out)
                write_structure(structure_file, lammps_out)
                write_contacts(contact_file, contacts)

            # (Temporary directory destroyed)

            # Save settings that were used
            with open(settings_file, 'w') as f:
                json.dump(settings, f)

            # Update last-modified time on output directory
            outdir.touch(exist_ok=True)

        except Exception as e:
            error(f"An error occured processing the Hi-C file: {e}")
            # If an error occured, we delete the settings file so that
            # the next run will always be attempted
            settings_file.unlink(missing_ok=True)
            raise e

    return {
        'structure':  structure_file,
        'contactmap': contact_file,
        'log':        log_file
    }

def process_datasets(settings: dict, inputs: list, outdir: Path) -> list:
    '''
    Process the given datasets from the project. Datasets are processed in
    parallel.

    Returns a dict with the paths to the output files for each input dataset.
    '''

    with multiprocessing.Pool(processes=4) as pool:
        input_args = [
            ( settings, INDIR.joinpath(dataset['data']), outdir.joinpath(f'lammps_{i}') ) 
            for i,dataset in enumerate(inputs) 
        ]
        results = pool.starmap(process_hic, input_args)

    return results

########################
# PROJECT.JSON GENERATION
########################

def contact_map_entry(project: dict, result: tuple) -> dict:
    '''
    Create an entry for the project.json's 'md-contact-map' array for the given
    the result (represented as a tuple of id, input dataset and output paths)
    '''
    return {
        'id': result[0],
        'version': "1.0",
        'url': str( result[2]['contactmap'].relative_to(OUTDIR) ),
        'interval': project['project']['interval']
    }

def structure_entry(project: dict, result: tuple) -> dict:
    '''
    Create an entry for the project.json's 'structure' array for the given
    the result (represented as a tuple of id, input dataset and output paths)
    '''
    # We need to know the number of segments in the structure, which we can
    # get by counting the lines of the output csv file
    wc = subprocess.run(['wc', '--lines', result[2]['structure']],
        capture_output=True, check=True, text=True
    )
    num_segments = int(wc.stdout.split()[0]) - 1

    return {
        'id': result[0],
        'type': {
            'version': "1.0",
            'name': "LAMMPS"
        },
        'md-contact-map': result[0],
        'unmapped_segments': project['project']['blackout'],
        'num_segments': num_segments,
        'url': str( result[2]['structure'].relative_to(OUTDIR) ),
        'interval': project['project']['interval']
    }

def dataset_entry(project: dict, result: tuple) -> dict:
    '''
    Create an entry for the project.json's 'dataset' array for the given
    the result (represented as a tuple of id, input dataset and output paths)
    '''
    return {
        'id': result[0],
        'name': result[1]['name'],
        'structure' : {
            'id': result[0],
            'md-contact-map': result[0]
        },
        'epigenetics': result[0]
    }

def track_data_entries(tracks: list) -> list:
    '''
    Create an entry for the project.json's 'array' field for the given
    track data from the project input.
    '''
    return [{
        'id': i,
        'url': track['data']
    }
    for i,track in enumerate(tracks)]

def make_project_json(project: dict, results: list) -> dict:
    '''
    Create a dict for the project.json for the output project, given the input
    project and a list of results from the Hi-C processing
    '''
    out_project = copy.deepcopy(BROWSER_PROJECT_TEMPLATE)

    out_project['project']['name'] = project['project']['name']
    out_project['project']['interval'] = project['project']['interval']

    #out_project['data']['array'] = track_data_entries(project['tracks'])

    for result in results:
        out_project['data']['md-contact-map'].append( contact_map_entry(project, result) )
        out_project['data']['structure'].append( structure_entry(project, result) )
        out_project['datasets'].append( dataset_entry(project, result) )

    return out_project

########################
# BROWSER
########################

def run_db_pop(project_dir: Path):
    '''
    Run the browser's db_pop script to generate the project database
    '''
    db_pop = BROWSER_DIR.joinpath('bin', 'db_pop')
    server_dir = BROWSER_DIR.joinpath('server')

    run = subprocess.run([db_pop, OUTDIR, server_dir],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )

    try:
        run.check_returncode()
    except subprocess.CalledProcessError as e:
        print(run.stdout)
        print("Error creating project database!")
        raise e

####################################
#
#    MAIN
#
###################################

def main():
    multiprocessing.set_start_method('spawn')

    project = load_project_spec()

    OUTDIR.mkdir(exist_ok=True)

    # Process Hi-C data
    process_settings = { k: project['project'][k] for k in SETTINGS_KEYS }
    process_outputs = process_datasets(process_settings, project['datasets'], OUTDIR )

    # A list of tuples matching ids and input datasets with the paths to
    # their output files
    dataset_results = list( zip(
        range( len(process_outputs) ),
        project['datasets'],
        process_outputs
    ))

    # Save browser project.json
    out_project = make_project_json(project, dataset_results)
    with open(OUTDIR.joinpath("project.json"), 'w') as f:
        json.dump(out_project, f)

    # Run db_pop
    run_db_pop(OUTDIR)

if __name__ == '__main__':
    main()

