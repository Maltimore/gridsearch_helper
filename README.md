# Gridsearch Helper
This repository contains some helper scripts to launch your parallelized gridsearch with the SLURM scheduling system. In the past there was also support for Sun Grid Engine, now called Univa grid engine. It shouldn't be hard to re-add support for that if there is interest.
Additionally it also provides a python package to collect and visualize the results of the gridsearch.


## What problems does `gridsearch-helper` solve?
A common occurrence is that you want to run a grid search over hyperparameters. For simple grid searches, this is not very complicated, but for more complex setups (e.g. including nested hyperparameter dicts), this becomes cumbersome. `gridsearch-helper` helps with that. Additionally, sometimes you want to run several gridsearches simultaneously and change the code in between. A problem occurs if you start a gridsearch and some jobs are put into the waiting queue. Then you change the code for another gridsearch that you want to run. The jobs from your old gridsearch will eventually get activated, but they will now run the new code, which you are in the middle of changing! `gridsearch_helper` helps with that, too. Every time you start a new job, a copy of the current version of your repository is made. The gridsearch is then executed within this copy. What's especially great about this is that this happens without you even noticing or having to care about it.

## Requirements in your code
In order for this to work, unfortunately some assumptions have to be made about your code. I hope that making modifications to your code such that it fulfills these requirements is not too hard.
- Your project must be version controlled with git
- Your code must be able to read its hyperparameters from a `YAML` file, and your code must accept a command line parameter like `--parameters_file=...` which tells it from where to read the `YAML` file.
- if you use data or other external files in your code, either these data need to be part of your repository, or your code must use absolute paths to these data
- Your code must be set up such that it takes a command line parameter like `--output_path=...` and writes all its output in (subfolders of) this path

## Usage - running gridsearch jobs
Place this repository anywhere on your system. This program assumes that you have an entry point into your project that is a module called main.py, containing the function main(params), where params is a parameter dictionary.

```python
# filename: main.py

def main(params):
	# ...
```

It also assumes that in the same directory as your main.py you have a file called parameters.yaml in which you have two sections, one being 'default', containing the default parameters, and the other 'gridsearch', in which parameters to be gridsearched are given with their values in YAML-lists. See the example YAML file in this repository.

Then, from the working directory in which you want your program to be run, call the gridsearch_entry.sh script, which is called like

```bash
/path/to/gridsearch_entry.sh /path/to/main.py start_idx end_idx run_name
```

Where ``/path/to/main.py`` is the (relative or absolute) path to the main.py file, ``start_idx`` is the beginning index of the task range, ``end_idx`` is the end index of the task range, and ``run_name`` is the name for the entire run. To call a gridsearch with indices 1, 2, 3, 4, 5, 6 and name mygridsearch, and assuming that the (relative) path to your main.py is myproject/main.py, call

```
/path/to/gridsearch_entry.sh myproject/main.py 1 6 mygridsearch_name
```

The results will be put in ``./outfiles/mygridsearch_name``, which is a path relative to your current working directory (your current working directory is also the working directory of the program you start with ```gridsearch_entry.sh```). Specifically, each instance of ```main(params)``` will get a params dictionary as argument. In params, you will find the keys 'gridsearch', set to ```True```, and 'output_path' and 'gridsearch_results_path'. 'output_path' is where you should save all relevant data generated by your program. Into 'gridsearch_results_path' you should only save a file 'program_state.yaml' in which you save the final score of the current run.

Hint: if you add the folder SGE from this repository to your PATH, you can easily call the gridsearch from anywhere on your system. Say that you have gridsearch_helper in your home directory, then you would do (for instance in your .bashrc):

```bash
export PATH=$PATH:"$HOME"/gridsearch_helper/SGE
```

and from then on you can call your gridsearch simply with ``gridsearch_entry.sh myrepo/src/main.py 1 20 mygridsearch_name``.

## Usage - analyzing results
This repository also contains a package ``gridsearch_analysis``. ``gridsearch_analysis`` can be installed by simply running ``pip install .`` from the root of this repository.
``gridsearch_analysis`` assumes that the above instructions were followed, in other words that there is a folder ``outfiles/mygridsearch_name/results`` and in this folder there is one subfolder for each job that ran, and in each subfolder there are two files: ``parameters.yaml`` and ``program_state.yaml``. You can use the function ``collect_results``, which loops over all subfolders and collects all values in ``parameters.yaml`` and ``program_state.yaml`` into a pandas dataframe.

If some of your runs didn't finish yet but you can't wait and already wnat to perform the analysis, and you also want to include the missing runs in the analysis, you have the option of setting some default values for unfinished runs (see code below):

```python
from gridsearch_analysis import collect_results

df = collect_results.collect_results(results_path)
```

Furthermore, ``gridsearch_analysis`` can also make plots of the collected results. It will plot the performance as measured by some variable ``target_column`` as a function of user-specified indpendent variables ``relevant_parameters``. The type of plot created depends on how many independent variables you specify. If you have:
- 0  independent variables: create a swarm/barplot with a single group that contains all runs
- 1  independent variable: create a swarm/barplot with one group for each value of the independent variable
- 2+ independent variables: create a parallel coordinates plot

There is also an option to split the analysis into separate parts via the values of another independent variable. In this case, one plot per value of this ``split_analysis_column`` is performed. This effectively reduces the amount of independent variables by 1.

```python
from gridsearch_analysis import plotting

# Specify the relevant parameters by which the results are differentiated
RELEVANT_PARAMETERS = ['name']  # list of strings (list can be empty)
# what variable to use as performance measure
TARGET_COLUMN = 'first_success'  # string
# is the performance better when the target variable is lower or when it is higher?
# this only makes a difference if you have 2+ relevant parameters and hence when a
# parallel coordinates plot is created
LOWER_IS_BETTER = True  # bool
# split up the analysis into separate parts for unique values in this column
SPLIT_ANALYSIS_COLUMN = None  # string or None

plotting.plot(df, plot_path, RELEVANT_PARAMETERS, TARGET_COLUMN, LOWER_IS_BETTER, SPLIT_ANALYSIS_COLUMN, VAR_ORDER)
```
