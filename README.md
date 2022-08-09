# 4DGB Workflow

![](doc/workflow.png)

A dockerized application implementing an end-to-end workflow to process Hi-C data files and displaying their structures in an instance of the [4D Genome Browser](https://github.com/lanl/4DGB).

The workflow takes ```.hic``` data, processes the data and creates a running server that can be used to view the data with a web browser. The system takes advantage of previous runs, so if you've already computed some data, it won't be recomputed the next time the workflow is run. 

## Setting up Input Data

1. Create a directory to contain all of your input data. In it, create a `workflow.yaml` file with the following format:

```yaml
project:
  name: "My Project"
  interval: 200000 # optional (defaults to 200000)
  chromosome: X    # optional (defaults to 'X')
  count_threshold:  2.0  # optional (defaults to 2.0)

datasets:
  - name: "Data 01"
    hic:  "path/to/data_01.hic"
  - name: "Data 02"
    hic:  "path/to/data_02.hic"
```

*See the [File Specification Document](doc/project.md) for full details on what can be included in the input data*

2. Checkout submodules

```sh
git submodule update --init
```

3. Build the Docker image.

```sh
docker build -t 4dgb/4dgbworkflow-tool:latest .
```

4. Run the browser!

```sh
./4DGBWorkflow run /path/to/project/directory/
```

**Example output:**
```
$ ./4DGBWorkflow run ./example_project
[>]: Building project... (this may take a while)

        #
        # Ready!
        # Open your web browser and visit:
        # http://localhost:8000/compare.html?gtkproject=example_project
        #
        # Press [Ctrl-C] to exit
        #
```

If this is the first time running a project, this may take a while, since it needs to run a molecular dynamics simulation with LAMMPS on your input data. The next time you run it, it won't need to run the simulation again. If you update the input files, then the simulation will automatically be re-run!

**Example Screenshot**

![](doc/example_screen.png)

## Help for Maintainers

See the [Publising](./doc/publishing.md) doc for information on publishing and releasing new versions.
