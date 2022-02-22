# 4DGB Workflow

A dockerized application implementing an end-to-end workflow to process Hi-C data files and displaying their structures in an instance of the [4DGB Browser](https://github.com/lanl/4DGB).

## Setting up Input Data

1. Create a directory to contain all of your input data. In it, create a `workflow.yaml` file with the following format:

```yaml
project:
  name: "My Project"
  # 'interval' is optional (defaults to 200000)
  interval: 200000

datasets:
  - name: "Data 01"
    hic:  "path/to/data_01.hic"
  - name: "Data 02"
    hic:  "path/to/data_02.hic"
```

*See the [File Specification Document](doc/file_specs.md) for full details on what can be included in the input data*

2. Build the Docker image. **NOTE:** For now, this requires access to a private GitHub repository, so a little magic is needed to build it: You must have a Docker version capable of using BuildKit, and a running ssh agent with keys that will let you access the private repo. With that, you can build the image with this command:

```sh
DOCKER_BUILDKIT=1 docker build -t 4dgbworkflow --ssh default .
```

3. Run the browser!

```sh
./run_project /path/to/project/directory/
```

Example output:
```
$ ./run_project ./my_project
[>]: Building project...
[3/7] Copy files to project directory

        #
        # Ready!
        # Open your web browser and visit:
        # http://localhost:8000/compare.html?gtkproject=my_project
        #
        # Press [Ctrl-C] to exit
        #
```

If this is the first time running a project, this may take a while, since it needs to run a molecular dynamics simulation with LAMMPS on your input data. The next time you run it, it won't need to run the simulation again. If you update the input files, then the simulation will automatically be re-run!
