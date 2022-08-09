# Publishing a new version

Follow these steps when you're ready to publish and release a new version of the workflow.

1. Update the verison number in [version.txt](../version.txt).

2. Rebuild the Docker image
```sh
docker build -t 4dgb/4dgbworkflow-tool:latest .
```

3. Test with the `4DGBWorkflow version` command. You should see your new version number reported.
```sh
./4DGBWorkflow version
> Docker container tag: latest
> Workflow version: v1.1.0
> Browser version: v1.4.0
```

4. Tag the new docker image with your new version number.
```sh
docker tag 4dgb/4dgbworkflow-tool:latest 4dgb/4dgbworkflow-tool:1.1.0
```

5. Push both tags to DockerHub (You'll need to be logged into an account with permissions to do so)
```sh
docker push 4dgb/4dgbworkflow-tool:latest
docker push 4dgb/4dgbworkflow-tool:1.1.0
```

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
