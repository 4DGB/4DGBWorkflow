# Instructions for cvs2arrays script

The script takes as input a ```workflow.yaml``` file that defines the ```cas``` data and a ```--destination``` directory, where it will write results. 

The script can be called from anywhere. It assumes that the path to the ```worflow.yaml``` is a top level 'workplace' directory, and that paths defined in the ```workflow.yaml``` file are relative to that directory. The path defined by the```--destination``` command line argument assumed to be absolute or relative to the directory that the script is run from.

## Arguments; calling the script

```
csv2arrays --workflow workplace/directory/workflow.yaml --destination some/results/directory
```

The ```workflow.yaml``` file must contain the following clause, defining how the track data is to be converted into array files:

```
tracks:
    - file: input_01.csv
      tracks: 
        - name: trackname_01
          columns: [first, second, third]
        - name: trackname_02
          columns: [second, third, fourth]
    - file: input_02.csv
      tracks: 
        - name: trackname_03
          columns: [fifth, sixth, seventh]
        - name: trackname_04
          columns: [sixth, seventh, eighth]
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
	trackname_03/
    	    track.json
            track.npz
	trackname_04/
    	    track.json
            track.npz
```
