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


## Git submodules
In order to **add** a git submodule to a repository:

``` git submodule add git@github.com:Maltimore/gridsearch_helper.git path/where/submodule/should/be ```

If you clone a repository that contains submodules, use this command to **initialize** all of them

``` git submodule update --init --recursive ```

In order to **update** submodules to the tips of the remote branches:

```	git submodule update --recursive --remote ```
