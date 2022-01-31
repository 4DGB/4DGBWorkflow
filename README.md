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
      data:     somefile.csv            (required)
    - name:     array two               (optional)
      data:     somefile.csv            (required)
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
