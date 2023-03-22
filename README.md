# Gridsearch Helper
This repository contains some helper scripts to launch your parallelized gridsearch with the SLURM scheduling system. In the past there was also support for Sun Grid Engine, now called Univa grid engine. It shouldn't be hard to re-add support for that if there is interest.
Additionally it also provides a python package to collect and visualize the results of the gridsearch.


## What problems does `gridsearch_helper` solve?
A common problem is that you want to run a grid search over hyperparameters. For simple grid searches, this is not very complicated, but for more complex setups (e.g. including nested hyperparameter dicts), this becomes cumbersome. `gridsearch_helper` helps with that. Additionally, sometimes you want to run several gridsearches simultaneously and change the code in between. A problem occurs if you start a gridsearch and some jobs are put into the waiting queue. Then you change the code for another gridsearch that you want to run. The jobs from your old gridsearch will eventually get activated, but they will now run the new code, which you are in the middle of changing! `gridsearch_helper` helps with that, too. Every time you start a new job, a copy of the current version of your repository is made. The gridsearch is then executed within this copy. What's especially great about this is that this happens without you even noticing or having to care about it.

## Requirements in your code
In order for this to work, unfortunately some assumptions have to be made about your code. I hope that making modifications to your code such that it fulfills these requirements is not too hard.
- Your project must be version controlled with git
- Your code must be able to read its hyperparameters from a `YAML` file, and your code must accept a command line parameter like `--parameters_file=...` which tells it from where to read the `YAML` file.
- if you use data or other external files in your code, either these data need to be part of your git repository, or your code must use absolute paths to these data
- Your code must be set up such that it takes a command line parameter like `--output_path=...` and writes all its output in (subfolders of) this path

## Usage - running gridsearch jobs
Place this repository anywhere on your system.

You need to have a `YAML` file in which you have two sections, one being `'default'`, containing the default parameters, and the other `'gridsearch'`, which is again split into one or more config sections (see below). Parameters to be gridsearched are given with their values in YAML-lists.
```YAML
default:
  x_y_step: 0.1
  zstep: -0.035
  nn_architecture: ['dense50', 'softplus', 'dense100', 'softplus']
  gamma: 0.9
  target_update_rate: 1000
  lr: 0.0003
  initial_temperature: 3.001
  learning_rule: double_q_learning
gridsearch:
  learning_rule:
  - double_q_learning
  - PPO
  target_update_rate:
  - 500
  - 1000
  - 10000
```
Then, from the working directory in which you want your program to be run, call the `slurmlaunch` script like this

```bash
path/to/gridsearch_helper/SLURM/slurmlaunch --taskrange-begin=1 --taskrange-end=5 --time=00:10:00 --partition=cpu-shot --params-path=./parameters.yaml --path=outfiles/test
```
The results will be put in ``./outfiles/test``, which is a path relative to your current working directory. Specifically, each instance of ```main(params)``` will get a params dictionary as argument.

## Usage - analyzing results (currently still in development)
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
