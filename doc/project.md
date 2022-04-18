# ``project.yaml`` Specification

The input to the workflow is a directory with a file named `workflow.yaml` or `project.yaml` with the following values:

```
project:
    name:       Project Name            (required)
    interval:   integer                 (optional, default=200000)
    annotation: file.gff3               (required)
    blackout:   [a list of bead IDs]    (optional)
    spector_correlation:    float       (optional global value)

sequence:
    name:       name of sequence        (required)
    data:       url of sequence         (required) 

tracks:
   - name: trackname_01
     file: input_01.csv
     columns: 
       - name: first
       - name: second
       - name: third
   - name: trackname_02
      file: input_01.csv
      columns:
        - name: first
        - name: second
        - name: fifth
          file: input_02.csv
    - ...

datasets:
    - name:     Name of first dataset   (optional)
      hic:      somefile.ext            (required)
      spector_correlation:  float       (optional override on global value)
    - name:     Name of second dataset  (optional)
      hic:      somefile.ext            (required)
      spector_correlation:  float       (optional override on global value)
```

## Explanation of values

- **`spector_correlation`** A metric that compares the correlation between the contact map computed for the input `hic` data and a contact map computed after the structure for the `hic` data has been computed by the MD simulation. The user can set this value globally, and override it per dataset. If the correlation threshold is not met, the MD simulation will be re-computed until that value is met. See [spector correlation](spector.md) for more information.
    

## Computed Values

Quantities that are computed from input.

```
num_beads = (num base pairs in sequence)/(project:interval)
```

- **`beads`** a 1-based `integer` array of size `num_beads`, with IDs that go from 1 to (num_beads - 1) The first bead is at sequence position `interval`. Therefore, the first `[1, (interval - 1)]` beads are not represented in the 3D structure file.

## File Specifications

### Structure `.csv` file

A structure `.csv` file is a three-column csv file in which the first line names the coordinate `[x,y,z]` of the structure point. The ID of the point is the number of the line, where the first data line is ID `1`, and the ids increment by one until the last line. The file has `num_beads + 1` lines, the first of which is the name of the coordinate. There are three coordinates, and their order is not specified, but all three must be present. 

```
x,y,z
0.0,0.0,0.0
0.1,0.1,0.1
0.2,0.2,0.2
...
```

### Track data

A track is specified by a name, an input csv file and a list of column names in that file. The columns listed map directly onto the datasets in the `datasets` section. (So that first column belongs to the first dataset, the second to the second dataset and so on). Optionally, you can override the filename specified in each column so that a track can have data from seperate files.

Track data is parsed using the [csv2tracks](../scripts/csv2tracks) script. For more details, see its [documentation](readme_csv2tracks.md)

### Annotation `csv` file

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
