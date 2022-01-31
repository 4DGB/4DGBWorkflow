# 4DGB Workflow

repository init

# Input Parameters

The input to the workflow is a yaml file with the following values:

```
project:
    name:       Project Name            (required)
    interval:   200000                  (required)
    annotation: file.gff3               (required)
    blackout:   [a list of bead IDs]    (optional)

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


