# 4DGB Workflow

A repository of an end-to-end workflow that takes hic and other data 
as input, creates a 3D structure, and starts a 4DGB server.


# Input Parameters

The input to the workflow is a file named `workflow.yaml` with 
the following values:

```
project:
    name:       Project Name            (required)
    interval:   integer                 (optional, default=200000)
    annotation: file.gff3               (required)
    blackout:   [a list of bead IDs]    (optional)

sequence:
    - name:     name of sequence        (required)
    - data:     url of sequence         (required) 

arrays:
    - name:     array one               (optional)
      data:     somefile.json           (required)
    - name:     array two               (optional)
      data:     somefile.json           (required)
    - ...

datasets:
    - name:     Name of first dataset   (required)
      hic:      data01.hic              (required)
    - name:     Name of second dataset  (required)
      hic:      data02.hic              (required)
```

# Computed Values

Quantities that are computed from input.

```
num_beads = (num base pairs in sequence)/(project:interval)
```

- **`beads`** a 1-based `integer` array of size `num_beads`, with IDs
  that go from 1 to (num_beads - 1) The first bead is at sequence position 
  `interval`. Therefore, the first `[1, (interval - 1)]` beads are not 
  represented in the 3D structure file.

# File Specifications

## Structure `.csv` file

A structure `.csv` file is a three-column csv file in which the first line
names the coordinate `[x,y,z]` of the structure point. The ID of the point is 
the number of the line, where the first data line is ID `1`, and the ids
increment by one until the last line. The file has `num_beads + 1` lines, the first of which is the name of the coordinate. There are three coordinates,
and their order is not specified, but all three must be present. 

```
x,y,z
0.0,0.0,0.0
0.1,0.1,0.1
0.2,0.2,0.2
...
```

## Array data

An array is specified by two files: a `array.json` file and a `array.npz` 
file. The `array.json` file is metadata about the array, and the 
`array.npz` file is a compressed python python file containing float
arrays as specified in the associated `array.json`.

Specification of the `array.json` file:
```
{
"name"      : "name of the array",  
"type"      : "structure",
"version"   : "version of the array metadata file",
"data"      : {
    "type"  : "int",
    "dim"   : 1,
    "min"   : 1,
    "max"   : 833,
    "values" : [
        {
            "id"  : "name expected by python when extracting data",
            "url" : "relative path to the npz file"
        },
        {
            "id"  : "name expected by python when extracting data",
            "url" : "relative path to the npz file"
        }
    ]
}
}
```

