# Input Parameters

The input to the workflow is a directory with a file named `workflow.yaml` or `project.yaml` with the following values:

```
project:
    name:       Project Name            (required)
    interval:   integer                 (optional, default=200000)
    annotation: file.gff3               (required)
    blackout:   [a list of bead IDs]    (optional)

sequence:
    name:       name of sequence        (required)
    data:       url of sequence         (required) 

tracks:
    - name:     tracks one              (optional)
      data:     somefile.yaml           (required)
    - name:     tracks two              (optional)
      data:     somefile.yaml           (required)
    - ...

datasets:
    - name:     Name of first dataset   (optional)
      hic:      somefile.ext            (required)
    - name:     Name of second dataset  (optional)
      hic:      somefile.ext            (required)
```

# Computed Values

Quantities that are computed from input.

```
num_beads = (num base pairs in sequence)/(project:interval)
```

- **`beads`** a 1-based `integer` array of size `num_beads`, with IDs that go from 1 to (num_beads - 1) The first bead is at sequence position `interval`. Therefore, the first `[1, (interval - 1)]` beads are not represented in the 3D structure file.

# File Specifications

## Structure `.csv` file

A structure `.csv` file is a three-column csv file in which the first line names the coordinate `[x,y,z]` of the structure point. The ID of the point is the number of the line, where the first data line is ID `1`, and the ids increment by one until the last line. The file has `num_beads + 1` lines, the first of which is the name of the coordinate. There are three coordinates, and their order is not specified, but all three must be present. 

```
x,y,z
0.0,0.0,0.0
0.1,0.1,0.1
0.2,0.2,0.2
...
```

## Track data

A track is specified by two files: a `track.yaml` file (specifying metadata about the track) and a file containing the data (either a compressed python `track.npz` or text-based `track.csv` file). 

Specification of the `track.yaml` file:
```
name    : name of the track
type    : structure
version : version of the track metadata file
data    :
    type    : string value, one of [int, float]
    dim     : integer (number of sets of values)
    length  : number of elements in each set of values 
    min     : min value over all track 
    max     : max value over all track 
    values :
        - id : name needed to retrieve data 
          url: relative path to the data file 
        - id : name needed to retrieve data 
          url: relative path to the data file 
        ...
```

The `id` used to retrieve the data is either the name used by python's compressed array reader to access the data in the `track.npz` file, or the column name of the data in the `track.csv` file.

An `track.csv` file looks like this (where `time_0` and `time_1` are the `value:id` names:

```
time_0,time_1
0.0,0.0
0.1,0.0001
0.2,0.0002
0.3,0.0003
...
```

## Annotation `csv` file

A general file for providing annotations for the workflow's sequence.

```
name:   a string naming the annotation
start:  the 1-based ID of the start position in the sequence
end:    the 1-based ID of the end position in the sequence
id:     an identified for the annotation
type:   one of [gene, megadomain, or other user-defined type]
```

Example of the `annotation.csv` file:
```
name,start,end,id,type
first,100000,200000,CEN,megadomain
second,200000,300000,CEN,megadomain
```
