# Documentation for 4DGB Workflow

The 4DGB Workflow provides an end-to-end workflow  for exploring 4D genomic data. The workflow and browser support analysis of sets of related data, for example, a time series of a chromosome, allowing scientists to visualize their genomic data in three dimensions.

Scientists provide input ``.hic`` data and track data, and a ``project.yaml`` file that defines the 

## Input data

The workflow accepts the following input data. Specifications for each type of data can be found in the following sections:

- ``.hic`` data files. These are used to compute and estimated 3D structure for the genomics data. 
- ``.csv`` files with track data.
- ``project.yaml`` file defining how the ``.hic`` and ``csv`` files are related.

### Data Specification: ``.hic``

Scientists can include ``.hic`` data as input used to compute the structure for the genome, and to provide a framework for 3D visualization of the track data defined in ``.csv`` files. For a complete description of how to prepare this input, see the [``.hic`` data preparation specification](hic_input.md).


### Data Specification: ``.csv``

``.csv`` files follow the format specification **rfc4180** [[1]](#1). In addition, the following constraints are applied:

- There shall be **NUM_BEADS + 1** rows in the file, the first of which is the names of the columns
- The first line of the file shall be names for the column, with each value treated as a string.
- All rows other than the first line are treated as float values 
- All values in a row must be a valid float value, the empty string, or ``NaN``, a string that results in a ``NaN`` value. 

### Data Specification: ``project.yaml``

The ``project.yaml`` file defines high level data for the workflow, and defines how ``.hic`` and ``csv`` files are related. For a complete description, see the [project file specification](project.md).

# References

[1] Y. Shafranovich, "Common Format and MIME Type for Comma-Separated Values (CSV) Files." RFC 4180, Oct. 2005. <a id="1"></a> 


