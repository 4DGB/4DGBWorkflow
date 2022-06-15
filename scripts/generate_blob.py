#!/usr/bin/env python3

#
# Print a chunk of base85-encoded text
# containing a gzipped tar archive of the example
# project, to be inserted into the 4dgb-workflow script
#
# Note that the output will have newlines inserted into it,
# these must be removed before decoding
#

import sys
import subprocess
import re
from base64 import b85encode
from pathlib import Path

DIRECTORY=Path.joinpath(Path(__file__).parent, '..', 'example_project/')
FILES=[
    'chr22.tracks.12.csv',
    'chr22.tracks.csv',
    'ENCLB571GEP.chr22.200kb.h5.hic',
    'ENCLB870JCZ.chr22.200kb.12.h5.hic',
    'project.yaml'
]

if not DIRECTORY.is_dir():
    print("Error: Could not find example_project/ directory.", file=sys.stderr)
    exit(1)

command = [ 'tar', '-C', DIRECTORY, '-cvJ', *FILES]
run = subprocess.run(command, capture_output=True)

try:
    run.check_returncode()
except subprocess.CalledProcessError as e:
    print(run.stderr.decode('utf-8'))
    print(f"Error: tar failed with exit code: {run.returncode}", file=sys.stderr)
    exit(1)

print(run.stderr.decode('utf-8'), file=sys.stderr)

encoded = b85encode(run.stdout, pad=False).decode('ascii')
with_newlines = re.sub(r"(.{120})", r"\1\n", encoded, 0, re.DOTALL)

print(with_newlines)
