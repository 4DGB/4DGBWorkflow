# Docker commands 

1. Docker command: Report version

```
    docker run --rm --entrypoint ./scripts/report_version.sh 4dgb/4dgbworkflow-build
    docker run --rm --entrypoint ./scripts/report_version.sh 4dgb/4dgbworkflow-view
```

2. create template files with the workflow tool. This will create a directory called
   `example` with all the files in it that the tool needs. This can then be linked 
   in the next step.

```
    4dgbworkflow template example 
```


3. run the build image
```
    docker run -it --rm --user (uid:gid) --volume (host-input):/in  --volume (host-output):/out 4dgb/4dgbworkflow-build
``` 

4. run the view image
```
    docker run -it --rm --user (uid:gid) --volume (host-input):/in  4dgb/4dgbworkflow-build (port) (indir name)
``` 

