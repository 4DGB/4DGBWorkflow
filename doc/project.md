# Project Specification

The input to the workflow is a directory containing all of the input files alongside a file, `workflow.yaml` or `project.yaml` specifying the role of the files.

Please see the [example_project](../example_project/) directory for an example of such a project, and pay particular attention to the [project.yaml](../example_project/project.yaml) in it.

## `project.yaml` Fields

(All file paths specified in the `project.yaml` file are considered relative to the project directory)
### `workflow` (optional)

- `version`: Used to specify the version of the workflow the project is intended for.

### `project` (required)

Project settings. For the most part, these are used to adjust how the `.hic` files will be read
and how LAMMPS will be run.

- `name`: User-friendly name of the project
- `interval`: The bin resolution in the `.hic` files to choose. **Default:** 200000
- `chromosome`: The name of the chromosome in the `.hic` files to choose. **Default:** 'X'
- `count_threshold`: Used to filter the contacts records from the `.hic` files to use in the simulation. Only records with a count higher than this will be used. **Default:** 2.0
- `distance_threshold`: Used to filter the contact records from the structure output by the simulation. Only segments closer to each other than this value will be used (This only affects the display on the "intermediate data" page in the browser. The 3D structure is not filtered). **Default:** 3.3
- `blackout`: A list of 2-long arrays, each specifying a range of segments in the structure. These segments are considered "unmapped" and will not be visible by default in the browser.
- `bond_coeff`: The FENE bond coefficient used in the LAMMPS simulation. If LAMMPS fails with a "bad FENE bond" error, try increasing this value. **Default:** 55

### `datasets` (required)

A list of the two datasets to be compared in the browser. Each one is an object with the following fields:

- `name`: User-friendly name for the dataset
- `data`: Path to the `.hic` file for the dataset.

### `tracks` (optional)

Specify "tracks" of data. These are 1-dimensional sets of data that can be mapped along the structure. The `tracks` field is a list of individual track specifications. There can be as many tracks as you like, each one is specified with the following fields:

Tracks are represented in `.csv` files. Each track specifies a file, and the name of a column within that file.

- `name`: Name of the track
- `file`: Path to a `.csv` file containing the track data.
- `columns`: List of two column specifications. The first one is mapped onto the first dataset, and the second onto the second dataset. Each of these have the following fields:
    - `name`: Name of the column
    - `file`: (optional) Used to override the file specified above.

### `annotaions` (optional)

Annotations are sections of the structure that you can tag with names. They can come from two different sources: Genes specified in `.gff` file, or arbitary features described in a `.csv` file.

- `genes`: Specify a source of annotations from a `.gff` flie.
    - `file`: Path to `.gff` file to use.
    - `description`: Description of the file/annotations
- `features`: Specify a source of annotations from `.csv` file. This file must have the columns, `name`, `start`, `end`, `id`, and `type`. See the [features.csv](../example_project/features.csv) in the example project for an idea of how it works. The `id` and `type` columns can be whatever you like
  - `file`: Path to the `.csv` file to use.
  - `description`: Description of the file/annotations

### `bookmarks` (optional)

In addition to the annotations specified above, you can "bookmark" your favorite locations or annotations, and they will appear in the drop-down menus to select them in the browser.

- `locations`: A list of 2-long arrays, each specifying a range of locations (in basepairs) to bookmark.
- `features`: A list of names of annotations (either from the `genes` or `features`) to bookmark.
