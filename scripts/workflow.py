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
#   ./workflow.py INPUT_DIR OUTPUT_DIR [PATH_TO_BROWSER_REPO]
#
#   (if 'db_pop' is in the PATH, then the last argument is not needed)
#

from asyncio.subprocess import STDOUT
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

from hic2structure.types import Settings
from hic2structure.hic import HIC
from hic2structure.lammps import run_lammps
from hic2structure.contacts import find_contacts, contact_records_to_set
from hic2structure.out import write_contact_records, write_structure, write_contact_set

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
        'count_threshold': 2.0,
        'distance_threshold': 3.3,
        'blackout': [],
        'timesteps': 1000000,
        'bond_coeff': 55
    },
    'datasets': [],
    'tracks': []
}

# Parse arguments
if len(sys.argv) < 3:
    print("Usage: ./workflow.py INPUT_DIR OUTPUT_DIR [PATH_TO_BROWSER_REPO]")
    exit(1)

# Input/Output directories
[ INDIR, OUTDIR ] = map(
    lambda dir: Path(dir).resolve(),
    sys.argv[1:3]
)
if len(sys.argv) > 3:
    BROWSER_DIR = Path(sys.argv[3])
else:
    BROWSER_DIR = None

# Find project input file
search = [ INDIR.joinpath(f) for f in ['workflow.yaml', 'project.yaml'] ]
# Find and load file
try:
    INPUT_FILE = next( f for f in search if f.is_file() )
except StopIteration:
    print(f"Could not find project file. (Looked for '{search[0]}' and '{search[1]}')")
    exit(1)

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
    with open(INPUT_FILE, 'r') as f:
        project_input = yaml.load(f, Loader=Loader)
    
    # Resolve default settings
    return deep_update(
        copy.deepcopy(DEFAULT_PROJECT),
        project_input
    )

def settings_from_project(project_spec: dict) -> Settings:
    project: dict = project_spec['project']
    return {
        'chromosome': project['chromosome'],
        'count_threshold':  project['count_threshold'],
        'distance_threshold':  project['distance_threshold'],
        'resolution': project['interval'],
        'bond_coeff': project['bond_coeff'],
        'timesteps':  project['timesteps']
    }

########################
# Hi-C Processing
########################

def process_hic(settings: Settings, input: Path, outdir: Path):
    '''
    Process a Hi-C file. The run is
    performed in a temporary directory, with the results being copied to
    the provided output directory. If the output directory has a later
    last-modified time than the input file, it won't be run, though a
    change in the settings can override that.

    Returns a dict of Paths to the various output files
    '''

    results = {
        'settings':   (outdir/'settings.json').resolve(),
        'structure':  (outdir/'structure.csv').resolve(),
        'contactmap': (outdir/'contactmap.tsv').resolve(),
        'inputset':   (outdir/'inputset.tsv').resolve(),
        'outputset':  (outdir/'outputset.tsv').resolve(),
        'log':        (outdir/'sim.log').resolve(),
    }

    # Print info about current processing run
    def info(message):
        print(f"  \033[1m[\033[94m!\033[0m\033[1m {input.name}]:\033[0m {message}")

    # Print error for current processing run
    def error(message):
        print(f"  \033[1m[\033[31mX\033[0m\033[1m {input.name}]:\033[0m {message}")

    # Process a single Hi-C file
    def run():
        outdir.mkdir(parents=True, exist_ok=True)

        # Read Hi-C and run LAMMPS
        hic = HIC(input)
        input_records = hic.get_contact_records(settings)
        input_set = contact_records_to_set(input_records)
        lammps_data = run_lammps(input_set, settings, copy_log_to=results['log'])
        last_timestep = lammps_data[ sorted(lammps_data.keys())[-1] ]
        output_set = find_contacts(last_timestep, settings)

        # Save output data
        write_structure(results['structure'], last_timestep)
        write_contact_records(results['contactmap'], input_records)
        write_contact_set(results['inputset'], input_set)
        write_contact_set(results['outputset'], output_set)
        pass

    # Load the settings used for the last run (if there are any)
    try:
        with open(results['settings'], 'r') as f:
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

            try:
                run()
            except Exception as e:
                log_path = results['log'].relative_to(OUTDIR)
                error(f"Error running LAMMPS! A log may be available in the output directory in {log_path}")
                raise e

            # Save settings that were used
            with open(results['settings'], 'w') as f:
                json.dump(settings, f)

            # Update last-modified time on output directory
            outdir.touch(exist_ok=True)

        except Exception as e:
            error(f"An error occured processing the Hi-C file: {e}")
            # If an error occured, we delete the settings file so that
            # the next run will always be attempted
            results['settings'].unlink(missing_ok=True)
            raise e

    return results

def process_datasets(settings: Settings, inputs: list[dict], outdir: Path) -> list[dict]:
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

def contact_map_entry(project: dict, result: tuple[int,dict,dict]) -> dict:
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

def structure_entry(project: dict, result: tuple[int,dict,dict]) -> dict:
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

def dataset_entry(project: dict, result: tuple[int,dict,dict]) -> dict:
    '''
    Create an entry for the project.json's 'dataset' array for the given
    the result (represented as a tuple of id, input dataset and output paths)
    '''
    return {
        'id': result[0],
        'name': result[1]['name'],
        'structure' : {
            'id': result[0],
            'md-contact-map': result[0],
            'input_set':  str( result[2]['inputset'].relative_to(OUTDIR) ),
            'output_set': str( result[2]['outputset'].relative_to(OUTDIR) )
        },
        'epigenetics': result[0]
    }

def track_data_entries(tracks: list[dict]) -> list:
    '''
    Create an entry for the project.json's 'array' field for the given
    track data from the project input.
    '''
    return [{
        'id': i,
        'url': f"tracks/{track['name']}/track.json"
    }
    for i,track in enumerate(tracks)]

def make_project_json(project: dict, results: list[tuple[int,dict,dict]]) -> dict:
    '''
    Create a dict for the project.json for the output project, given the input
    project and a list of results from the Hi-C processing
    '''
    out_project = copy.deepcopy(BROWSER_PROJECT_TEMPLATE)

    out_project['project']['name'] = project['project']['name']
    out_project['project']['interval'] = project['project']['interval']

    out_project['data']['array'] = track_data_entries(project['tracks'])

    for result in results:
        out_project['data']['md-contact-map'].append( contact_map_entry(project, result) )
        out_project['data']['structure'].append( structure_entry(project, result) )
        out_project['datasets'].append( dataset_entry(project, result) )

    return out_project

########################
# TRACK DATA
########################

def make_tracks():
    '''
    Call csv2tracks to generate track data for the project
    '''
    csv2tracks = Path(__file__).parents[0].joinpath('csv2tracks')
    run = subprocess.run([
        csv2tracks,
        '--workflow', INPUT_FILE,
        '--destination', OUTDIR.joinpath('tracks'),
        '--relative', OUTDIR,
        '--verbose'
    ],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )

    try:
        run.check_returncode()
    except subprocess.CalledProcessError as e:
        print(run.stdout)
        print("Error creating tracks!")
        raise e

########################
# BROWSER
########################

def run_db_pop():
    '''
    Run the browser's db_pop script to generate the project database
    '''
    db_pop = shutil.which('db_pop')
    if db_pop is None:
        if BROWSER_DIR is None:
            raise EnvironmentError("Could not find db_pop script")
        else:
            db_pop = BROWSER_DIR.joinpath('bin', 'db_pop')

    run = subprocess.run([db_pop, OUTDIR],
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
    process_settings = settings_from_project(project)
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

    if ('tracks' in project) and len(project['tracks']) > 0:
        make_tracks()

    run_db_pop()

if __name__ == '__main__':
    main()
