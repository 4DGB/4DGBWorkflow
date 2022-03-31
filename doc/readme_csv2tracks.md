# Instructions for cvs2arrays script

The script takes as input a ```workflow.yaml``` file that defines the ```cas``` data and a ```--destination``` directory, where it will write results. 

The script can be called from anywhere. It assumes that the path to the ```worflow.yaml``` is a top level 'workplace' directory, and that paths defined in the ```workflow.yaml``` file are relative to that directory. The path defined by the```--destination``` command line argument assumed to be relative to the 'workplace' directory 

## Arguments; calling the script

```
csv2arrays --workflow workplace/directory/workflow.yaml --destination some/results/directory
```

The ```workflow.yaml``` file must contain the following clause, defining how the track data is to be converted into array files. Note that the tracks must have a ```file``` field, but that can be overridden on a column-by-column basis if the information for that column is to be pulled from a different file. This is achieved by providin a column with its own ```file``` field (see the third track example). This allows data from different files to be integrated into a single track. 

```
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
```

This will result in the following files, with the ```.json``` file defining the metatdata for an array required by the browser, and the ```.npz``` file containing the compressed arrays required by the browser.

```
some/results/directory/
	trackname_01/
    	    track.json
            track.npz
	trackname_02/
    	    track.json
            track.npz
```

The script also outputs a ```array_results.json``` file that includes a clause that defines the data that a 4DGenomeBrowser ```project.json``` file needs to define the arrays.
