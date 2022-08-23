:q# Publishing a new version

Follow these steps when you're ready to publish and release a new version of the workflow.

1. Update the verison number in [version.txt](../version.txt).

2. Update the workflow version in ``example_project/project.yaml`` 
```sh
workflow:
    version: <new version number>
```
3. Rebuild the Docker images
```sh
make docker
```

4. Test with the `4DGBWorkflow version` command. You should see your new version number reported.
```sh
Workflow Container: 4dgb/4dgbworkflow-build:latest
       Version: v1.1.0
Browser Container:  4dgb/4dgbworkflow-view:latest
       Version: v1.5.1
```

5. Tag the new docker images with your new version number.
```sh
docker tag 4dgb/4dgbworkflow-build:latest 4dgb/4dgbworkflow-build:1.1.0
docker tag 4dgb/4dgbworkflow-view:latest 4dgb/4dgbworkflow-view:1.1.0
```

6. Push both tags to DockerHub (You'll need to be logged into an account with permissions to do so)
```sh
docker push 4dgb/4dgbworkflow-build:latest
docker push 4dgb/4dgbworkflow-build:1.1.0

docker push 4dgb/4dgbworkflow-view:latest
docker push 4dgb/4dgbworkflow-view:1.1.0
```

7. Push an updated python module to pypi. Do this by running make on the `module` target. `make` will
create a clean version of the `4dgb-workflow` module, and attempt to upload it to `pypi` with `twine`.
If `twine` is not installed, or if you do not have permission to upload the module to `pypi`, this 
will fail.

```
    make module
```

8. Update documentation at ``4dgb.readthedocs.io`` but updating the associated repository at 
``github.com/4dgb/4dgb-docs``


## If you changed the Example Project

If your changes affected the example project in the [example_project](../example_project/) directory, then you'll need to update the version embedded in the [4DGBWorkflow](../4DGBWorkflow) script.

1. Run the [generate_blob.py](../scripts/generate_blob.py) script, and copy its standard output to your clipboard.
```sh
python3 scripts/generate_blob.py
```

2. Find the string named `TEMPLATE_BLOB` in the [4DGBWorkflow](../4DGBWorkflow) script and replace it with the new blob from your clipboard.

3. You may want to re-create the template directory to make sure it works.
```
./4DGBWorkflow version --output test
```
