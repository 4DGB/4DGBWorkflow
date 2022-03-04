# 4DGB Workflow

A dockerized application implementing an end-to-end workflow to process Hi-C data files and displaying their structures in an instance of the [4DGB Browser](https://github.com/lanl/4DGB).

## Setting up Input Data

1. Create a directory to contain all of your input data. In it, create a `workflow.yaml` file with the following format:

```yaml
project:
  name: "My Project"
  interval: 200000 # optional (defaults to 200000)
  chromosome: X    # optional (defaults to 'X')
  threshold:  2.0  # optional (defaults to 2.0)

datasets:
  - name: "Data 01"
    hic:  "path/to/data_01.hic"
  - name: "Data 02"
    hic:  "path/to/data_02.hic"
```

*See the [File Specification Document](doc/file_specs.md) for full details on what can be included in the input data*

2. Checkout submodules

```sh
git submodule update --init
```

3. Build the Docker image.

```sh
docker build -t 4dgbworkflow .
```

4. Run the browser!

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
