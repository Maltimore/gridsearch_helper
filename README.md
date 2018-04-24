# Gridsearch Helper

This repository contains some helper scripts to launch your parallelized gridsearch with a scheduling system like sun grid engine (in fact at the moment only sun grid engine is supported).

## Usage

Place this repository as a submodule in the same folder in which you have your python entrypoint. This repository assumes that your entry point is a module called main.py, containing the function


```python
# filename: main.py


def main(params, output_files_path, results_yaml_path, gridsearch):
	# ...
```

and a file called parameters.yaml in which you have two sections, one being 'default', containing the default parameters, and the other 'gridsearch', in which parameters to be gridsearched are given with their values in yaml-lists. See the example .yaml file.

Then, from the directory in which you want your program to be run, call the entry.sh script, which is called like

```
./path/to/entry.sh start_idx end_idx name
```

Where ``start_idx`` is the beginning index of the task ranage, ``end_idx`` is the end index of the task range, and ``name`` is the name for the entire gridsearch. To call a gridsearch with indices 1, 2, 3, 4, 5, 6 and name mygridsearch, call

```
./path/to/entry.sh 1 6 mygridsearch
```

The results will be put in ``./outfiles/mygridsearch``.


## Git submodules
In order to **add** this repository as a git submodule to a repository:

``` git submodule add git@github.com:Maltimore/gridsearch_helper.git path/where/submodule/should/be ```

If you clone a repository that already contains submodules, use this command to **initialize** all of them:

``` git submodule update --init --recursive ```

In order to **update** submodules to the tips of the remote branches:

```	git submodule update --recursive --remote ```
